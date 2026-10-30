"""Mark complete -> comprehension check (Phase 3 step 5). Rules (Rules.md §1, Phases.md "Settled before building"):

  * "complete" is never self-reported alone: marking an assignment complete opens a check, and the check is the proof.
  * size   : `plan_check` over the assignment's STORED concept list, one question per concept inside the floor / ceiling;
             concepts the student asked doubts about come first when there are more concepts than the ceiling allows.
  * source : each question is written from its concept's own page (`generate_question`, validated, retried twice).
  * no leak: the student gets `student_view` only. The key, the explanation and what the student chose are shown only
             after `submit`, which grades in code (never a model).
  * failure: a question the model never wrote validly is `failed` ("couldn't generate this right now": never blank or
             stale). Calling `start_check` again retries the failed / unfinished ones. A check can be submitted once at
             least CHECK_MIN_QUESTIONS (or all, if fewer were planned) questions exist; failed ones are not graded.
  * one open: a student has at most one OPEN check per assignment (a unique index), so a double click resumes it."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.assessment import checks, mastery
from app.core.config import settings
from app.core.errors import ProcessingError
from app.assignments import service as assignment_service
from app.llm import get_llm_provider
from app.models import Assignment, AssignmentCheck, CheckQuestion, Concept, Page, User

logger = logging.getLogger(__name__)

OPEN, SUBMITTED = "open", "submitted"


def _404(what: str) -> HTTPException:
    return HTTPException(404, f"{what} not found")


def get_student_check(db: Session, student: User, check_id: uuid.UUID) -> AssignmentCheck:
    found = db.scalar(select(AssignmentCheck).where(AssignmentCheck.id == check_id, AssignmentCheck.student_id == student.id))
    if found is None:
        raise _404("Check")
    return found


def _llm():
    try:
        return get_llm_provider()
    except Exception:  # a misconfigured provider means "couldn't generate", never a 500
        logger.warning("Check model could not start", exc_info=True)
        return None


def _write(db: Session, llm, q: CheckQuestion, already: list[str]) -> None:
    """Fill one planned question from its concept's own page. Sets ready or failed; never leaves a half-written one."""
    concept = db.get(Concept, q.concept_id) if q.concept_id else None
    page = db.get(Page, concept.page_id) if concept is not None else None
    if llm is None or concept is None or page is None or not (page.content_text or "").strip():
        q.status = "failed"
        return
    try:
        made = checks.generate_question(llm, str(concept.id), concept.name, concept.description or "", page.content_text,
                                        already_asked=already, seed=str(q.id))
    except (ProcessingError, RuntimeError):
        logger.warning("Check question could not be written", exc_info=True)
        q.status = "failed"
        return
    q.question, q.options, q.correct_index, q.explanation, q.status = made.question, made.options, made.correct_index, made.explanation, "ready"


def _fill(db: Session, check: AssignmentCheck) -> None:
    llm = _llm()
    for q in check.questions:
        if q.status == "ready":
            continue
        q.status = "pending"
        already = [o.question for o in check.questions if o.status == "ready" and o.concept_id == q.concept_id and o.question]
        _write(db, llm, q, already)
        db.commit()  # each question is kept as soon as it exists: a crash loses at most the one being written


def _ask_first(db: Session, student: User, concept_ids: list[uuid.UUID]) -> list[str]:
    """When the scope is bigger than the ceiling: concepts that tested weak first, then those flagged at risk, then those the
    student asked about (most recent first)."""
    state = mastery.current_state(db, student.id, concept_ids)
    wanted = set(concept_ids)
    weak = sorted((s for s in state.values() if s.status == mastery.WEAK), key=lambda s: s.score)
    at_risk = [s for s in state.values() if s.status == mastery.AT_RISK]
    doubted = [c for c in mastery.doubted_concept_ids(db, student.id) if c in wanted]
    return [str(i) for i in dict.fromkeys([s.concept_id for s in weak] + [s.concept_id for s in at_risk] + doubted)]


def start_check(db: Session, student: User, assignment: Assignment) -> AssignmentCheck:
    """Mark complete. Resumes the open check (retrying its failed questions) or opens a new one."""
    open_check = db.scalar(select(AssignmentCheck).where(
        AssignmentCheck.student_id == student.id, AssignmentCheck.assignment_id == assignment.id, AssignmentCheck.status == OPEN))
    if open_check is not None:
        if any(q.status != "ready" for q in open_check.questions):
            _fill(db, open_check)
        return open_check
    book, chapter = assignment_service.resolve_student_target(db, student, assignment)
    if assignment.chapter_title and chapter is None:
        raise HTTPException(409, "Upload this chapter to see this task.")
    if chapter is not None:
        available = assignment_service.chapter_concepts(db, chapter.id)
    elif book is not None:
        available = assignment_service.subject_concepts(db, [book.id], assignment.subject)
    else:
        raise HTTPException(409, "Upload this chapter to see this task.")
    wanted_keys = {ac.concept_key for ac in assignment.concepts}
    if wanted_keys:
        available = [c for c in available if assignment_service.loose_key(c.name) in wanted_keys]
    concept_ids = [str(c.id) for c in available]
    plan = checks.plan_check(concept_ids, priority_ids=_ask_first(db, student, [c.id for c in available]))
    if not plan:
        raise HTTPException(409, "This assignment has no concepts to check yet")
    check = AssignmentCheck(student_id=student.id, assignment_id=assignment.id, assignment_title=assignment.title, status=OPEN)
    check.questions = [CheckQuestion(position=i, concept_id=uuid.UUID(cid), status="pending") for i, cid in enumerate(plan)]
    db.add(check)
    try:
        db.commit()  # claims the one open slot before any model call is paid for
    except IntegrityError:
        db.rollback()
        return start_check(db, student, assignment)
    db.refresh(check)
    _fill(db, check)
    return check


def can_submit(check: AssignmentCheck) -> bool:
    ready = sum(1 for q in check.questions if q.status == "ready")
    return not any(q.status == "pending" for q in check.questions) and ready >= min(settings.check_min_questions, len(check.questions))


def submit(db: Session, check: AssignmentCheck, answers: dict[uuid.UUID, Optional[int]]) -> AssignmentCheck:
    """Grade by code and reveal. A question left out of `answers` is wrong. Once only."""
    if check.status != OPEN:
        raise HTTPException(409, "This check was already submitted")
    if not can_submit(check):
        raise HTTPException(409, "Some questions aren't ready yet. Please try again in a moment.")
    by_id = {q.id: q for q in check.questions}
    unknown = [a for a in answers if a not in by_id or by_id[a].status != "ready"]
    if unknown:
        raise HTTPException(422, "An answer doesn't match a question of this check")
    graded = []
    for q in check.questions:
        if q.status != "ready":
            continue
        g = checks.grade(checks.Question(str(q.concept_id), q.question, list(q.options), q.correct_index, q.explanation), answers.get(q.id))
        q.chosen_index = answers.get(q.id) if isinstance(answers.get(q.id), int) and not isinstance(answers.get(q.id), bool) else None
        q.correct = g.correct
        graded.append(g)
    check.score = round(sum(1 for g in graded if g.correct) / len(graded), 4)
    check.status, check.submitted_at = SUBMITTED, datetime.now(timezone.utc)
    per_concept: dict[uuid.UUID, tuple[int, int]] = {}
    for q in check.questions:
        if q.status == "ready" and q.concept_id is not None:
            asked, right = per_concept.get(q.concept_id, (0, 0))
            per_concept[q.concept_id] = (asked + 1, right + (1 if q.correct else 0))
    try:  # the graded check and its mastery events are ONE transaction: a half-written result never reaches the mastery log
        mastery.record_check(db, check.student_id, check.id, check.assignment_id, per_concept)
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(check)
    return check
