"""Raising a doubt (Phase 3 step 2): scope it, retrieve, record it, and say what the student may do next.
No answer is written here (step 3). The retrieval rules and the cut-off live in `doubts/retrieval.py`."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from dataclasses import dataclass

from app.assessment import mastery
from app.core.config import settings
from app.core.errors import ProcessingError
from app.doubts import tutor
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, RetrievalResult, Scope, retrieve, scope_for_concepts
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import Assignment, AssignmentLevel, Chapter, ChapterStatus, Concept, Doubt, Page, User, student_book

logger = logging.getLogger(__name__)

MESSAGES = {
    GROUNDED: "Found it in your book.",
    OUTSIDE: "That isn't part of this assignment, but your books do cover it. Try \"Ask a Doubt\" to look at it.",
    NOT_IN_BOOK: "This isn't in your book yet. Ask your teacher to add it.",
    UNAVAILABLE: "We couldn't look this up right now. Please try again in a little while.",
}


CHAPTER_OUTSIDE = "That isn't in the chapter you picked, but your books do cover it elsewhere. Have a look at where, or ask again without choosing a chapter."


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


def chapter_scope(chapter: Chapter) -> Scope:
    """Standalone "Ask a Doubt" with a chosen chapter: the search is narrowed to that one chapter."""
    return Scope(chapter_ids={str(chapter.id)})


def get_ready_chapter(db: Session, student: User, chapter_id: uuid.UUID) -> Optional[Chapter]:
    """A READY chapter of a book this student has linked, else None (the route answers 404, so a chapter of an unlinked or
    another teacher's book, or one still processing, is indistinguishable from one that doesn't exist)."""
    return db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.status == ChapterStatus.READY,
                                           Chapter.book_id.in_(linked_book_ids(db, student))))


def concept_doubt_text(db: Session, student: User, concept_id: uuid.UUID) -> Optional[str]:
    """The doubt text for a concept the student picked from a photographed page. None when that concept is not in a
    ready chapter of one of the student's linked books (the route answers 404: never reveals another book's concepts)."""
    row = db.execute(
        select(Concept.name, Concept.description).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id == concept_id, Chapter.status == ChapterStatus.READY, Chapter.book_id.in_(linked_book_ids(db, student)))
    ).first()
    if row is None:
        return None
    name, description = row
    return " ".join(f"I don't understand {name}. {description or ''}".split())[:1000]


def _providers():
    try:
        return get_embedding_provider(), get_graph_store()
    except Exception:  # a misconfigured provider must read as "unavailable", never a 500 or a guess
        logger.warning("Doubt providers could not start", exc_info=True)
        return None, None


def _refresher_material(db: Session, result: RetrievalResult, book_ids: list[uuid.UUID]) -> list[tuple[str, str]]:
    """(name, description) of the prerequisite concepts, read from PostgreSQL and only for ready chapters of the
    student's own books (the store's answer is never taken on trust)."""
    ids = [uuid.UUID(p.concept_id) for p in result.prerequisites]
    if not ids or not book_ids:
        return []
    rows = db.execute(
        select(Concept.id, Concept.name, Concept.description).join(Page, Page.id == Concept.page_id)
        .join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id.in_(ids), Chapter.book_id.in_(book_ids), Chapter.status == ChapterStatus.READY)
    ).all()
    by_id = {r[0]: (r[1], r[2] or "") for r in rows}
    return [by_id[i] for i in ids if i in by_id]


@dataclass
class DoubtOutcome:
    doubt: Doubt
    result: RetrievalResult
    answer: Optional[tutor.TutorAnswer] = None
    chapter: Optional[Chapter] = None  # the chapter a standalone doubt was narrowed to


def _explain(db: Session, text: str, result: RetrievalResult, book_ids: list[uuid.UUID]):
    """-> (answer_status, TutorAnswer | None). Only ever called for a grounded result."""
    pages = result.pages[: settings.tutor_max_pages]
    if not pages:
        return "failed", None
    try:
        answer = tutor.explain(get_llm_provider(), text, pages, result.concepts, _refresher_material(db, result, book_ids))
    except (ProcessingError, RuntimeError):  # model down, misconfigured, or no valid grounded reply: show the pages, never a guess
        logger.warning("Tutor could not answer", exc_info=True)
        return "failed", None
    return ("unanswered" if answer.cannot_answer else "answered"), answer


def raise_doubt(db: Session, student: User, text: str, assignment: Optional[Assignment], chapter: Optional[Chapter] = None) -> DoubtOutcome:
    """A doubt is scoped by its assignment, by a chosen chapter (standalone "Ask a Doubt"), or not at all (every linked book)."""
    if assignment is not None and chapter is not None:
        raise ValueError("a doubt has an assignment or a chapter, not both")
    scope = assignment_scope(db, assignment) if assignment is not None else chapter_scope(chapter) if chapter is not None else None
    embedder, store = _providers()
    book_ids = linked_book_ids(db, student)
    result = retrieve(db, text, embedder=embedder, store=store, book_ids=book_ids, scope=scope)
    best = result.concepts[0].concept_id if result.status == GROUNDED and result.concepts else None
    answer_status, answer = ("none", None)
    if result.status == GROUNDED:  # the ONLY status the Tutor is ever asked to answer
        answer_status, answer = _explain(db, text, result, book_ids)
    doubt = Doubt(
        student_id=student.id, assignment_id=assignment.id if assignment else None, text=text, status=result.status,
        concept_id=uuid.UUID(best) if best else None, confidence=round(result.confidence, 4),
        created_at=datetime.now(timezone.utc),  # microsecond order, so history is stable on every database
        answer_status=answer_status, answer=answer.answer if answer else None, refresher=answer.refresher if answer else None,
        needs_review=answer_status == "answered" and result.confidence < settings.tutor_verify_below,
        answer_model=(answer.model or None) if answer else None,
    )
    db.add(doubt)
    if best:  # the doubt event (mastery log) is written with the doubt itself: it feeds the "ask first" ordering of the next check
        mastery.record_doubt(db, student.id, uuid.UUID(best), assignment.id if assignment else None)
    db.commit()
    db.refresh(doubt)
    return DoubtOutcome(doubt, result, answer, chapter)
