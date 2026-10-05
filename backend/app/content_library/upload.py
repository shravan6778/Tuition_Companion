"""Front-pages-first upload orchestration (Rules.md §3 / md 'Step 2').

1. Front pages (cover + publisher/edition page): OCR + one small LLM call -> proposed metadata + known
   books that already match it. Nothing is created until the teacher confirms (POST /teacher/books with draft_id).
2. Then the content itself: chapter-by-chapter (teacher/routes.py) or the whole textbook at once, which is
   split into chapters from the PDF's bookmarks or the teacher's page ranges and processed per chapter."""
import io
import logging
import uuid
from dataclasses import dataclass
from typing import Optional

import pypdf
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.core.storage import detect_extension, save_by_hash, sha256_hex
from app.llm import get_llm_provider
from app.models import Book, Chapter, UploadDraft, User
from app.ocr import get_ocr_provider
from app.pipeline.front_matter import extract_book_metadata
from app.schemas import ChapterRange
from app.content_library.search import match_metadata

logger = logging.getLogger(__name__)


@dataclass
class ValidatedUpload:
    data: bytes
    ext: str
    sha256: str


def read_validated_upload(file: UploadFile, max_mb: int, pdf_only: bool = False) -> ValidatedUpload:
    """Size limit, non-empty, and file TYPE BY CONTENT (never the filename or the client's MIME type)."""
    max_bytes = max_mb * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty")
    if len(data) > max_bytes:
        raise HTTPException(413, f"File is too large (max {max_mb} MB)")
    ext = detect_extension(data)
    if ext is None or (pdf_only and ext != "pdf"):
        raise HTTPException(
            415,
            "Please upload a PDF file" if pdf_only else "Please upload a PDF, PNG or JPG file",
        )
    return ValidatedUpload(data, ext, sha256_hex(data))


# ---- PDF helpers ------------------------------------------------------------------------------

def open_pdf(data: bytes) -> pypdf.PdfReader:
    try:
        reader = pypdf.PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("encrypted")
        len(reader.pages)  # force a parse
        return reader
    except Exception:
        raise HTTPException(
            422,
            "This PDF can't be read (it may be damaged or password-protected)",
        )


def outline_chapters(reader: pypdf.PdfReader) -> list[ChapterRange]:
    """Chapters proposed from the PDF's top-level bookmarks, if it has any. Teachers review/edit them."""
    total = len(reader.pages)
    starts: list[tuple[int, str]] = []
    try:
        for item in reader.outline:
            if isinstance(item, list):  # nested = sub-sections; only top level counts as chapters
                continue
            page = reader.get_destination_page_number(item)
            title = " ".join(str(item.title).split())
            if title and 0 <= page < total:
                starts.append((page + 1, title))
    except Exception:
        logger.warning("Couldn't read PDF bookmarks", exc_info=True)
        return []
    starts.sort()
    proposed, seen_pages = [], set()
    for i, (start, title) in enumerate(starts):
        if start in seen_pages:
            continue
        seen_pages.add(start)
        end = (starts[i + 1][0] - 1) if i + 1 < len(starts) else total
        if end >= start:
            proposed.append(ChapterRange(title=title[:200], start_page=start, end_page=end))
    return proposed


def split_pdf(reader: pypdf.PdfReader, start_page: int, end_page: int) -> bytes:
    writer = pypdf.PdfWriter()
    for index in range(start_page - 1, end_page):
        writer.add_page(reader.pages[index])
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def validate_ranges(ranges: list[ChapterRange], page_count: int) -> list[ChapterRange]:
    if not ranges:
        raise HTTPException(422, "Add at least one chapter")
    if len(ranges) > settings.max_whole_book_chapters:
        raise HTTPException(
            422, f"At most {settings.max_whole_book_chapters} chapters per upload"
        )
    ordered = sorted(ranges, key=lambda r: r.start_page)
    previous_end = 0
    for r in ordered:
        if r.end_page < r.start_page:
            raise HTTPException(422, f"'{r.title}': the last page is before the first page")
        if r.end_page > page_count:
            raise HTTPException(
                422, f"'{r.title}': the PDF only has {page_count} pages"
            )
        if r.start_page <= previous_end:
            raise HTTPException(422, f"'{r.title}' overlaps the previous chapter")
        previous_end = r.end_page
    return ordered


# ---- step 1: front pages -> proposed metadata -------------------------------------------------------

def create_front_pages_draft(db: Session, teacher: User, upload: ValidatedUpload):
    """Returns (draft, metadata, matching_books). Costs one OCR call + one small LLM call."""
    if upload.ext == "pdf":
        pages = len(open_pdf(upload.data).pages)
        if pages > settings.front_pages_max_pages:
            raise HTTPException(
                422,
                f"Upload only the cover and publisher/edition pages (at most {settings.front_pages_max_pages} pages)",
            )
    try:
        layout = get_ocr_provider().extract_layout(upload.data, upload.ext)
    except Exception as exc:
        logger.exception("Front-page OCR failed")
        raise ProcessingError("Couldn't read these pages right now. Please try again, or enter the details by hand.") from exc
    text = "\n".join(p["text"] for p in layout["pages"]).strip()
    if len(text) < 10:
        raise HTTPException(
            422, "No readable text was found on these pages. Try a clearer scan."
        )
    metadata = extract_book_metadata(get_llm_provider(), text)  # ProcessingError -> 422 with a safe message

    draft = UploadDraft(
        teacher_id=teacher.id, kind="front_pages", source_file=save_by_hash(upload.data, upload.sha256, upload.ext),
        source_sha256=upload.sha256, page_count=layout["page_count"] if "page_count" in layout else len(layout["pages"]),
        payload={"metadata": metadata.model_dump()},
    )
    db.add(draft)
    db.commit()
    return draft, metadata, match_metadata(db, teacher, metadata)


# ---- step 2b: whole textbook -> chapters ---------------------------------------------------------------

def create_whole_book_plan(db: Session, teacher: User, book: Book, upload: ValidatedUpload):
    reader = open_pdf(upload.data)
    proposed = outline_chapters(reader)
    draft = UploadDraft(
        teacher_id=teacher.id, kind="whole_book", book_id=book.id,
        source_file=save_by_hash(upload.data, upload.sha256, "pdf"), source_sha256=upload.sha256,
        page_count=len(reader.pages), payload={"proposed": [r.model_dump() for r in proposed]},
    )
    db.add(draft)
    db.commit()
    return draft, proposed


def get_draft(db: Session, teacher: User, draft_id: uuid.UUID, kind: str, book_id: Optional[uuid.UUID] = None) -> UploadDraft:
    draft = db.get(UploadDraft, draft_id)
    if draft is None or draft.teacher_id != teacher.id or draft.kind != kind or (book_id and draft.book_id != book_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload not found (it may have expired). Please upload it again.")
    return draft


def split_into_chapters(db: Session, book: Book, draft: UploadDraft, ranges: list[ChapterRange]) -> list[Chapter]:
    """Creates one Chapter per range, each with its own stored PDF slice, marked 'processing'.
    The caller commits and schedules one background job per chapter."""
    from app.core.storage import read_file
    from app.pipeline.jobs import mark_processing

    reader = open_pdf(read_file(draft.source_file))
    last = max((c.sequence_num or 0 for c in book.chapters), default=0)
    chapters = []
    for offset, r in enumerate(validate_ranges(ranges, len(reader.pages)), start=1):
        part = split_pdf(reader, r.start_page, r.end_page)
        digest = sha256_hex(part)
        chapter = Chapter(
            book_id=book.id, title=r.title.strip(), sequence_num=last + offset,
            source_file=save_by_hash(part, digest, "pdf"), source_sha256=digest,
        )
        mark_processing(chapter)
        db.add(chapter)
        chapters.append(chapter)
    return chapters
