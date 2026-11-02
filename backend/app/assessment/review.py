"""The teacher's view of written and spoken answers, and the override.

    GET  /teacher/quizzes/{id}/responses              every student's answers to a test: transcript, input method, the key points
                                                      hit and missed, the score and who gave it (ai | teacher)
    GET  /teacher/assignments/{id}/checks             the same for the comprehension checks students took on an assignment
    POST /teacher/quiz-responses/{id}/override        the teacher's mark replaces the AI suggestion (points hit, or a score)
    POST /teacher/check-questions/{id}/override
    POST /teacher/quiz-responses/{id}/confirm         "confirm before grading": confirm (or correct) a held spoken answer's transcript;
    POST /teacher/check-questions/{id}/confirm        the model then gives its suggestion

An AI score is only ever a SUGGESTION (`score_source='ai'`, kept in `ai_score` when overridden). When a teacher changes a mark the
check's score is recomputed and the affected concepts are re-measured in the mastery log (`mastery.record_correction`): the earlier
event is replaced when the state is read, never edited or deleted.
Only the teacher who set the test or the assignment can see or change these; anyone else gets a 404."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment import answers as answer_rules, mastery, quiz_service, service as check_service
from app.assessment.views import WrittenResultOut, fill_written
from app.auth.dependencies import require_teacher
from app.db.session import get_db
from app.llm import get_llm_provider
from app.models import AnswerFormat, Assignment, AssignmentCheck, CheckQuestion, Concept, Quiz, QuizKind, QuizQuestion, QuizResponse, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teacher", tags=["answer-review"], dependencies=[Depends(require_teacher)])


class AnswerReviewOut(WrittenResultOut):
    id: uuid.UUID  # the QuizResponse id (tests) or the CheckQuestion id (checks): what override and confirm take
    position: int
    question: Optional[str] = None
    concept_name: Optional[str] = None
    options: Optional[list[str]] = None
    chosen_index: Optional[int] = None
    correct_index: Optional[int] = None
    correct: Optional[bool] = None
    ai_score: Optional[float] = None
    can_override: bool = False
    reviewed_at: Optional[datetime] = None


class StudentWorkOut(BaseModel):
    student_id: uuid.UUID
    student_name: Optional[str] = None
    check_id: Optional[uuid.UUID] = None
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    waiting_for_you: int = 0  # spoken answers held until you confirm the transcript
    answers: list[AnswerReviewOut]


class OverrideIn(BaseModel):
    points_hit: Optional[list[int]] = Field(default=None, max_length=20)  # the key points the answer hit; the score follows from their marks
    score: Optional[float] = Field(default=None, ge=0, le=1)  # or a score directly (also for an older answer with no key points)
    feedback: Optional[str] = Field(default=None, max_length=1000)  # a note to the student


class ConfirmIn(BaseModel):
    transcript: Optional[str] = Field(default=None, max_length=6000)  # the transcript as you corrected it; omit to accept it as it is


def _404(what: str) -> HTTPException:
    return HTTPException(404, f"{what} not found")


def _llm():
    try:
        return get_llm_provider()
    except Exception:
        logger.warning("Review model could not start", exc_info=True)
        return None


def _names(db: Session, concept_ids) -> dict[uuid.UUID, str]:
    ids = [c for c in concept_ids if c]
    return {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_(ids)))} if ids else {}


def _written_view(item: AnswerReviewOut, row, key_points, expected) -> AnswerReviewOut:
    fill_written(item, row, key_points, expected, reveal=True)
    item.ai_score, item.reviewed_at = row.ai_score, row.reviewed_at
    item.can_override = item.answer_format in AnswerFormat.WRITTEN
    return item


# ---- tests ------------------------------------------------------------------------------------------------------------

def _teacher_quiz(db: Session, teacher: User, quiz_id: uuid.UUID) -> Quiz:
    return quiz_service.get_teacher_quiz(db, teacher, quiz_id)


def _quiz_row(db: Session, teacher: User, response_id: uuid.UUID) -> tuple[QuizResponse, QuizQuestion, Quiz]:
    row = db.get(QuizResponse, response_id)
    quiz = db.get(Quiz, row.quiz_id) if row else None
    if row is None or quiz is None or quiz.kind != QuizKind.TEACHER or quiz.teacher_id != teacher.id:
        raise _404("Answer")
    return row, db.get(QuizQuestion, row.question_id), quiz


def _quiz_tally(db: Session, quiz: Quiz, student_id: uuid.UUID) -> dict:
    t = answer_rules.ConceptTally()
    rows = db.scalars(select(QuizResponse).where(QuizResponse.quiz_id == quiz.id, QuizResponse.student_id == student_id))
    by_q = {q.id: q for q in quiz.questions}
    for r in rows:
        t.add(by_q[r.question_id].concept_id if r.question_id in by_q else None, r.correct)
    return t.per_concept


@router.get("/quizzes/{quiz_id}/responses", response_model=list[StudentWorkOut])
def quiz_responses(quiz_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    quiz = _teacher_quiz(db, teacher, quiz_id)
    rows = list(db.scalars(select(QuizResponse).where(QuizResponse.quiz_id == quiz.id).order_by(QuizResponse.created_at, QuizResponse.id)))
    questions = {q.id: q for q in quiz.questions}
    names = _names(db, [q.concept_id for q in quiz.questions])
    students = {u.id: u.name for u in db.scalars(select(User).where(User.id.in_({r.student_id for r in rows})))} if rows else {}
    out: dict[uuid.UUID, StudentWorkOut] = {}
    for r in rows:
        q = questions.get(r.question_id)
        if q is None:
            continue
        work = out.setdefault(r.student_id, StudentWorkOut(student_id=r.student_id, student_name=students.get(r.student_id), submitted_at=r.created_at, answers=[]))
        item = AnswerReviewOut(id=r.id, position=q.position, question=q.question, concept_name=names.get(q.concept_id), answer_format=q.answer_format,
                               options=list(q.options) if q.options is not None else None, chosen_index=r.chosen_index, correct_index=q.correct_index if q.answer_format == "mcq" else None,
                               correct=r.correct, score=r.score, feedback=r.feedback)
        if q.answer_format in AnswerFormat.WRITTEN:
            _written_view(item, r, q.key_points, q.expected_answer)
        work.answers.append(item)
    for work in out.values():
        work.answers.sort(key=lambda a: a.position)
        scores = [a.score for a in work.answers if a.score is not None]
        work.score = round(sum(scores) / len(scores), 4) if scores else None
        work.waiting_for_you = sum(1 for a in work.answers if a.needs_confirm)
    return list(out.values())


def _after_quiz_change(db: Session, quiz: Quiz, student_id: uuid.UUID, before: dict) -> None:
    after = _quiz_tally(db, quiz, student_id)
    if after != before and after:
        mastery.record_correction(db, student_id, quiz.assignment_id, after, quiz_id=quiz.id)


@router.post("/quiz-responses/{response_id}/override", response_model=AnswerReviewOut)
def override_quiz_response(response_id: uuid.UUID, body: OverrideIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    row, q, quiz = _quiz_row(db, teacher, response_id)
    before = _quiz_tally(db, quiz, row.student_id)
    answer_rules.override(row, q.answer_format, q.key_points, teacher.id, points_hit=body.points_hit, score=body.score, feedback=body.feedback)
    db.flush()
    _after_quiz_change(db, quiz, row.student_id, before)
    db.commit()
    return _quiz_item(db, row, q)


@router.post("/quiz-responses/{response_id}/confirm", response_model=AnswerReviewOut)
def confirm_quiz_response(response_id: uuid.UUID, body: ConfirmIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    row, q, quiz = _quiz_row(db, teacher, response_id)
    before = _quiz_tally(db, quiz, row.student_id)
    name = _names(db, [q.concept_id]).get(q.concept_id, "")
    answer_rules.confirm_and_grade(_llm(), row, q.answer_format, q.question or "", q.key_points, q.expected_answer, name, teacher.id, body.transcript)
    db.flush()
    _after_quiz_change(db, quiz, row.student_id, before)
    db.commit()
    return _quiz_item(db, row, q)


def _quiz_item(db: Session, row: QuizResponse, q: QuizQuestion) -> AnswerReviewOut:
    item = AnswerReviewOut(id=row.id, position=q.position, question=q.question, concept_name=_names(db, [q.concept_id]).get(q.concept_id),
                           answer_format=q.answer_format, correct=row.correct, score=row.score, feedback=row.feedback)
    return _written_view(item, row, q.key_points, q.expected_answer)


# ---- assignment checks --------------------------------------------------------------------------------------------------

def _check_row(db: Session, teacher: User, question_id: uuid.UUID) -> tuple[CheckQuestion, AssignmentCheck, Assignment]:
    cq = db.get(CheckQuestion, question_id)
    check = db.get(AssignmentCheck, cq.check_id) if cq else None
    assignment = db.get(Assignment, check.assignment_id) if check is not None and check.assignment_id else None
    if cq is None or assignment is None or assignment.teacher_id != teacher.id or check.status != check_service.SUBMITTED:
        raise _404("Answer")
    return cq, check, assignment


def _check_item(db: Session, cq: CheckQuestion, names: dict) -> AnswerReviewOut:
    item = AnswerReviewOut(id=cq.id, position=cq.position, question=cq.question, concept_name=names.get(cq.concept_id), answer_format=cq.answer_format,
                           options=list(cq.options) if cq.options is not None else None, chosen_index=cq.chosen_index,
                           correct_index=cq.correct_index if cq.answer_format == "mcq" else None, correct=cq.correct, score=cq.score, feedback=cq.feedback)
    if cq.answer_format in AnswerFormat.WRITTEN:
        _written_view(item, cq, cq.key_points, cq.expected_answer)
    return item


@router.get("/assignments/{assignment_id}/checks", response_model=list[StudentWorkOut])
def assignment_checks(assignment_id: uuid.UUID, student_id: Optional[uuid.UUID] = None, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Submitted checks on this assignment, newest first. Needs the teacher who set it."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id, Assignment.teacher_id == teacher.id))
    if assignment is None:
        raise _404("Assignment")
    query = select(AssignmentCheck).where(AssignmentCheck.assignment_id == assignment.id, AssignmentCheck.status == check_service.SUBMITTED)
    if student_id is not None:
        query = query.where(AssignmentCheck.student_id == student_id)
    checks = list(db.scalars(query.order_by(AssignmentCheck.submitted_at.desc())))
    students = {u.id: u.name for u in db.scalars(select(User).where(User.id.in_({c.student_id for c in checks})))} if checks else {}
    out = []
    for c in checks:
        names = _names(db, [q.concept_id for q in c.questions])
        answers = [_check_item(db, q, names) for q in c.questions if q.status == "ready"]
        out.append(StudentWorkOut(student_id=c.student_id, student_name=students.get(c.student_id), check_id=c.id, submitted_at=c.submitted_at, score=c.score,
                                  waiting_for_you=sum(1 for a in answers if a.needs_confirm), answers=answers))
    return out


def _after_check_change(db: Session, check: AssignmentCheck, before: dict) -> None:
    check.score = check_service.overall_score(check)
    after = check_service.tally(check)
    if after != before and after:
        mastery.record_correction(db, check.student_id, check.assignment_id, after, check_id=check.id)


@router.post("/check-questions/{question_id}/override", response_model=AnswerReviewOut)
def override_check_question(question_id: uuid.UUID, body: OverrideIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    cq, check, _ = _check_row(db, teacher, question_id)
    before = check_service.tally(check)
    answer_rules.override(cq, cq.answer_format, cq.key_points, teacher.id, points_hit=body.points_hit, score=body.score, feedback=body.feedback)
    db.flush()
    _after_check_change(db, check, before)
    db.commit()
    return _check_item(db, cq, _names(db, [cq.concept_id]))


@router.post("/check-questions/{question_id}/confirm", response_model=AnswerReviewOut)
def confirm_check_question(question_id: uuid.UUID, body: ConfirmIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    cq, check, _ = _check_row(db, teacher, question_id)
    before = check_service.tally(check)
    names = _names(db, [cq.concept_id])
    answer_rules.confirm_and_grade(_llm(), cq, cq.answer_format, cq.question or "", cq.key_points, cq.expected_answer, names.get(cq.concept_id, ""), teacher.id, body.transcript)
    db.flush()
    _after_check_change(db, check, before)
    db.commit()
    return _check_item(db, cq, names)
