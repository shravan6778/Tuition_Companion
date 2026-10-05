import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access, link_requests
from app.db.session import get_db
from app.models import Book, ChapterRequest
from app.schemas import BookBrief, ChapterRequestCreate, ChapterRequestOut

router = APIRouter()


def _out(request: ChapterRequest, book: Book) -> ChapterRequestOut:
    return ChapterRequestOut(
        id=request.id, book=BookBrief.model_validate(book), chapter_hint=request.chapter_hint,
        chapter_id=request.chapter_id, status=request.status, created_at=request.created_at,
        resolved_at=request.resolved_at,
    )


@router.post("/books/{book_id}/chapter-requests", response_model=ChapterRequestOut, status_code=status.HTTP_201_CREATED)
def request_chapter(
    book_id: uuid.UUID, body: ChapterRequestCreate, response: Response,
    student=Depends(require_student), db: Session = Depends(get_db),
):
    """Ask the book's teacher to add a chapter that isn't available yet. Only for books you've linked."""
    book = access.get_linked_book(db, student, book_id)
    request, created = link_requests.create_request(db, student, book, body.chapter_hint, body.chapter_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return _out(request, book)


@router.get("/chapter-requests", response_model=list[ChapterRequestOut])
def my_requests(student=Depends(require_student), db: Session = Depends(get_db)):
    rows = db.execute(
        select(ChapterRequest, Book)
        .join(Book, Book.id == ChapterRequest.book_id)
        .where(ChapterRequest.student_id == student.id)
        .order_by(ChapterRequest.created_at.desc())
    ).all()
    return [_out(r, b) for r, b in rows]


@router.delete("/chapter-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_request(request_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    request = db.get(ChapterRequest, request_id)
    if request is None or request.student_id != student.id:
        raise HTTPException(404, "Request not found")
    if request.status == "open":
        link_requests.resolve(db, request, "cancelled")
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
