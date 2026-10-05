import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import link_requests
from app.db.session import get_db
from app.models import Book, Chapter, ChapterRequest, ChapterStatus, User
from app.schemas import BookBrief, ChapterRequestOut, FulfillRequestIn

router = APIRouter()


def _out(request: ChapterRequest, book: Book, student: User) -> ChapterRequestOut:
    return ChapterRequestOut(
        id=request.id, book=BookBrief.model_validate(book), chapter_hint=request.chapter_hint,
        chapter_id=request.chapter_id, status=request.status, created_at=request.created_at,
        resolved_at=request.resolved_at, student_name=student.name,
    )


def _own_request(db: Session, teacher: User, request_id: uuid.UUID) -> ChapterRequest:
    request = db.get(ChapterRequest, request_id)
    if request is None or request.teacher_id != teacher.id:
        raise HTTPException(404, "Request not found")
    return request


@router.get("/chapter-requests", response_model=list[ChapterRequestOut])
def list_requests(
    status: Literal["open", "fulfilled", "dismissed", "cancelled", "all"] = "open",
    teacher=Depends(require_teacher), db: Session = Depends(get_db),
):
    query = (
        select(ChapterRequest, Book, User)
        .join(Book, Book.id == ChapterRequest.book_id)
        .join(User, User.id == ChapterRequest.student_id)
        .where(ChapterRequest.teacher_id == teacher.id)
        .order_by(ChapterRequest.created_at.desc())
    )
    if status != "all":
        query = query.where(ChapterRequest.status == status)
    return [_out(r, b, s) for r, b, s in db.execute(query).all()]


@router.post("/chapter-requests/{request_id}/dismiss", response_model=ChapterRequestOut)
def dismiss_request(request_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    request = _own_request(db, teacher, request_id)
    if request.status != "open":
        raise HTTPException(409, "This request is already closed")
    link_requests.resolve(db, request, "dismissed")
    db.commit()
    return _out(request, db.get(Book, request.book_id), db.get(User, request.student_id))


@router.post("/chapter-requests/{request_id}/fulfill", response_model=ChapterRequestOut)
def fulfill_request(request_id: uuid.UUID, body: FulfillRequestIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Mark a request done (optionally pointing at the chapter that now covers it). Requests are also closed
    automatically when a matching chapter finishes processing."""
    request = _own_request(db, teacher, request_id)
    if request.status != "open":
        raise HTTPException(409, "This request is already closed")
    if body.chapter_id is not None:
        chapter = db.scalar(select(Chapter).where(Chapter.id == body.chapter_id, Chapter.book_id == request.book_id))
        if chapter is None:
            raise HTTPException(404, "Chapter not found in that book")
        if chapter.status != ChapterStatus.READY:
            raise HTTPException(409, "That chapter hasn't finished processing yet")
        request.chapter_id = chapter.id
    link_requests.resolve(db, request, "fulfilled")
    db.commit()
    return _out(request, db.get(Book, request.book_id), db.get(User, request.student_id))
