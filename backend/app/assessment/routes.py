"""Mark complete and take the check (Phase 3 step 5).

    POST /student/assignments/{id}/complete   open (or resume) the check; the questions come back WITHOUT their keys
    GET  /student/checks/{id}                 resume an open check, or read a submitted one with its answers
    POST /student/checks/{id}/submit          grade by code; the key and the explanations are revealed only here
    GET  /student/checks                      this student's checks, newest first"""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment import service
from app.assignments import service as assignments
from app.auth.dependencies import require_student
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.assessment import mastery
from app.models import AssignmentCheck, Concept, MasteryEvent

router = APIRouter(prefix="/student", tags=["checks"], dependencies=[Depends(require_student)])
mastery_router = APIRouter(prefix="/student/mastery", tags=["mastery"], dependencies=[Depends(require_student)])

FAILED_MESSAGE = "We couldn't write this question right now."


class QuestionOut(BaseModel):
    id: uuid.UUID
    position: int
    concept_id: uuid.UUID | None
    concept_name: str | None
    status: str  # ready | pending | failed
    question: str | None = None
    options: list[str] | None = None
    message: str | None = None  # for a failed / pending question
    # Only after submission:
    chosen_index: int | None = None
    correct_index: int | None = None
    correct: bool | None = None
    explanation: str | None = None


class ConceptResultOut(BaseModel):
    concept_id: uuid.UUID | None
    concept_name: str
    score: float
    asked: int
    correct: int
    weak: bool


class AtRiskOut(BaseModel):
    concept_id: uuid.UUID | None
    concept_name: str
    reason: str  # always present: this is a flag from the graph, not a measurement


class CheckOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    assignment_title: str
    status: str  # open | submitted
    can_submit: bool
    score: float | None = None
    created_at: datetime
    submitted_at: datetime | None = None
    questions: list[QuestionOut]
    # Only after submission: how each concept went, and which dependent concepts this result put at risk (and why)
    concept_results: list[ConceptResultOut] | None = None
    at_risk: list[AtRiskOut] | None = None


class CheckSummaryOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    assignment_title: str
    status: str
    score: float | None
    created_at: datetime
    submitted_at: datetime | None


class AnswerIn(BaseModel):
    question_id: uuid.UUID
    chosen_index: int | None = Field(default=None, ge=0, le=3)


class SubmitIn(BaseModel):
    answers: list[AnswerIn] = Field(max_length=20)


def _out(db: Session, check: AssignmentCheck) -> CheckOut:
    ids = [q.concept_id for q in check.questions if q.concept_id]
    names = {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_(ids)))} if ids else {}
    revealed = check.status == service.SUBMITTED  # the ONLY time a key, explanation or choice leaves the server
    questions = []
    for q in check.questions:
        item = QuestionOut(id=q.id, position=q.position, concept_id=q.concept_id, concept_name=names.get(q.concept_id), status=q.status)
        if q.status == "ready":
            item.question, item.options = q.question, list(q.options)
            if revealed:
                item.chosen_index, item.correct_index, item.correct, item.explanation = q.chosen_index, q.correct_index, q.correct, q.explanation
        else:
            item.message = FAILED_MESSAGE if q.status == "failed" else "This question is still being written."
        questions.append(item)
    out = CheckOut(id=check.id, assignment_id=check.assignment_id, assignment_title=check.assignment_title, status=check.status,
                   can_submit=check.status == service.OPEN and service.can_submit(check), score=check.score,
                   created_at=check.created_at, submitted_at=check.submitted_at, questions=questions)
    if revealed:
        events = db.scalars(select(MasteryEvent).where(MasteryEvent.check_id == check.id).order_by(MasteryEvent.id)).all()
        out.concept_results = [ConceptResultOut(concept_id=e.concept_id, concept_name=e.concept_name, score=e.score, asked=e.asked, correct=e.correct,
                                                weak=e.score < settings.weak_below) for e in events if e.kind == mastery.CHECK]
        out.at_risk = [AtRiskOut(concept_id=e.concept_id, concept_name=e.concept_name, reason=e.reason) for e in events if e.kind == mastery.PROPAGATED]
    return out


@router.post("/assignments/{assignment_id}/complete", response_model=CheckOut)
def mark_complete(assignment_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    assignment = assignments.get_student_assignment(db, student, assignment_id)  # 404 first: nothing is learned from the rate limit
    limiter.check("check", str(student.id), settings.rate_checks_per_hour, 3600)
    return _out(db, service.start_check(db, student, assignment))


@router.get("/checks", response_model=list[CheckSummaryOut])
def my_checks(student=Depends(require_student), db: Session = Depends(get_db)):
    rows = db.scalars(select(AssignmentCheck).where(AssignmentCheck.student_id == student.id).order_by(AssignmentCheck.created_at.desc()).limit(50))
    return [CheckSummaryOut(id=c.id, assignment_id=c.assignment_id, assignment_title=c.assignment_title, status=c.status, score=c.score,
                            created_at=c.created_at, submitted_at=c.submitted_at) for c in rows]


@router.get("/checks/{check_id}", response_model=CheckOut)
def get_check(check_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _out(db, service.get_student_check(db, student, check_id))


@router.post("/checks/{check_id}/submit", response_model=CheckOut)
def submit_check(check_id: uuid.UUID, body: SubmitIn, student=Depends(require_student), db: Session = Depends(get_db)):
    check = service.get_student_check(db, student, check_id)
    return _out(db, service.submit(db, check, {a.question_id: a.chosen_index for a in body.answers}))


# ---- the student's mastery picture (built from the append-only log) -------------------------------------------

class MasteryConceptOut(BaseModel):
    concept_id: uuid.UUID
    concept_name: str
    status: str  # weak | at_risk | ok
    score: float | None  # the latest MEASURED score; null when the concept was only ever flagged
    asked: int | None
    correct: int | None
    last_checked: datetime | None
    reason: str | None = None  # at_risk: why ("flagged because it depends on X, which tested weak")
    flagged_by_concept_id: uuid.UUID | None = None


class MasteryOut(BaseModel):
    weak: int
    at_risk: int
    ok: int
    concepts: list[MasteryConceptOut]  # weak first, then at risk, then ok


class MasteryEventOut(BaseModel):
    id: int
    kind: str
    concept_id: uuid.UUID | None
    concept_name: str
    score: float | None
    asked: int | None
    correct: int | None
    reason: str | None
    assignment_id: uuid.UUID | None
    created_at: datetime


_ORDER = {mastery.WEAK: 0, mastery.AT_RISK: 1, mastery.OK: 2}


@mastery_router.get("", response_model=MasteryOut)
def my_mastery(status: str | None = None, student=Depends(require_student), db: Session = Depends(get_db)):
    states = list(mastery.current_state(db, student.id).values())
    states.sort(key=lambda s: (_ORDER[s.status], s.score if s.score is not None else 1.0, s.name))
    shown = [s for s in states if status is None or s.status == status]
    return MasteryOut(
        weak=sum(s.status == mastery.WEAK for s in states), at_risk=sum(s.status == mastery.AT_RISK for s in states), ok=sum(s.status == mastery.OK for s in states),
        concepts=[MasteryConceptOut(concept_id=s.concept_id, concept_name=s.name, status=s.status, score=s.score, asked=s.asked, correct=s.correct,
                                    last_checked=s.last_checked, reason=s.reason, flagged_by_concept_id=s.flagged_by) for s in shown])


@mastery_router.get("/events", response_model=list[MasteryEventOut])
def my_mastery_events(concept_id: uuid.UUID | None = None, student=Depends(require_student), db: Session = Depends(get_db)):
    """The log itself, newest first (100 at most): every check, doubt and flag, with the reason a flag carries."""
    query = select(MasteryEvent).where(MasteryEvent.student_id == student.id).order_by(MasteryEvent.id.desc()).limit(100)
    if concept_id is not None:
        query = query.where(MasteryEvent.concept_id == concept_id)
    return [MasteryEventOut(id=e.id, kind=e.kind, concept_id=e.concept_id, concept_name=e.concept_name, score=e.score, asked=e.asked,
                            correct=e.correct, reason=e.reason, assignment_id=e.assignment_id, created_at=e.created_at) for e in db.scalars(query)]
