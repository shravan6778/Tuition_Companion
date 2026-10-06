"""Load an official textbook (NCERT, SCERT...) into the Reference Corpus from a PDF.

    python -m app.db.ingest_reference book.pdf --board CBSE --class "Class 9" --subject Science \
        --publisher NCERT [--edition "2025"] [--chapters "Matter:1-12,Atoms:13-30"] [--append] [--number 5]

Without --chapters the PDF's top-level bookmarks define the chapters. NCERT publishes one PDF per chapter:
ingest the first with --append (or without it), then every further chapter of the SAME book with --append,
and --number N to give a chapter its textbook number (default: the next free number). Without --append an
existing reference book is never touched. Runs the same OCR -> fingerprint ->
concept -> graph pipeline as a teacher upload (use OCR_PROVIDER / LLM_PROVIDER in .env), one chapter at a time,
each in its own transaction, so a failure only affects that chapter. Reference books are public and read-only
through the API; this script is the only way to create them."""
import argparse
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content_library.upload import open_pdf, outline_chapters, split_pdf, validate_ranges
from app.core.storage import save_by_hash, sha256_hex
from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.jobs import mark_processing, run_chapter_job
from app.schemas import ChapterRange


def parse_ranges(text: str) -> list[ChapterRange]:
    ranges = []
    for part in text.split(","):
        title, _, pages = part.rpartition(":")
        start, _, end = pages.partition("-")
        ranges.append(ChapterRange(title=title.strip(), start_page=int(start), end_page=int(end or start)))
    return ranges


def ingest(db_factory, pdf_bytes: bytes, *, board: str, class_name: str, subject: str, publisher: str,
           edition: str | None = None, ranges: list[ChapterRange] | None = None,
           append: bool = False, first_number: int | None = None, allow_fake: bool = False) -> tuple[str, list[str]]:
    """Returns (book_id, per-chapter result lines). Refuses to create a duplicate reference book unless
    append=True, which adds the chapters to the existing one (refusing duplicate titles/numbers)."""
    refuse_fake_llm(allow_fake)
    reader = open_pdf(pdf_bytes)
    chapters = validate_ranges(ranges or outline_chapters(reader), len(reader.pages))

    with db_factory() as db:
        dup = db.scalar(select(Book).where(
            Book.is_reference.is_(True), Book.board == board, Book.class_name == class_name,
            Book.subject == subject, Book.publisher == publisher, Book.edition == edition,
        ))
        if dup is not None and not append:
            raise SystemExit(
                f"This reference book already exists (id {dup.id}). Use --append to add chapters to it, "
                "or delete it first to re-ingest."
            )
        existing = list(db.scalars(select(Chapter).where(Chapter.book_id == dup.id))) if dup else []
        first = first_number or (max((c.sequence_num or 0 for c in existing), default=0) + 1)
        titles = {c.title.casefold() for c in existing}
        numbers = {c.sequence_num for c in existing}
        for offset, r in enumerate(chapters):
            if r.title.casefold() in titles:
                raise SystemExit(f"This book already has a chapter called '{r.title}'. Nothing was changed.")
            if first + offset in numbers:
                raise SystemExit(f"This book already has a chapter number {first + offset}. Use --number to pick another.")
        if dup is not None:
            book = dup
        else:
            book = Book(board=board, class_name=class_name, subject=subject, publisher=publisher,
                        edition=edition, is_reference=True, owner_teacher_id=None, metadata_source="manual")
            db.add(book)
            db.flush()
        chapter_ids = []
        for number, r in enumerate(chapters, start=first):
            part = split_pdf(reader, r.start_page, r.end_page)
            digest = sha256_hex(part)
            chapter = Chapter(book_id=book.id, title=r.title, sequence_num=number,
                              source_file=save_by_hash(part, digest, "pdf"), source_sha256=digest)
            mark_processing(chapter)
            db.add(chapter)
            db.flush()
            chapter_ids.append(chapter.id)
        db.commit()
        book_id = str(book.id)

    results = []
    for chapter_id in chapter_ids:
        run_chapter_job(chapter_id, None, db_factory)  # owns its session; failures are recorded on the chapter
        with db_factory() as db:
            ch = db.get(Chapter, chapter_id)
            ok = ch.status == ChapterStatus.READY
            results.append(f"{'ok    ' if ok else 'FAILED'} {ch.title}" + ("" if ok else f": {ch.error_message}"))
    return book_id, results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf")
    parser.add_argument("--board", required=True)
    parser.add_argument("--class", dest="class_name", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--publisher", required=True)
    parser.add_argument("--edition")
    parser.add_argument("--allow-fake", action="store_true", help="allow the placeholder LLM (tests only)")
    parser.add_argument("--append", action="store_true", help="add the chapter(s) to the existing reference book")
    parser.add_argument("--number", type=int, dest="first_number", help="textbook number of the first chapter")
    parser.add_argument("--chapters", help='"Title:first-last,Title2:first-last"; default: the PDF bookmarks')
    a = parser.parse_args()
    book_id, results = ingest(
        SessionLocal, Path(a.pdf).read_bytes(), board=a.board, class_name=a.class_name, subject=a.subject,
        publisher=a.publisher, edition=a.edition, ranges=parse_ranges(a.chapters) if a.chapters else None,
        append=a.append, first_number=a.first_number, allow_fake=a.allow_fake,
    )
    print(f"Reference book {book_id}")
    print("\n".join(results))
    if any(line.startswith("FAILED") for line in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
