"""Who may see / change which Book. Single source of truth for content tenancy (Rules.md §2, §4).

- Reference books (NCERT etc.): readable by everyone, writable by no one through the API.
- Private books: owned by exactly one teacher. A student can only see/link them if the student has
  joined a room of that teacher. Nobody else ever sees them. Not-visible looks like "doesn't exist" (404).
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models import Book, Room, RoomMember, User, student_book


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")


# ---- teacher ---------------------------------------------------------------

def teacher_visible_books(teacher: User) -> Select:
    return select(Book).where(or_(Book.is_reference.is_(True), Book.owner_teacher_id == teacher.id))


def get_book_visible_to_teacher(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(teacher_visible_books(teacher).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_owned_book(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    """For anything that changes a book (add chapter, upload pages)."""
    book = db.get(Book, book_id)
    if book is None:
        raise _not_found()
    if book.is_reference:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reference books are read-only")
    if book.owner_teacher_id != teacher.id:
        raise _not_found()
    return book


# ---- student ---------------------------------------------------------------

def student_visible_books(student: User) -> Select:
    """Reference books + private books of any teacher whose room this student has joined."""
    my_teachers = (
        select(Room.teacher_id)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
    )
    return select(Book).where(or_(Book.is_reference.is_(True), Book.owner_teacher_id.in_(my_teachers)))


def get_book_visible_to_student(db: Session, student: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(student_visible_books(student).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_linked_book(db: Session, student: User, book_id: uuid.UUID) -> Book:
    """Page content is only readable for books the student has linked."""
    book = db.scalar(
        select(Book)
        .join(student_book, student_book.c.book_id == Book.id)
        .where(Book.id == book_id, student_book.c.student_id == student.id)
    )
    if book is None:
        raise _not_found()
    return book
