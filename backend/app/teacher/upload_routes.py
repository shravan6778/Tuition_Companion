import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.content_library import upload as uploads
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db, get_session_factory
from app.pipeline.jobs import run_chapter_job
from app.schemas import (
    BookBrief, BookMetadataOut, ChapterOut, FrontPagesDraftOut, WholeBookConfirmIn, WholeBookPlanOut,
)

from app.pipeline.front_matter import is_empty  # noqa: E402

router = APIRouter()  # included into the /teacher router (teacher guard + prefix come from there)


@router.post("/book-drafts/front-pages", response_model=FrontPagesDraftOut, status_code=status.HTTP_201_CREATED)
def upload_front_pages(file: UploadFile = File(...), teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Step 1 of adding a book: the cover + publisher/edition pages (a few pages, PDF or image).
    Returns the metadata the system read and any known books that already match it. Creates no Book:
    confirm by calling POST /teacher/books with the draft_id and the (edited) metadata."""
    limiter.check("front-pages", str(teacher.id), settings.rate_front_pages_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    draft, metadata, matches = uploads.create_front_pages_draft(db, teacher, upload)
    warning = None
    if is_empty(metadata):
        chars = (draft.payload or {}).get("text_chars", 0)
        warning = (f"We read {chars} characters from these pages but could not find the book's details in them. "
                   "Upload the cover and the publisher/edition pages (clear scans), or fill the details in by hand.")
    return FrontPagesDraftOut(
        draft_id=draft.id, page_count=draft.page_count,
        metadata=BookMetadataOut(**metadata.model_dump()),
        matches=[BookBrief.model_validate(b) for b in matches],
        warning=warning,
    )


@router.post("/books/{book_id}/whole-book/plan", response_model=WholeBookPlanOut, status_code=status.HTTP_201_CREATED)
def plan_whole_book(book_id: uuid.UUID, file: UploadFile = File(...), teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Upload the entire textbook (PDF). Nothing is processed yet: the response proposes a chapter split
    (from the PDF's bookmarks, if any) for the teacher to review before confirming."""
    book = access.get_owned_book(db, teacher, book_id)
    limiter.check("whole-book-plan", str(teacher.id), settings.rate_whole_book_plan_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_whole_book_mb, pdf_only=True)
    draft, proposed = uploads.create_whole_book_plan(db, teacher, book, upload)
    return WholeBookPlanOut(draft_id=draft.id, page_count=draft.page_count, proposed_chapters=proposed)


@router.post(
    "/books/{book_id}/whole-book/confirm", response_model=list[ChapterOut], status_code=status.HTTP_202_ACCEPTED
)
def confirm_whole_book(
    book_id: uuid.UUID,
    body: WholeBookConfirmIn,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Splits the uploaded PDF by the confirmed page ranges into new chapters and processes each in the background."""
    book = access.get_owned_book(db, teacher, book_id)
    draft = uploads.get_draft(db, teacher, body.draft_id, "whole_book", book.id)
    chapters = uploads.split_into_chapters(db, book, draft, body.chapters)
    db.delete(draft)
    db.commit()
    for chapter in chapters:
        db.refresh(chapter)
        background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapters
