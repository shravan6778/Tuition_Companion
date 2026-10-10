"""Remove one chapter of an OFFICIAL book (for example a leftover test chapter).

    python -m app.db.drop_chapter --book <book-id> --number 3          # dry run: shows what would go
    python -m app.db.drop_chapter --book <book-id> --number 3 --yes    # really delete it

Deletes the chapter with its pages, concepts, edges and embeddings (database cascade) and its copy in the graph store.
Official books only; teachers' chapters are never touched here. Afterwards run
`python -m app.db.crosslink --book <book-id> --force` so cross-chapter links stop pointing at the removed chapter."""
import argparse
import uuid

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.graph_store import get_graph_store
from app.models import Book, Chapter, Concept, Page


def run(db_factory, book_id: uuid.UUID, number: int, confirm: bool) -> list[str]:
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            return ["Book not found."]
        if not book.is_reference:
            return ["Refused: this is not an official book. This tool only removes chapters of official books."]
        chapter = db.scalar(select(Chapter).where(Chapter.book_id == book.id, Chapter.sequence_num == number))
        if chapter is None:
            return [f"No chapter number {number} in this book."]
        pages = db.scalar(select(func.count()).select_from(Page).where(Page.chapter_id == chapter.id))
        concepts = db.scalar(select(func.count()).select_from(Concept).join(Page, Page.id == Concept.page_id).where(Page.chapter_id == chapter.id))
        line = f"chapter {chapter.sequence_num} '{chapter.title}' [{chapter.status}]: {pages} pages, {concepts} concepts"
        if not confirm:
            return [f"would delete {line}", "dry run, nothing deleted (add --yes)"]
        store = get_graph_store()
        if store is not None:
            store.delete_chapter(str(chapter.id))
        db.delete(chapter)
        db.commit()
        return [f"deleted {line}", f"now run: python -m app.db.crosslink --book {book_id} --force"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", required=True)
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--yes", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book), a.number, a.yes)))
