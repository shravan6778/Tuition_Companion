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
from app.models import AssignmentCheck, Concept

router = APIRouter(prefix="/student", tags=["checks"], dependencies=[Depends(require_student)])

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
    return CheckOut(id=check.id, assignment_id=check.assignment_id, assignment_title=check.assignment_title, status=check.status,
                    can_submit=check.status == service.OPEN and service.can_submit(check), score=check.score,
                    created_at=check.created_at, submitted_at=check.submitted_at, questions=questions)


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
