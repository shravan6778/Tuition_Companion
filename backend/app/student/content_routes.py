"""Student-owned textbook upload and removal endpoints.

Private textbook content never enters the teacher content-upload path. Every mutating
operation is scoped to the authenticated student and rate-limited by that student's id.
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access, deletion
from app.content_library import upload as uploads
from app.core.config import settings
from app.core.ratelimit import limiter
from app.core.storage import save_by_hash
from app.db.session import get_db, get_session_factory
from app.pipeline.jobs import mark_processing, run_chapter_job, is_actively_processing
from app.schemas import BookCreate, BookOut, ChapterCreate, ChapterOut, FrontPagesDraftOut, BookMetadataOut, BookBrief, WholeBookConfirmIn, WholeBookPlanOut
from app.models import Book, Chapter
from app.pipeline.front_matter import is_empty

router = APIRouter(prefix="/student", tags=["student-content"], dependencies=[Depends(require_student)])


def _book_out(book):
    # Students may see their own processed chapters; the normal BookOut schema already
    # contains no page text/images.
    return BookOut.model_validate(book)


@router.post("/book-drafts/front-pages", response_model=FrontPagesDraftOut, status_code=status.HTTP_201_CREATED)
def upload_front_pages(file: UploadFile = File(...), student=Depends(require_student), db: Session = Depends(get_db)):
    limiter.check("student-front-pages", str(student.id), settings.rate_student_front_pages_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    draft, metadata, matches = uploads.create_front_pages_draft(db, student, upload)
    warning = None
    if is_empty(metadata):
        chars = (draft.payload or {}).get("text_chars", 0)
        warning = (f"We read {chars} characters from these pages but could not find the book's details. "
                   "Upload clear cover/publisher pages or fill the details in by hand.")
    return FrontPagesDraftOut(
        draft_id=draft.id, page_count=draft.page_count,
        metadata=BookMetadataOut(**metadata.model_dump()),
        matches=[BookBrief.model_validate(b) for b in matches], warning=warning,
    )


@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, student=Depends(require_student), db: Session = Depends(get_db)):
    limiter.check("student-book-create", str(student.id), settings.rate_student_book_creates_per_hour, 3600)
    if body.variant_of_id is not None:
        # A student may compare only against a reference book; another student's book is never visible.
        base = access.get_book_visible_to_student(db, student, body.variant_of_id)
        if not base.is_reference:
            from fastapi import HTTPException
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    draft = None
    if body.draft_id is not None:
        draft = uploads.get_draft(db, student, body.draft_id, "front_pages")
    elif settings.require_front_pages:
        from fastapi import HTTPException
        raise HTTPException(422, "Upload the book's cover and publisher/edition pages first")
    book = Book(
        board=body.board.strip(), class_name=body.class_name.strip(), subject=body.subject.strip(),
        publisher=body.publisher.strip(), edition=body.edition, is_customized=body.is_customized,
        school=body.school, variant_of_id=body.variant_of_id if body.variant_of_id else None,
        is_reference=False, owner_student_id=student.id,
        metadata_source="front_pages" if draft else "manual",
        extracted_metadata=(draft.payload or {}).get("metadata") if draft else None,
        front_pages_file=draft.source_file if draft else None,
    )
    db.add(book)
    if draft:
        db.delete(draft)
    db.commit(); db.refresh(book)
    return _book_out(book)


@router.post("/books/{book_id}/whole-book/plan", response_model=WholeBookPlanOut, status_code=status.HTTP_201_CREATED)
def plan_whole_book(book_id: uuid.UUID, file: UploadFile = File(...), student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, student, book_id)
    limiter.check("student-whole-book-plan", str(student.id), settings.rate_student_whole_book_plans_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_whole_book_mb, pdf_only=True)
    draft, proposed = uploads.create_whole_book_plan(db, student, book, upload)
    return WholeBookPlanOut(draft_id=draft.id, page_count=draft.page_count, proposed_chapters=proposed)


@router.post("/books/{book_id}/whole-book/confirm", response_model=list[ChapterOut], status_code=status.HTTP_202_ACCEPTED)
def confirm_whole_book(book_id: uuid.UUID, body: WholeBookConfirmIn, background_tasks: BackgroundTasks,
                       student=Depends(require_student), db: Session = Depends(get_db), session_factory=Depends(get_session_factory)):
    book = access.get_owned_book(db, student, book_id)
    draft = uploads.get_draft(db, student, body.draft_id, "whole_book", book.id)
    chapters = uploads.split_into_chapters(db, book, draft, body.chapters)
    original_file = draft.source_file
    db.delete(draft); db.commit()
    deletion.delete_unreferenced_files(db, {original_file})
    for chapter in chapters:
        db.refresh(chapter)
        background_tasks.add_task(run_chapter_job, chapter.id, student.id, session_factory)
    return chapters


@router.post("/books/{book_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
def create_chapter(book_id: uuid.UUID, body: ChapterCreate, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, student, book_id)
    chapter = Chapter(book_id=book.id, title=body.title.strip(), sequence_num=body.sequence_num)
    db.add(chapter); db.commit(); db.refresh(chapter)
    return chapter


def _owned_chapter(db, student, book_id, chapter_id):
    book = access.get_owned_book(db, student, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if chapter is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Chapter not found")
    return chapter


@router.post("/books/{book_id}/chapters/{chapter_id}/pages/upload", response_model=ChapterOut, status_code=status.HTTP_202_ACCEPTED)
def upload_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, response: Response, background_tasks: BackgroundTasks,
                         file: UploadFile = File(...), student=Depends(require_student), db: Session = Depends(get_db),
                         session_factory=Depends(get_session_factory)):
    chapter = _owned_chapter(db, student, book_id, chapter_id)
    if is_actively_processing(chapter):
        from fastapi import HTTPException
        raise HTTPException(409, "This chapter is still being processed. Please wait for it to finish.")
    limiter.check("student-chapter-upload", str(student.id), settings.rate_student_chapter_uploads_per_hour, 3600)
    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    if chapter.status == "ready" and chapter.source_sha256 == upload.sha256:
        response.status_code = status.HTTP_200_OK
        return chapter
    chapter.source_file = save_by_hash(upload.data, upload.sha256, upload.ext)
    chapter.source_sha256 = upload.sha256
    mark_processing(chapter); db.commit(); db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, student.id, session_factory)
    return chapter


@router.post("/books/{book_id}/chapters/{chapter_id}/retry", response_model=ChapterOut, status_code=status.HTTP_202_ACCEPTED)
def retry_chapter(book_id: uuid.UUID, chapter_id: uuid.UUID, background_tasks: BackgroundTasks,
                  student=Depends(require_student), db: Session = Depends(get_db), session_factory=Depends(get_session_factory)):
    chapter = _owned_chapter(db, student, book_id, chapter_id)
    if is_actively_processing(chapter):
        from fastapi import HTTPException
        raise HTTPException(409, "This chapter is still being processed.")
    if chapter.status not in ("failed", "processing") or not chapter.source_file:
        from fastapi import HTTPException
        raise HTTPException(409, "Nothing to retry for this chapter")
    mark_processing(chapter); db.commit(); db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, student.id, session_factory)
    return chapter


@router.get("/books/{book_id}/chapters", response_model=list[ChapterOut])
def list_my_chapters(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_student(db, student, book_id)
    return db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(uploads.Chapter.sequence_num)).all()


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    deletion.delete_book(db, access.get_owned_book(db, student, book_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
