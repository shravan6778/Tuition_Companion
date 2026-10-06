"""Re-run processing for a book's chapters from their stored files (no re-upload).

    python -m app.db.reprocess <book-id>              # every chapter
    python -m app.db.reprocess <book-id> --chapter 2  # one chapter number

Use it after fixing .env (e.g. switching from the fake LLM to a real one): each chapter's pages and concepts
are replaced. Concepts made by the fake model are never reused by a real run."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job


def reprocess(db_factory, book_id: uuid.UUID, chapter_number: int | None = None, allow_fake: bool = False) -> list[str]:
    refuse_fake_llm(allow_fake)
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            raise SystemExit("Book not found.")
        query = select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)
        if chapter_number is not None:
            query = query.where(Chapter.sequence_num == chapter_number)
        targets, results = [], []
        for chapter in db.scalars(query).all():
            if not chapter.source_file:
                results.append(f"skipped {chapter.title}: no stored file")
            elif is_actively_processing(chapter):
                results.append(f"skipped {chapter.title}: still processing")
            else:
                mark_processing(chapter)
                targets.append(chapter.id)
        db.commit()
        owner = book.owner_teacher_id
    for chapter_id in targets:
        run_chapter_job(chapter_id, owner, db_factory)
        with db_factory() as db:
            ch = db.get(Chapter, chapter_id)
            ok = ch.status == ChapterStatus.READY
            results.append(f"{'ok    ' if ok else 'FAILED'} {ch.title}" + ("" if ok else f": {ch.error_message}"))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("book_id")
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--allow-fake", action="store_true")
    args = parser.parse_args()
    print("\n".join(reprocess(SessionLocal, uuid.UUID(args.book_id), args.chapter, args.allow_fake)))
