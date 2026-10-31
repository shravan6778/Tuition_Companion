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
from app.doubts.query import normalize_doubt_text
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, RetrievalResult, Scope, retrieve, scope_for_concepts
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import Assignment, AssignmentLevel, Book, Chapter, ChapterStatus, Concept, Doubt, Page, User, student_book
from app.assignments import service as assignment_service

logger = logging.getLogger(__name__)

MESSAGES = {
    GROUNDED: "Found it in your book.",
    OUTSIDE: "That isn't part of this assignment, but your books do cover it. Try \"Ask a Doubt\" to look at it.",
    NOT_IN_BOOK: "This isn't in your book yet. Upload this chapter to continue.",
    UNAVAILABLE: "We couldn't look this up right now. Please try again in a little while.",
}


CHAPTER_OUTSIDE = "That isn't in the chapter you picked, but your books do cover it elsewhere. Have a look at where, or ask again without choosing a chapter."


def linked_book_ids(db: Session, student: User) -> list[uuid.UUID]:
    """All private books owned by the student plus explicitly linked reference books."""
    own = select(Book.id).where(Book.owner_student_id == student.id)
    refs = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    return list(db.scalars(select(Book.id).where(Book.id.in_(own.union(refs)))))


def assignment_scope(db: Session, student: User, assignment: Assignment) -> Scope:
    """Resolve the assignment's concept names against the student's own copy, never the source book ids."""
    book, chapter = assignment_service.resolve_student_target(db, student, assignment)
    if book is None:
        return Scope()
    if chapter is not None:
        concepts = assignment_service.chapter_concepts(db, chapter.id)
    else:
        concepts = assignment_service.subject_concepts(db, [book.id], assignment.subject)
    keys = {ac.concept_key for ac in assignment.concepts}
    if keys:
        concepts = [c for c in concepts if assignment_service.loose_key(c.name) in keys]
    if assignment.level in (AssignmentLevel.CONCEPT, AssignmentLevel.EXERCISE):
        return scope_for_concepts(db, concepts)
    chapter_ids = {str(db.get(Page, c.page_id).chapter_id) for c in concepts}
    return Scope(chapter_ids=chapter_ids)


def chapter_scope(chapter: Chapter) -> Scope:
    """Standalone "Ask a Doubt" with a chosen chapter: the search is narrowed to that one chapter."""
    return Scope(chapter_ids={str(chapter.id)})


def get_ready_chapter(db: Session, student: User, chapter_id: uuid.UUID) -> Optional[Chapter]:
    """A READY chapter of a book this student has linked, else None (the route answers 404, so a chapter of an unlinked or
    another student's book, or one still processing, is indistinguishable from one that doesn't exist)."""
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
        answer = tutor.explain(get_llm_provider(), text, pages, result.concepts, _refresher_material(db, result, book_ids), result.items)
    except (ProcessingError, RuntimeError):  # model down, misconfigured, or no valid grounded reply: show the pages, never a guess
        logger.warning("Tutor could not answer", exc_info=True)
        return "failed", None
    return ("unanswered" if answer.cannot_answer else "answered"), answer


def find_reusable_answer(
    db: Session,
    student: User,
    text: str,
    assignment_id: Optional[uuid.UUID] = None,
    chapter_id: Optional[uuid.UUID] = None,
) -> Optional[Doubt]:
    """Find an existing answered doubt that can safely be reused.

    Reuse is deliberately scoped to the same student and the same assignment
    or chapter.

    Matching rules:
    1. Exact normalized text is always reusable.
    2. A shorter normalized question may reuse a longer previously answered
       question when all of the shorter question's tokens occur in the
       previous question.
    3. The reverse is not allowed: a new, more specific question must not
       reuse a shorter old answer.
    4. Follow-up doubts are handled separately by the route and never reach
       this function.
    5. Assignment/chapter scope must match, preventing answers from one
       assignment or chapter leaking into another.
    """
    normalized = normalize_doubt_text(text)

    if not normalized:
        return None

    requested_tokens = normalized.split()

    candidates = db.scalars(
        select(Doubt)
        .where(
            Doubt.student_id == student.id,
            Doubt.answer_status == "answered",
            Doubt.assignment_id == assignment_id,
            Doubt.chapter_id == chapter_id,
        )
        .order_by(Doubt.created_at.desc())
        .limit(100)
    ).all()

    for candidate in candidates:
        if not candidate.answer:
            continue

        candidate_normalized = (
            candidate.normalized_text
            or normalize_doubt_text(candidate.text)
        )

        if not candidate_normalized:
            continue

        # Fast path: exact normalized match.
        if candidate_normalized == normalized:
            return candidate

        candidate_tokens = candidate_normalized.split()

        # Controlled narrowing:
        #
        # "what is a tissue"
        # is allowed to reuse
        # "what is a tissue group of similar cells"
        #
        # But:
        #
        # "what is a tissue group of similar cells"
        # must NOT reuse
        # "what is a tissue"
        #
        # This keeps reuse conservative while supporting the existing
        # repeated-doubt behavior.
        if (
            len(requested_tokens) >= 3
            and len(requested_tokens) <= len(candidate_tokens)
            and all(token in candidate_tokens for token in requested_tokens)
        ):
            return candidate

    return None


def raise_doubt(
    db: Session,
    student: User,
    text: str,
    assignment: Optional[Assignment],
    chapter: Optional[Chapter] = None,
    parent_doubt_id: Optional[uuid.UUID] = None,
) -> DoubtOutcome:
    """A doubt is scoped by its assignment, by a chosen chapter (standalone "Ask a Doubt"), or not at all (every linked book)."""
    if assignment is not None and chapter is not None:
        raise ValueError("a doubt has an assignment or a chapter, not both")
    if assignment is not None:
        target_book, target_chapter = assignment_service.resolve_student_target(db, student, assignment)
        if assignment.chapter_title and target_chapter is None:
            raise HTTPException(409, "Upload this chapter to see this task.")
    scope = assignment_scope(db, student, assignment) if assignment is not None else chapter_scope(chapter) if chapter is not None else None
    embedder, store = _providers()
    book_ids = linked_book_ids(db, student)
    # Follow-ups retrieve the original question's evidence, then ask the Tutor to answer the follow-up instruction.
    retrieval_text = text
    if parent_doubt_id is not None:
        parent = db.scalar(select(Doubt).where(Doubt.id == parent_doubt_id, Doubt.student_id == student.id))
        if parent is None:
            raise ValueError("parent doubt does not belong to this student")
        retrieval_text = parent.text
    result = retrieve(db, retrieval_text, embedder=embedder, store=store, book_ids=book_ids, scope=scope)
    best = result.concepts[0].concept_id if result.status == GROUNDED and result.concepts else None
    answer_status, answer = ("none", None)
    if result.status == GROUNDED:  # the ONLY status the Tutor is ever asked to answer
        answer_status, answer = _explain(db, text, result, book_ids)
    doubt = Doubt(
        student_id=student.id,
        normalized_text=normalize_doubt_text(text),
        parent_doubt_id=parent_doubt_id,
        assignment_id=assignment.id if assignment else None,
        chapter_id=chapter.id if chapter else None,
        text=text, status=result.status,
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
