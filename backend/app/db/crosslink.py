"""Link chapters to the earlier chapters of their book (cross-chapter prerequisites), for chapters that were
processed before this existed, or after a change of model.

    python -m app.db.crosslink                 # every book
    python -m app.db.crosslink --book <id>     # one book
    python -m app.db.crosslink --force         # ask the model again even if nothing changed
    python -m app.db.crosslink --book <id> --explain   # dry run: show every candidate, its similarity and what the model chose

Needs the chapters' embeddings (run `python -m app.db.sync_graph` first if `show_graph` says embeddings are not
done). Chapters are linked in book order. Nothing here changes pages, concepts or any chapter's own graph."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.crosslink import crosslink_chapter, explain_chapter
from app.pipeline.indexing import sync_cross_edges


def crosslink_books(db_factory, book_id=None, force: bool = False, allow_fake: bool = False) -> list[str]:
    refuse_fake_llm(allow_fake)
    from app.llm import get_llm_provider
    provider = get_llm_provider()
    out: list[str] = []
    with db_factory() as db:
        query = select(Book.id)
        if book_id is not None:
            query = query.where(Book.id == book_id)
        book_ids = list(db.scalars(query))
    for bid in book_ids:
        with db_factory() as db:
            chapters = list(db.scalars(
                select(Chapter).where(Chapter.book_id == bid, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)
            ))
            for chapter in chapters:
                if force:
                    report = dict(chapter.graph_report or {})
                    report.pop("cross_chapter", None)
                    chapter.graph_report = report
                try:
                    rep = crosslink_chapter(db, chapter, provider)
                    db.commit()
                    out.append(f"{rep.get('status'):14} {chapter.title}: {rep.get('edges', 0)} cross-chapter edges")
                except Exception as exc:
                    db.rollback()
                    out.append(f"FAILED         {chapter.title}: {type(exc).__name__}")
            if chapters:
                out.append(f"  graph store {'updated' if sync_cross_edges(db, bid) else 'not updated (off or unreachable)'}")
    return out


def explain_books(db_factory, book_id=None, allow_fake: bool = False) -> list[str]:
    """Writes nothing (the model is still asked, so it costs a few LLM calls)."""
    refuse_fake_llm(allow_fake)
    from app.llm import get_llm_provider
    provider = get_llm_provider()
    out: list[str] = []
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for chapter in db.scalars(query):
            out += explain_chapter(db, chapter, provider)
        db.rollback()
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--explain", action="store_true", help="dry run, writes nothing")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    if a.explain:
        print("\n".join(explain_books(SessionLocal, uuid.UUID(a.book) if a.book else None, a.allow_fake)))
        raise SystemExit(0)
    print("\n".join(crosslink_books(SessionLocal, uuid.UUID(a.book) if a.book else None, a.force, a.allow_fake)))
