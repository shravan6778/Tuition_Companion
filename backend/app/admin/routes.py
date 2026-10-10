"""Administrator actions on OFFICIAL books (who is an administrator: ADMIN_USERNAMES). Teachers delete their own
books through /teacher/books/...; these routes exist only for the official library."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.admin import require_admin
from app.content_library import deletion
from app.db.session import get_db
from app.models import Book, Chapter

router = APIRouter(prefix="/admin", tags=["admin"])


def _official_book(db: Session, book_id: uuid.UUID) -> Book:
    book = db.get(Book, book_id)
    if book is None or not book.is_reference:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Official book not found")
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_book(book_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    deletion.delete_book(db, _official_book(db, book_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_chapter(book_id: uuid.UUID, chapter_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    book = _official_book(db, book_id)
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or chapter.book_id != book.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    deletion.delete_chapter(db, chapter)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
