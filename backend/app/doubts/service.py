"""Raising a doubt (Phase 3 step 2): scope it, retrieve, record it, and say what the student may do next.
No answer is written here (step 3). The retrieval rules and the cut-off live in `doubts/retrieval.py`."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, RetrievalResult, Scope, retrieve, scope_for_concepts
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.models import Assignment, AssignmentLevel, Concept, Doubt, Page, User, student_book

logger = logging.getLogger(__name__)

MESSAGES = {
    GROUNDED: "Found it in your book.",
    OUTSIDE: "That isn't part of this assignment, but your books do cover it. Try \"Ask a Doubt\" to look at it.",
    NOT_IN_BOOK: "This isn't in your book yet. Ask your teacher to add it.",
    UNAVAILABLE: "We couldn't look this up right now. Please try again in a little while.",
}


def linked_book_ids(db: Session, student: User) -> list[uuid.UUID]:
    return list(db.scalars(select(student_book.c.book_id).where(student_book.c.student_id == student.id)))


def assignment_scope(db: Session, assignment: Assignment) -> Scope:
    """Chapter / subject level: the chapters its concepts sit in. Concept / exercise level: narrower, down to the
    pages those concepts are explained on (`scope_for_concepts`)."""
    concepts = list(db.scalars(select(Concept).where(Concept.id.in_([ac.concept_id for ac in assignment.concepts]))))
    if assignment.level in (AssignmentLevel.CONCEPT, AssignmentLevel.EXERCISE):
        return scope_for_concepts(db, concepts)
    chapter_ids = {str(db.get(Page, c.page_id).chapter_id) for c in concepts}
    return Scope(chapter_ids=chapter_ids)


def _providers():
    try:
        return get_embedding_provider(), get_graph_store()
    except Exception:  # a misconfigured provider must read as "unavailable", never a 500 or a guess
        logger.warning("Doubt providers could not start", exc_info=True)
        return None, None


def raise_doubt(db: Session, student: User, text: str, assignment: Optional[Assignment]) -> tuple[Doubt, RetrievalResult]:
    scope = assignment_scope(db, assignment) if assignment is not None else None
    embedder, store = _providers()
    result = retrieve(db, text, embedder=embedder, store=store, book_ids=linked_book_ids(db, student), scope=scope)
    best = result.concepts[0].concept_id if result.status == GROUNDED and result.concepts else None
    doubt = Doubt(
        student_id=student.id, assignment_id=assignment.id if assignment else None, text=text, status=result.status,
        concept_id=uuid.UUID(best) if best else None, confidence=round(result.confidence, 4),
        created_at=datetime.now(timezone.utc),  # microsecond order, so history is stable on every database
    )
    db.add(doubt)
    db.commit()
    db.refresh(doubt)
    return doubt, result
