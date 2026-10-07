"""Print a book's concept graph as text, to judge (and tune) extraction quality on real chapters.

    python -m app.db.show_graph <book-id>              # every chapter
    python -m app.db.show_graph <book-id> --chapter 3  # one chapter number

For each chapter: the pipeline's report (merged names, edges, dropped loops, unresolved prerequisites,
pages flagged for review), then each concept with what it needs. Paste the output when asking for tuning."""
import argparse
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content_library.graph_view import chapter_graph
from app.db.session import SessionLocal
from app.models import Book, Chapter


def render_book(db: Session, book_id: uuid.UUID, chapter_number: int | None = None) -> str:
    book = db.get(Book, book_id)
    if book is None:
        return "Book not found."
    query = select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)
    if chapter_number is not None:
        query = query.where(Chapter.sequence_num == chapter_number)
    out = [f"{book.board} {book.class_name} {book.subject} ({book.publisher}"
           f"{', ' + book.edition if book.edition else ''})" + ("  [official]" if book.is_reference else "")]
    for chapter in db.scalars(query).all():
        graph = chapter_graph(db, chapter)
        r = graph.report or {}
        out += ["", f"== Chapter {chapter.sequence_num}: {chapter.title}  [{chapter.status}]"]
        if chapter.error_message:
            out.append(f"   error: {chapter.error_message}")
        if r.get("model") == "fake":
            out.append("   !! PLACEHOLDER concepts: made by the fake LLM (LLM_PROVIDER=fake). Not real extraction.")
        out.append(f"   search copy: embeddings={chapter.embedding_status}  graph store={chapter.graph_sync_status}"
                   + (f"  ({chapter.index_error})" if chapter.index_error else ""))
        out.append(
            f"   model={r.get('model', 'unknown (made before models were recorded)')}\n"
            f"   concepts={r.get('concepts', 0)}  edges={r.get('edges', 0)}  merged_duplicates={r.get('duplicate_names_merged', 0)}"
            f"  dropped_loops={len(r.get('dropped_cycle_edges', []))}  unresolved={len(r.get('unresolved_prerequisites', []))}"
            f"  llm_linking={r.get('llm_linking', '-')}  review_pages={[p['page'] for p in r.get('review_pages', [])]}"
        )
        names = {n.id: n.name for n in graph.nodes}
        needs: dict = {}
        for e in graph.edges:
            needs.setdefault(e.concept_id, []).append(f"{names[e.prerequisite_id]} ({e.source})")
        for node in graph.nodes:
            line = f"   - {node.name}  [p. {', '.join(map(str, node.pages))}]"
            if node.id in needs:
                line += "\n       needs: " + "; ".join(needs[node.id])
            out.append(line)
        for item in r.get("unresolved_prerequisites", []):
            out.append(f"   ? '{item['concept']}' mentions '{item['prerequisite']}' (no such concept in this chapter)")
        for item in r.get("dropped_cycle_edges", []):
            out.append(f"   x dropped loop: '{item['prerequisite']}' before '{item['concept']}'")
    return "\n".join(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id")
    parser.add_argument("--chapter", type=int)
    args = parser.parse_args()
    with SessionLocal() as session:
        print(render_book(session, uuid.UUID(args.book_id), args.chapter))
