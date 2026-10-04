import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access
from app.db.session import get_db
from app.models.content import Book, Chapter, ChapterStatus, Page, student_book
from app.models.room import Room, RoomMember
from app.schemas import BookOut, JoinRoomIn, PageOut, RoomOut

def _student_view(book: Book) -> BookOut:
    """Students only see chapters that finished processing."""
    out = BookOut.model_validate(book)
    out.chapters = [c for c in out.chapters if c.status == ChapterStatus.READY]
    return out


router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

@router.post("/rooms/join", response_model=RoomOut)
def join_room(body: JoinRoomIn, student=Depends(require_student), db: Session = Depends(get_db)):
    room = db.scalar(select(Room).where(func.lower(Room.join_code) == body.join_code.lower()))
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid join code")

    already = db.scalar(select(RoomMember.id).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id))
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
        select(Room).join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id).order_by(RoomMember.joined_at.desc())
    ).all()


# ---- books -----------------------------------------------------------------

@router.get("/library", response_model=list[BookOut])
def library(student=Depends(require_student), db: Session = Depends(get_db)):
    """Books this student may link but hasn't yet: reference books + books of teachers whose room they joined."""
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    query = access.student_visible_books(student).where(Book.id.not_in(linked))
    books = db.scalars(query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)).all()
    return [_student_view(b) for b in books]


@router.get("/books", response_model=list[BookOut])
def my_books(student=Depends(require_student), db: Session = Depends(get_db)):
    books = db.scalars(
        select(Book).join(student_book, student_book.c.book_id == Book.id)
        .where(student_book.c.student_id == student.id)
    ).all()
    return [_student_view(b) for b in books]


@router.get("/books/{book_id}", response_model=BookOut)
def get_book_details(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _student_view(access.get_book_visible_to_student(db, student, book_id))


@router.post("/books/{book_id}/link", status_code=status.HTTP_200_OK)
def link_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_student(db, student, book_id)
    existing = db.execute(
        select(student_book).where(student_book.c.student_id == student.id, student_book.c.book_id == book.id)
    ).first()
    if existing:
        return {"status": "already_linked", "book_id": book.id}
    db.execute(student_book.insert().values(student_id=student.id, book_id=book.id))
    db.commit()
    return {"status": "linked", "book_id": book.id}


@router.delete("/books/{book_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    db.execute(student_book.delete().where(student_book.c.student_id == student.id, student_book.c.book_id == book_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def get_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_linked_book(db, student, book_id)  # page content only for books the student has linked
    chapter = db.scalar(
        select(Chapter).where(
            Chapter.id == chapter_id, Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY
        )
    )
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()
