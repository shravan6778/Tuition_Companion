"""Delete a student-owned book and all derived content safely.

Database cascades remove pages, concepts, embeddings and edges. The graph store is
best-effort cleaned immediately, and hash-addressed PDFs are removed only when no
remaining DB row references the same stored file.
"""
import logging

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.storage import delete_file
from app.graph_store import get_graph_store
from app.models import Book, Chapter, UploadDraft
from app.pipeline.jobs import is_actively_processing

logger = logging.getLogger(__name__)


def _clean_graph_store(chapter_ids) -> None:
    try:
        store = get_graph_store()
        if store is not None:
            for cid in chapter_ids:
                store.delete_chapter(str(cid))
    except Exception:
        logger.exception("Could not remove chapters from the graph store; run `python -m app.db.sync_graph --prune`")


def delete_unreferenced_files(db: Session, paths: set[str]) -> None:
    for path in {p for p in paths if p}:
        still_book = db.scalar(select(Book.id).where(Book.front_pages_file == path).limit(1))
        still_chapter = db.scalar(select(Chapter.id).where(Chapter.source_file == path).limit(1))
        still_draft = db.scalar(select(UploadDraft.id).where(UploadDraft.source_file == path).limit(1))
        if not still_book and not still_chapter and not still_draft:
            delete_file(path)


def delete_chapter(db: Session, chapter: Chapter) -> None:
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Wait for it to finish, then delete it.")
    cid = chapter.id
    source_file = chapter.source_file
    db.delete(chapter)
    db.commit()
    _clean_graph_store([cid])
    delete_unreferenced_files(db, {source_file} if source_file else set())


def delete_book(db: Session, book: Book) -> None:
    if book.is_reference:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Reference books are read-only")
    chapters = list(book.chapters)
    if any(is_actively_processing(c) for c in chapters):
        raise HTTPException(status.HTTP_409_CONFLICT, "A chapter of this book is still being processed. Wait for it to finish, then delete the book.")
    ids = [c.id for c in chapters]
    paths = {c.source_file for c in chapters if c.source_file}
    if book.front_pages_file:
        paths.add(book.front_pages_file)
    paths.update(d.source_file for d in db.scalars(select(UploadDraft).where(UploadDraft.book_id == book.id)).all())
    # Variant metadata is no longer used for student-owned matching, but clear dependent pointers before delete.
    db.execute(update(Book).where(Book.variant_of_id == book.id).values(variant_of_id=None))
    db.delete(book)
    db.commit()
    _clean_graph_store(ids)
    delete_unreferenced_files(db, paths)
