"""See which concepts each exercise page would be mapped to, on your real chapters (read-only, no model calls).

    python -m app.db.exercise_map                       # every ready chapter that has exercise pages
    python -m app.db.exercise_map --book <id>           # one book
    python -m app.db.exercise_map --book <id> --chapter 9 --pages 7,8   # the pages of one exercise (e.g. Ex.9.5)
    python -m app.db.exercise_map --min-similarity 0.4  # try another cut-off without touching the settings
    python -m app.db.exercise_map --show-text           # also print each exercise page's first lines and the chapter's page-kind counts,
                                                        # to judge whether the pages labelled `exercise` really are exercises

For each exercise page it prints the closest concepts WITH their similarity, kept or not, and then the list that would
be proposed to the teacher. Judge two things: are the kept concepts really what the exercise practises, and does the
cut-off (EXERCISE_MAP_MIN_SIMILARITY) sit between the right and the wrong ones? Needs `python -m app.db.sync_graph`
to have created the embeddings and `python -m app.db.backfill_page_kind --yes` to have labelled old pages."""
import argparse
import uuid
from collections import Counter

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.assignments.scope import propose_exercise_concepts
from app.models import Book, Chapter, ChapterStatus, Page


def run(db_factory, book_id=None, chapter_number=None, pages=None, min_similarity=None, show_text: bool = False) -> list[str]:
    floor = settings.exercise_map_min_similarity if min_similarity is None else min_similarity
    out = [f"top {settings.exercise_map_top_k} per page, kept when similarity >= {floor}, at most {settings.exercise_map_max_concepts} concepts"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        if chapter_number is not None:
            query = query.where(Chapter.sequence_num == chapter_number)
        for chapter in db.scalars(query):
            mapping = propose_exercise_concepts(db, chapter, pages, min_similarity=floor)
            if mapping.status == "no_exercise_pages":
                continue
            book = db.get(Book, chapter.book_id)
            out.append(f"\n{book.publisher or ''} {book.class_name or ''} {book.subject or ''} / {chapter.title}  [{mapping.status}]")
            if show_text:
                every = list(db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)))
                kinds = Counter(p.page_kind for p in every)
                out.append("  page kinds: " + ", ".join(f"{n} {k}" for k, n in sorted(kinds.items())) + "  | exercise pages: "
                           + ", ".join(str(p.page_number) for p in every if p.page_kind == "exercise"))
                by_number = {p.page_number: p for p in every}
                for number in mapping.exercise_pages:
                    page = by_number.get(number)
                    if page is not None:
                        out.append(f"  text of page {number} [{page.page_kind}]: {' '.join(page.content_text.split())[:240]}")
            if mapping.status != "ok":
                out.append("    no vectors: run python -m app.db.sync_graph first")
                continue
            for number in mapping.exercise_pages:
                rows = mapping.per_page.get(number)
                if rows is None:
                    out.append(f"  page {number}: too short to embed")
                    continue
                out.append(f"  page {number}: " + "; ".join(f"{'*' if s >= floor else ' '}{n} {s}" for n, s in rows))
            out.append("  PROPOSED: " + (", ".join(f"{c.name} ({c.similarity:.2f}, p{','.join(map(str, c.pages))})" for c in mapping.proposed) or "nothing above the cut-off"))
    out.append("\n* = kept. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--pages", help="comma-separated page numbers of one exercise")
    parser.add_argument("--min-similarity", type=float)
    parser.add_argument("--show-text", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book) if a.book else None, a.chapter,
                        [int(x) for x in a.pages.split(",")] if a.pages else None, a.min_similarity, a.show_text)))
