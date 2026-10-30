"""Content-library tenancy rules.

Reference books are platform-wide and read-only. Private books belong to exactly one
student. Teachers may inspect only privacy-safe metadata for students in their rooms;
they never receive page text or images through the content-library teacher API.
"""
import uuid

from fastapi import HTTPException, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models import Book, Room, RoomMember, User, student_book


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")


def teacher_visible_books(teacher: User) -> Select:
    """Only official/reference books are content-readable by teachers."""
    return select(Book).where(Book.is_reference.is_(True))


def teacher_metadata_visible_books(teacher: User) -> Select:
    """Books whose safe metadata may be shown to a teacher.

    This includes official books and private student books owned by students in
    one of the teacher's rooms. It deliberately returns no page-level content.
    """
    room_students = (
        select(RoomMember.user_id)
        .join(Room, Room.id == RoomMember.room_id)
        .where(Room.teacher_id == teacher.id)
    )
    return select(Book).where(
        or_(Book.is_reference.is_(True), Book.owner_student_id.in_(room_students))
    )


def get_book_visible_to_teacher(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(teacher_visible_books(teacher).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_book_metadata_visible_to_teacher(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(teacher_metadata_visible_books(teacher).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_owned_book(db: Session, student: User, book_id: uuid.UUID) -> Book:
    """A mutating operation is allowed only on the current student's private book."""
    book = db.get(Book, book_id)
    if book is None:
        raise _not_found()
    if book.is_reference:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reference books are read-only")
    if book.owner_student_id != student.id:
        raise _not_found()
    return book


def student_visible_books(student: User) -> Select:
    """Reference books + this student's own private books. Never another student's."""
    return select(Book).where(
        or_(Book.is_reference.is_(True), Book.owner_student_id == student.id)
    )


def get_book_visible_to_student(db: Session, student: User, book_id: uuid.UUID) -> Book:
    book = db.scalar(student_visible_books(student).where(Book.id == book_id))
    if book is None:
        raise _not_found()
    return book


def get_linked_book(db: Session, student: User, book_id: uuid.UUID) -> Book:
    """Page content is readable for the student's own books or linked reference books."""
    book = db.scalar(
        select(Book).where(
            Book.id == book_id,
            or_(
                Book.owner_student_id == student.id,
                Book.id.in_(select(student_book.c.book_id).where(student_book.c.student_id == student.id)),
            ),
        )
    )
    if book is None:
        raise _not_found()
    return book
