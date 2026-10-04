import uuid
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.core.config import settings
from app.core.storage import detect_extension, save_by_hash, sha256_hex
from app.db.session import get_db, get_session_factory
from app.models.content import Book, Chapter, ChapterStatus, Page
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job
from app.schemas import BookCreate, BookOut, ChapterCreate, ChapterOut, MemberOut, PageOut, RoomCreate, RoomOut
from app.teacher import rooms as svc

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


@router.get("/ping")
def ping(user=Depends(require_teacher)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(body: RoomCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.create_room(db, teacher, body.name, body.room_type)


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.list_rooms(db, teacher)


@router.get("/rooms/{room_id}/members", response_model=list[MemberOut])
def room_members(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    return svc.list_members(db, room)


# ---- books (reference corpus + this teacher's own uploads only) ------------------

@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    if body.variant_of_id is not None:
        # A variant may only point at a book this teacher can already see (never someone else's private book).
        access.get_book_visible_to_teacher(db, teacher, body.variant_of_id)
    book = Book(
        board=body.board.strip(),
        class_name=body.class_name.strip(),
        subject=body.subject.strip(),
        publisher=body.publisher.strip(),
        edition=body.edition,
        is_customized=body.is_customized,
        school=body.school,
        variant_of_id=body.variant_of_id,
        is_reference=False,  # reference books are created only by the seed/ingest scripts
        owner_teacher_id=teacher.id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books", response_model=list[BookOut])
def list_books(
    scope: Literal["all", "mine", "reference"] = "all",
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    publisher: Optional[str] = None,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    query = access.teacher_visible_books(teacher)
    if scope == "mine":
        query = query.where(Book.owner_teacher_id == teacher.id)
    elif scope == "reference":
        query = query.where(Book.is_reference.is_(True))
    if board: query = query.where(Book.board == board)
    if class_name: query = query.where(Book.class_name == class_name)
    if subject: query = query.where(Book.subject == subject)
    if publisher: query = query.where(Book.publisher == publisher)
    return db.scalars(query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)).all()


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return access.get_book_visible_to_teacher(db, teacher, book_id)


@router.post("/books/{book_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
def create_chapter(book_id: uuid.UUID, body: ChapterCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, teacher, book_id)
    chapter = Chapter(book_id=book.id, title=body.title, sequence_num=body.sequence_num)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/books/{book_id}/chapters", response_model=list[ChapterOut])
def list_chapters(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    return db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)).all()


def _owned_chapter(db: Session, teacher, book_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter:
    book = access.get_owned_book(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/pages/upload",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def teacher_upload_pages(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    response: Response,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Saves the file and starts processing in the background. Poll the chapter's `status`.
    Uploading again REPLACES the chapter's pages (one file per chapter)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Please wait for it to finish.")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The uploaded file is empty")
    if len(data) > max_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f"File is too large (max {settings.max_upload_mb} MB)")
    ext = detect_extension(data)  # by file content, never the filename
    if ext is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Please upload a PDF, PNG or JPG file")

    digest = sha256_hex(data)
    if chapter.status == ChapterStatus.READY and chapter.source_sha256 == digest:
        response.status_code = status.HTTP_200_OK  # same file as last time: nothing to redo
        return chapter

    chapter.source_file = save_by_hash(data, digest, ext)
    chapter.source_sha256 = digest
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/retry",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_chapter(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Re-runs processing on the file already uploaded, after a failure (or a stuck job)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed.")
    if chapter.status not in (ChapterStatus.FAILED, ChapterStatus.PROCESSING) or not chapter.source_file:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nothing to retry for this chapter")
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def list_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()
