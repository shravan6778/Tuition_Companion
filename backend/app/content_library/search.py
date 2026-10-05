"""Searching the library (official books + the teacher's own), and matching extracted metadata to known books."""
import re
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.content_library import access
from app.models import Book, User
from app.pipeline.graph import normalize_name

_ROMAN = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10, "xi": 11, "xii": 12}


def normalize_class(value: Optional[str]) -> str:
    """'Class 9', 'IX', '9th', 'Grade 9' -> '9'."""
    s = normalize_name(value or "")
    digits = re.search(r"\d+", s)
    if digits:
        return digits.group()
    for token in s.split():
        if token in _ROMAN:
            return str(_ROMAN[token])
    return s


def search_books(
    db: Session, teacher: User, *, q: Optional[str] = None, board: Optional[str] = None,
    class_name: Optional[str] = None, subject: Optional[str] = None, publisher: Optional[str] = None,
    scope: str = "all",
):
    """Books visible to this teacher, case-insensitive 'contains' on each filter; q searches all text fields."""
    query = access.teacher_visible_books(teacher)
    if scope == "mine":
        query = query.where(Book.owner_teacher_id == teacher.id)
    elif scope == "reference":
        query = query.where(Book.is_reference.is_(True))
    for column, value in ((Book.board, board), (Book.subject, subject), (Book.publisher, publisher)):
        if value and value.strip():
            query = query.where(func.lower(column).contains(value.strip().lower(), autoescape=True))
    if class_name and class_name.strip():
        wanted = normalize_class(class_name)
        query = query.where(or_(
            func.lower(Book.class_name).contains(class_name.strip().lower(), autoescape=True),
            func.lower(Book.class_name).contains(wanted.lower(), autoescape=True),
        ))
    if q and q.strip():
        for word in q.lower().split():
            query = query.where(or_(*(
                func.lower(c).contains(word, autoescape=True)
                for c in (Book.board, Book.class_name, Book.subject, Book.publisher, Book.edition, Book.school)
            )))
    return query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)


def match_metadata(db: Session, teacher: User, metadata) -> list[Book]:
    """Visible books that agree with what the front pages say: same class and subject (when stated), and
    >= 2 stated fields / >= 75% of them match overall. Official ones first. Class is compared as a number,
    so 'IX' equals 'Class 9'."""
    stated = {
        "board": normalize_name(metadata.board or ""),
        "class": normalize_class(metadata.class_name),
        "subject": normalize_name(metadata.subject or ""),
        "publisher": normalize_name(metadata.publisher or ""),
    }
    stated = {k: v for k, v in stated.items() if v}
    if len(stated) < 2:
        return []
    scored = []
    for book in db.scalars(access.teacher_visible_books(teacher)).all():
        have = {
            "board": normalize_name(book.board), "class": normalize_class(book.class_name),
            "subject": normalize_name(book.subject), "publisher": normalize_name(book.publisher),
        }
        if any(k in stated and have[k] != stated[k] for k in ("class", "subject")):
            continue  # a different class or subject is a different book, however well the rest matches
        hits = sum(1 for k, v in stated.items() if have[k] == v)
        if hits >= 2 and hits / len(stated) >= 0.75:
            scored.append((hits / len(stated), book.is_reference, book))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [b for _, _, b in scored[:5]]
