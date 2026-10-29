"""Who may see / change which Book. Single source of truth for content tenancy (Rules.md §2, §4).

- Reference books (NCERT etc.): readable by everyone, writable by no one through the API.
- Student books: uploaded by and owned by exactly one student. Only that student sees or links them. No other
  student, no teacher and no parent ever does, whatever rooms anyone has joined. Not-visible looks like
  "doesn't exist" (404).
- Teacher-owned books (TRANSITIONAL): still readable by their teacher, and by students of that teacher's rooms,
  until the upload routes move to the student side. That is the only branch of this module that still lets one
  person see a book somebody else uploaded; it is deleted together with the teacher upload routes.
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
    """Reference books + this student's own books (+ the TRANSITIONAL teacher branch below).

    A student-owned book matches only `owner_student_id == student.id`, so no other student, teacher or parent
    can ever see it, whatever rooms anyone has joined."""
    # TRANSITIONAL, deleted when the upload routes move to the student side: teachers' private books for the
    # student's rooms. Student-owned books never come through here (owner_teacher_id is NULL for them).
    my_teachers = (
        select(Room.teacher_id)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
    )
    return select(Book).where(or_(
        Book.is_reference.is_(True),
        Book.owner_student_id == student.id,
        Book.owner_teacher_id.in_(my_teachers),
    ))


def get_book_visible_to_student(db: Session, student: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(student_visible_books(student).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_student_owned_book(db: Session, student: User, book_id: uuid.UUID) -> Book:
    """For anything that changes a student's book (upload a chapter, remove the book)."""
    book = db.get(Book, book_id)
    if book is None:
        raise _not_found()
    if book.is_reference:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reference books are read-only")
    if book.owner_student_id != student.id:
        raise _not_found()  # someone else's book looks like it doesn't exist
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
