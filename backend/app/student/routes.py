import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.db.session import get_db
from app.models.content import Book, Chapter, Page, student_book
from app.models.room import Room, RoomMember
from app.pipeline.orchestrator import PipelineOrchestrator
from app.schemas import JoinRoomIn, RoomOut

router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


# ---------------------------------------------------------
# Schemas
# ---------------------------------------------------------

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
    concepts: list[ConceptOut] = []


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
    chapters: list[ChapterOut] = []


# ---------------------------------------------------------
# Rooms (Grouping students only)
# ---------------------------------------------------------

@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}


@router.post("/rooms/join", response_model=RoomOut)
def join_room(body: JoinRoomIn, student=Depends(require_student), db: Session = Depends(get_db)):
    room = db.scalar(select(Room).where(Room.join_code == body.join_code))
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid join code")
    already = db.scalar(
        select(RoomMember.id).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id)
    )
    if already:
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    try:
        db.add(RoomMember(room_id=room.id, user_id=student.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    return room


@router.get("/rooms", response_model=list[RoomOut])
def my_rooms(student=Depends(require_student), db: Session = Depends(get_db)):
    return db.scalars(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
        .order_by(RoomMember.joined_at.desc())
    ).all()


# ---------------------------------------------------------
# Book Linkage (Student <-> Book)
# ---------------------------------------------------------

@router.post("/books/{book_id}/link", status_code=status.HTTP_200_OK)
def link_book(book_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    """Link student to the specific Book they actually use in school."""
    book = db.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")

    existing = db.execute(
        select(student_book).where(
            student_book.c.student_id == student.id,
            student_book.c.book_id == book_id
        )
    ).first()

    if existing:
        return {"status": "already_linked", "book_id": book_id}

    db.execute(student_book.insert().values(student_id=student.id, book_id=book_id))
    db.commit()
    return {"status": "linked", "book_id": book_id}


@router.delete("/books/{book_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_book(book_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    db.execute(
        student_book.delete().where(
            student_book.c.student_id == student.id,
            student_book.c.book_id == book_id
        )
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/books", response_model=list[BookOut])
def my_books(student=Depends(require_student), db: Session = Depends(get_db)):
    """List all books the student is linked to."""
    return db.scalars(
        select(Book)
        .join(student_book, student_book.c.book_id == Book.id)
        .where(student_book.c.student_id == student.id)
    ).all()


@router.get("/books/{book_id}", response_model=BookOut)
def get_book_details(book_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    book = db.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def get_chapter_pages(book_id: int, chapter_id: int, student=Depends(require_student), db: Session = Depends(get_db)):
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")

    return db.scalars(
        select(Page).where(Page.chapter_id == chapter_id).order_by(Page.page_number)
    ).all()


# ---------------------------------------------------------
# Student On-The-Fly Doubt Single-Page Upload
# ---------------------------------------------------------

@router.post("/books/{book_id}/chapters/{chapter_id}/doubt-upload", response_model=list[PageOut])
async def student_doubt_upload(
    book_id: int,
    chapter_id: int,
    file: UploadFile = File(...),
    student=Depends(require_student),
    db: Session = Depends(get_db),
):
    """
    When a doubt page isn't in the system, process only that page,
    extract concepts for doubts, and add to Book as unverified.
    """
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")

    orchestrator = PipelineOrchestrator(db)
    file_bytes = await file.read()
    filename = file.filename or "page.jpg"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"

    pages = await orchestrator.process_upload(
        file_bytes=file_bytes,
        ext=ext,
        metadata={"book_id": book_id, "chapter_id": chapter_id},
        user_id=student.id,
        is_teacher=False,  # Student upload: marked as unverified
    )
    return pages