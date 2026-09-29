import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.db.session import get_db
from app.models.content import Book, Chapter, Page, Concept
from app.models.room import Room, RoomMember
from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas import MemberOut, RoomCreate, RoomOut
from app.teacher import rooms as svc

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


# ---------------------------------------------------------
# Schemas
# ---------------------------------------------------------

class BookCreate(BaseModel):
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool = False
    school: Optional[str] = None
    variant_of_id: Optional[int] = None


class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chapter_id: int
    page_number: int
    content_text: str
    verified: bool
    fingerprint: Optional[str] = None
    concepts: list[ConceptOut] = []


class ChapterCreate(BaseModel):
    title: str
    sequence_num: int = 1


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    book_id: int
    title: str
    sequence_num: int


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool
    school: Optional[str] = None
    variant_of_id: Optional[int] = None
    chapters: list[ChapterOut] = []


# ---------------------------------------------------------
# Room Management (Grouping students only - no shared content)
# ---------------------------------------------------------

@router.get("/ping")
def ping(user=Depends(require_teacher)):
    return {"role": user.role}


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


# ---------------------------------------------------------
# Book & Content Library
# ---------------------------------------------------------

@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, db: Session = Depends(get_db)):
    book = Book(
        board=body.board,
        class_name=body.class_name,
        subject=body.subject,
        publisher=body.publisher,
        edition=body.edition,
        is_customized=body.is_customized,
        school=body.school,
        variant_of_id=body.variant_of_id,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books", response_model=list[BookOut])
def list_books(
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Book)
    if board:
        query = query.where(Book.board == board)
    if class_name:
        query = query.where(Book.class_name == class_name)
    if subject:
        query = query.where(Book.subject == subject)
    return db.scalars(query).all()


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


# ---------------------------------------------------------
# Chapters
# ---------------------------------------------------------

@router.post("/books/{book_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
def create_chapter(book_id: int, body: ChapterCreate, db: Session = Depends(get_db)):
    book = db.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    chapter = Chapter(book_id=book.id, title=body.title, sequence_num=body.sequence_num)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/books/{book_id}/chapters", response_model=list[ChapterOut])
def list_chapters(book_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sequence_num)).all()


# ---------------------------------------------------------
# Pages & Pipeline Uploads
# ---------------------------------------------------------

@router.post("/books/{book_id}/chapters/{chapter_id}/pages/upload", response_model=list[PageOut])
async def teacher_upload_pages(
    book_id: int,
    chapter_id: int,
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")

    orchestrator = PipelineOrchestrator(db)
    file_bytes = await file.read()
    filename = file.filename or "file.pdf"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"

    pages = await orchestrator.process_upload(
        file_bytes=file_bytes,
        ext=ext,
        metadata={"book_id": book_id, "chapter_id": chapter_id},
        user_id=teacher.id,
        is_teacher=True,  # Deliberate upload: treated as verified
    )
    return pages


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def list_chapter_pages(book_id: int, chapter_id: int, db: Session = Depends(get_db)):
    return db.scalars(
        select(Page).where(Page.chapter_id == chapter_id).order_by(Page.page_number)
    ).all()


@router.get("/pages/unverified", response_model=list[PageOut])
def list_unverified_pages(db: Session = Depends(get_db)):
    """List student-contributed unverified pages needing teacher confirmation."""
    return db.scalars(select(Page).where(Page.verified == False).order_by(Page.id.desc())).all()


@router.post("/pages/{page_id}/verify", response_model=PageOut)
def verify_page(page_id: int, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Teacher confirms an unverified student-contributed page."""
    page = db.scalar(select(Page).where(Page.id == page_id))
    if not page:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
    page.verified = True
    db.commit()
    db.refresh(page)
    return page