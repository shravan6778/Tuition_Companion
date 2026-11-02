"""Mark complete -> comprehension check (Phase 3 step 5). Rules (Rules.md §1, Phases.md "Settled before building"):

  * "complete" is never self-reported alone: marking an assignment complete opens a check, and the check is the proof.
  * size   : `plan_check` over the assignment's STORED concept list, one question per concept inside the floor / ceiling;
             concepts the student asked doubts about come first when there are more concepts than the ceiling allows.
  * source : each question is written from its concept's own page (`generate_question`, validated, retried twice).
  * no leak: the student gets `student_view` only. The key, the explanation and what the student chose are shown only
             after `submit`. Multiple choice is graded in code; a written or spoken answer is marked by the model against its
             rubric of key points and labelled a SUGGESTION until a teacher has looked (assessment/answers.py).
  * answers: a share of the questions are short or long written answers (checks.plan_formats); typing is the baseline and a
             spoken answer is the same text after the student reviewed it. Maths-type subjects get no long and no spoken answers.
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

from app.assessment import answers as answer_rules, checks, mastery
from app.assessment.subject_policy import policy_for
from app.core.config import settings
from app.core.errors import ProcessingError
from app.assignments import service as assignment_service
from app.llm import get_llm_provider
from app.models import AnswerFormat, Assignment, AssignmentCheck, AssignmentLevel, CheckQuestion, Concept, Page, User

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


def _focus_by_concept(db: Session, student: User, assignment: Assignment | None) -> dict[uuid.UUID, str]:
    """Item-level assignments: for each concept, the picked items (label + text) that test it in THIS student's copy.
    Empty for every other level, or when the assignment or the student's chapter is gone."""
    if assignment is None or assignment.level != AssignmentLevel.ITEMS:
        return {}
    _, chapter = assignment_service.resolve_student_target(db, student, assignment)
    if chapter is None:
        return {}
    resolved = assignment_service.resolve_items(db, assignment, chapter)
    focus: dict[uuid.UUID, list[str]] = {}
    for item in resolved.items:
        for concept in assignment_service.concepts_of_items(db, chapter, [item]):
            focus.setdefault(concept.id, []).append(f"- {item.label} ({item.kind.replace('_', ' ')}): {(item.text or '')[:400]}")
    return {cid: "\n".join(lines[:4]) for cid, lines in focus.items()}


def _write(db: Session, llm, q: CheckQuestion, already: list[str], focus: str = "") -> None:
    """Fill one planned question from its concept's own page. Sets ready or failed; never leaves a half-written one."""
    concept = db.get(Concept, q.concept_id) if q.concept_id else None
    page = db.get(Page, concept.page_id) if concept is not None else None
    if llm is None or concept is None or page is None or not (page.content_text or "").strip():
        q.status = "failed"
        return
    try:
        if q.answer_format in AnswerFormat.WRITTEN:
            w = checks.generate_written_question(llm, q.answer_format, str(concept.id), concept.name, concept.description or "",
                                                 page.content_text, already_asked=already, focus=focus)
            q.question, q.expected_answer, q.key_points, q.explanation, q.status = w.question, w.expected_answer, w.key_points, w.explanation, "ready"
            return
        made = checks.generate_question(llm, str(concept.id), concept.name, concept.description or "", page.content_text,
                                        already_asked=already, seed=str(q.id), focus=focus)
    except (ProcessingError, RuntimeError):
        logger.warning("Check question could not be written", exc_info=True)
        q.status = "failed"
        return
    q.question, q.options, q.correct_index, q.explanation, q.status = made.question, made.options, made.correct_index, made.explanation, "ready"


def _fill(db: Session, check: AssignmentCheck) -> None:
    llm = _llm()
    student = db.get(User, check.student_id)
    focus = _focus_by_concept(db, student, db.get(Assignment, check.assignment_id) if check.assignment_id else None)
    for q in check.questions:
        if q.status == "ready":
            continue
        q.status = "pending"
        already = [o.question for o in check.questions if o.status == "ready" and o.concept_id == q.concept_id and o.question]
        _write(db, llm, q, already, focus.get(q.concept_id, "") if q.concept_id else "")
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
    """Mark complete. Resumes the open check (retrying its failed questions) or opens a new one.

    Never for a manual (homework) task: Rules.md wants book-grounded checks, and there is no book behind it. Its proof is the
    student's photo or spoken answer plus the teacher's verdict (assignments/manual.py). The route answers that case itself;
    this is the backstop so no other caller can make a model write questions for it."""
    if assignment.level == AssignmentLevel.MANUAL:
        raise HTTPException(409, "Homework tasks are verified by your teacher, not by a check")
    open_check = db.scalar(select(AssignmentCheck).where(
        AssignmentCheck.student_id == student.id, AssignmentCheck.assignment_id == assignment.id, AssignmentCheck.status == OPEN))
    if open_check is not None:
        if any(q.status != "ready" for q in open_check.questions):
            _fill(db, open_check)
        return open_check
    book, chapter = assignment_service.resolve_student_target(db, student, assignment)
    if assignment.chapter_title and chapter is None:
        raise HTTPException(409, "Upload this chapter to see this task.")
    if assignment.level == AssignmentLevel.ITEMS and chapter is not None:
        # item + page scope: the concepts the picked items test (plus any the teacher ticked), nothing else of the chapter
        available = assignment_service.resolve_items(db, assignment, chapter).concepts
    elif chapter is not None:
        available = assignment_service.chapter_concepts(db, chapter.id)
    elif book is not None:
        available = assignment_service.subject_concepts(db, [book.id], assignment.subject)
    else:
        raise HTTPException(409, "Upload this chapter to see this task.")
    wanted_keys = {ac.concept_key for ac in assignment.concepts}
    if wanted_keys and assignment.level != AssignmentLevel.ITEMS:  # items level already resolved its own concept list
        available = [c for c in available if assignment_service.loose_key(c.name) in wanted_keys]
    concept_ids = [str(c.id) for c in available]
    plan = checks.plan_check(concept_ids, priority_ids=_ask_first(db, student, [c.id for c in available]))
    if not plan:
        raise HTTPException(409, "This assignment has no concepts to check yet")
    check = AssignmentCheck(student_id=student.id, assignment_id=assignment.id, assignment_title=assignment.title, status=OPEN,
                            subject=assignment.subject)
    formats = checks.plan_formats(len(plan), allow_long=policy_for(assignment.subject).long_allowed)
    check.questions = [CheckQuestion(position=i, concept_id=uuid.UUID(cid), answer_format=formats[i], status="pending") for i, cid in enumerate(plan)]
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


def voice_allowed(check: AssignmentCheck) -> bool:
    return policy_for(check.subject).voice_allowed


def tally(check: AssignmentCheck) -> dict[uuid.UUID, tuple[int, int]]:
    """concept -> (asked, correct) over the graded questions. A spoken answer waiting for the teacher is not counted yet."""
    t = answer_rules.ConceptTally()
    for q in check.questions:
        if q.status == "ready" and q.correct is not None:
            t.add(q.concept_id, q.correct)
    return t.per_concept


def overall_score(check: AssignmentCheck) -> Optional[float]:
    """Mean of the graded questions' scores (a multiple-choice question is 1 or 0, a written one 0..1). None while nothing is graded."""
    scored = [(1.0 if q.correct else 0.0) if q.answer_format == AnswerFormat.MCQ else q.score for q in check.questions
              if q.status == "ready" and (q.answer_format == AnswerFormat.MCQ or q.score is not None)]
    return round(sum(scored) / len(scored), 4) if scored else None


def submit(db: Session, check: AssignmentCheck, answers: dict[uuid.UUID, "Optional[int] | answer_rules.AnswerInput"]) -> AssignmentCheck:
    """Grade and reveal. A question left out of `answers` is wrong. Once only.

    Multiple choice is graded by code; a written or spoken answer is marked by the model against its key points (a SUGGESTION).
    A bare int in `answers` is a multiple-choice choice (kept so older callers still work)."""
    if check.status != OPEN:
        raise HTTPException(409, "This check was already submitted")
    if not can_submit(check):
        raise HTTPException(409, "Some questions aren't ready yet. Please try again in a moment.")
    by_id = {q.id: q for q in check.questions}
    unknown = [a for a in answers if a not in by_id or by_id[a].status != "ready"]
    if unknown:
        raise HTTPException(422, "An answer doesn't match a question of this check")
    given = {qid: (a if isinstance(a, answer_rules.AnswerInput) else answer_rules.AnswerInput(chosen_index=a)) for qid, a in answers.items()}
    cleaned = {q.id: answer_rules.validate(q.answer_format, given.get(q.id, answer_rules.AnswerInput()), voice_allowed=voice_allowed(check))
               for q in check.questions if q.status == "ready"}  # every 422 happens before the first model call is paid for
    llm = _llm() if any(q.answer_format in AnswerFormat.WRITTEN and (cleaned[q.id].answer_text and not answer_rules.is_held(cleaned[q.id])) for q in check.questions if q.status == "ready") else None
    names = {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_([q.concept_id for q in check.questions if q.concept_id])))}
    try:
        _grade_all(check, cleaned, llm, names)
    except HTTPException:
        db.rollback()  # a model that fails half way leaves nothing half graded
        raise
    check.score = overall_score(check)
    check.status, check.submitted_at = SUBMITTED, datetime.now(timezone.utc)
    try:  # the graded check and its mastery events are ONE transaction: a half-written result never reaches the mastery log
        mastery.record_check(db, check.student_id, check.id, check.assignment_id, tally(check))
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(check)
    return check


def _grade_all(check: AssignmentCheck, cleaned: dict, llm, names: dict) -> None:
    for q in check.questions:
        if q.status != "ready":
            continue
        inp = cleaned[q.id]
        if q.answer_format == AnswerFormat.MCQ:
            g = checks.grade(checks.Question(str(q.concept_id), q.question, list(q.options), q.correct_index, q.explanation), inp.chosen_index)
            q.chosen_index = inp.chosen_index if isinstance(inp.chosen_index, int) and not isinstance(inp.chosen_index, bool) else None
            q.correct = g.correct
        else:
            out = answer_rules.grade_input(llm, inp, question=q.question, key_points=q.key_points, expected_answer=q.expected_answer,
                                           concept_name=names.get(q.concept_id, ""), fmt=q.answer_format)
            answer_rules.apply(q, inp, out)
