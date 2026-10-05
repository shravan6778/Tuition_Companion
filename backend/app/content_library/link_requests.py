"""Student -> teacher chapter requests: 'this chapter isn't in my teacher's book yet, please add it'."""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Book, Chapter, ChapterRequest, ChapterStatus, User
from app.pipeline.graph import normalize_name


def clean_hint(hint: str) -> str:
    return " ".join(hint.split())


def create_request(
    db: Session, student: User, book: Book, hint: str, chapter_id: uuid.UUID | None
) -> tuple[ChapterRequest, bool]:
    """Returns (request, created). Asking twice for the same thing returns the existing open request."""
    if book.owner_teacher_id is None:
        raise HTTPException(409, "Official books are maintained by us. If a chapter is missing, tell your teacher.")
    hint = clean_hint(hint)
    if len(normalize_name(hint)) < 3:
        raise HTTPException(422, "Please say which chapter you need (name or number)")

    if chapter_id is not None:
        chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
        if chapter is None:
            raise HTTPException(404, "Chapter not found in this book")
        if chapter.status == ChapterStatus.READY:
            raise HTTPException(409, "That chapter is already available")

    open_requests = db.scalars(
        select(ChapterRequest).where(ChapterRequest.student_id == student.id, ChapterRequest.status == "open")
    ).all()
    key = normalize_name(hint)
    for existing in open_requests:
        if existing.book_id == book.id and (
            normalize_name(existing.chapter_hint) == key or (chapter_id and existing.chapter_id == chapter_id)
        ):
            return existing, False
    if len(open_requests) >= settings.open_requests_per_student:
        raise HTTPException(429, "You have too many open requests. Wait for your teacher to respond to some first.")

    request = ChapterRequest(
        student_id=student.id, teacher_id=book.owner_teacher_id, book_id=book.id,
        chapter_id=chapter_id, chapter_hint=hint,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request, True


def resolve(db: Session, request: ChapterRequest, new_status: str) -> ChapterRequest:
    request.status = new_status
    request.resolved_at = datetime.now(timezone.utc)
    return request


def fulfill_requests_for_chapter(db: Session, chapter: Chapter) -> int:
    """Called when a chapter becomes ready: closes open requests that asked for exactly this chapter, or whose
    wording (>= 4 characters) appears in its title. Does not commit; the caller does."""
    title_key = normalize_name(chapter.title)
    count = 0
    for request in db.scalars(
        select(ChapterRequest).where(ChapterRequest.book_id == chapter.book_id, ChapterRequest.status == "open")
    ).all():
        hint_key = normalize_name(request.chapter_hint)
        if request.chapter_id == chapter.id or (len(hint_key) >= 4 and hint_key in title_key):
            resolve(db, request, "fulfilled")
            count += 1
    return count
