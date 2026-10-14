"""Standalone "Ask a Doubt" browse (Phase 3 step 7): Subject -> Book -> Chapter over every book the student has linked.
Only READY chapters are listed (students never see a chapter that is still processing or failed), and only books the
student linked, so the list is exactly the set a doubt can be searched in. Read-only; no model or embedding call."""
import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, Chapter, ChapterStatus, User, student_book


@dataclass
class BrowseChapter:
    id: uuid.UUID
    number: int
    title: str


@dataclass
class BrowseBook:
    id: uuid.UUID
    label: str
    chapters: list[BrowseChapter] = field(default_factory=list)


@dataclass
class BrowseSubject:
    subject: str
    books: list[BrowseBook] = field(default_factory=list)


def _label(book: Book) -> str:
    parts = [book.class_name, book.publisher, book.edition]
    return " · ".join(p for p in parts if p) or "Book"


def browse(db: Session, student: User) -> list[BrowseSubject]:
    """Subjects (case-insensitive, A-Z), each with the student's linked books and their ready chapters in book order.
    A book with no ready chapter is left out; so is a subject with no such book."""
    rows = db.execute(
        select(Book, Chapter).join(student_book, student_book.c.book_id == Book.id).join(Chapter, Chapter.book_id == Book.id)
        .where(student_book.c.student_id == student.id, Chapter.status == ChapterStatus.READY)
        .order_by(Book.subject, Book.class_name, Book.id, Chapter.sequence_num, Chapter.id)
    ).all()
    subjects: dict[str, BrowseSubject] = {}
    books: dict[uuid.UUID, BrowseBook] = {}
    for book, chapter in rows:
        name = (book.subject or "").strip() or "Other"
        subject = subjects.setdefault(name.lower(), BrowseSubject(name))
        entry = books.get(book.id)
        if entry is None:
            entry = books[book.id] = BrowseBook(book.id, _label(book))
            subject.books.append(entry)
        entry.chapters.append(BrowseChapter(chapter.id, chapter.sequence_num or len(entry.chapters) + 1, chapter.title or "Untitled chapter"))
    return sorted(subjects.values(), key=lambda s: s.subject.lower())
