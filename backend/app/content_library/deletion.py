"""Deleting a chapter or a whole book, with everything under it (pages, concepts, edges, embeddings, teacher decisions)
and its copy in the graph store. Shared by the teacher routes (own books), the admin routes (official books) and the
operator tools (`app.db.drop_book`). The graph store is a rebuildable copy: if it cannot be cleaned right now, the
database deletion still goes ahead and `python -m app.db.sync_graph --prune` removes the leftovers later."""
import logging

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.graph_store import get_graph_store
from app.models import Book, Chapter
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


def delete_chapter(db: Session, chapter: Chapter) -> None:
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Wait for it to finish, then delete it.")
    cid = chapter.id
    db.delete(chapter)
    db.commit()
    _clean_graph_store([cid])


def delete_book(db: Session, book: Book) -> None:
    chapters = list(book.chapters)
    if any(is_actively_processing(c) for c in chapters):
        raise HTTPException(status.HTTP_409_CONFLICT, "A chapter of this book is still being processed. Wait for it to finish, then delete the book.")
    ids = [c.id for c in chapters]
    # books marked as a variant of this one simply stop being marked (the column has no delete rule of its own)
    db.execute(update(Book).where(Book.variant_of_id == book.id).values(variant_of_id=None))
    db.delete(book)
    db.commit()
    _clean_graph_store(ids)
