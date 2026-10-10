"""Layer 4 from the command line: compare chapters' stored page vectors with the books a teacher can see.

    python -m app.db.embedmatch                  # every book, DRY RUN: prints what it would suggest and the closest books
    python -m app.db.embedmatch --book <id>      # one book
    python -m app.db.embedmatch --save           # also store the suggestions in each chapter's match report

Needs the chapters' embeddings (run `python -m app.db.sync_graph` first if `show_graph` says they are not done).
No embedding or LLM calls. Use the dry run to judge EMBED_MATCH_SIMILARITY on real data before relying on it."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Chapter, ChapterStatus
from app.pipeline.embedmatch import compute, embedmatch_chapter


def run(db_factory, book_id=None, save: bool = False) -> list[str]:
    out = [f"similarity >= {settings.embed_match_similarity} per page, coverage >= {settings.variant_min_coverage} of the chapter's pages"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for chapter in db.scalars(query):
            found, info = compute(db, chapter)
            out.append(f"{chapter.title}: {info.get('status')} ({info.get('pages_compared', 0)} pages)")
            for near in info.get("closest", []):
                out.append(f"    closest: {near['book']} / {near['chapter']}: {near['matched_pages']}/{near['pages_checked']} pages, avg {near['avg_similarity']}")
            for s in found:
                out.append(f"    SUGGEST: {s['chapter_title']} ({s['matched_pages']}/{s['pages_checked']} pages, avg {s['avg_similarity']})")
            if save:
                embedmatch_chapter(db, chapter)
                db.commit()
        if not save:
            db.rollback()
    out.append("saved" if save else "dry run, nothing saved (use --save)")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--save", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book) if a.book else None, a.save)))
