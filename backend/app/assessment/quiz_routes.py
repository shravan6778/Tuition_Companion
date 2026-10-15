"""Teacher and Student Quiz routes (Phase 4 Step 2).

    POST   /teacher/quizzes/generate          generate a full test for a chapter or concept list (10/20/30 questions)
    POST   /teacher/quizzes/{id}/assign       link a generated quiz to a room, student, or existing assignment
    GET    /teacher/quizzes                   list this teacher's generated quizzes
    GET    /teacher/quizzes/{id}              view a quiz (includes answer keys and explanations for teacher review)
    DELETE /teacher/quizzes/{id}              delete a teacher quiz
    GET    /student/quizzes                   list quizzes visible to this student (assigned teacher tests + own practice)
    GET    /student/quizzes/{id}              student view of a quiz (NEVER includes answer keys before submission)"""
import uuid
from datetime import date, datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment import quiz_service
from app.auth.dependencies import require_student, require_teacher
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models import Concept, Quiz, QuizResponse

teacher_quiz_router = APIRouter(prefix="/teacher/quizzes", tags=["quizzes"], dependencies=[Depends(require_teacher)])
student_quiz_router = APIRouter(prefix="/student/quizzes", tags=["quizzes"], dependencies=[Depends(require_student)])
student_practice_router = APIRouter(prefix="/student/practice", tags=["quizzes"], dependencies=[Depends(require_student)])

FAILED_MESSAGE = "We couldn't write this question right now."


class TeacherQuizGenerateIn(BaseModel):
    book_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    concept_ids: Optional[list[uuid.UUID]] = Field(default=None, max_length=60)
    length: Optional[Literal["short", "medium", "long"]] = None
    question_count: Optional[int] = Field(default=None, ge=10, le=30)
    title: Optional[str] = Field(default=None, max_length=200)
    assignment_id: Optional[uuid.UUID] = None
    room_id: Optional[uuid.UUID] = None
    student_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


class TeacherQuizAssignIn(BaseModel):
    room_id: Optional[uuid.UUID] = None
    student_id: Optional[uuid.UUID] = None
    assignment_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


class QuizQuestionOut(BaseModel):
    id: uuid.UUID
    position: int
    concept_id: Optional[uuid.UUID] = None
    concept_name: Optional[str] = None
    related_concept_id: Optional[uuid.UUID] = None
    related_concept_name: Optional[str] = None
    question_type: str  # recall | application | cross_concept
    answer_format: str  # mcq | short_answer
    status: str  # ready | pending | failed
    question: Optional[str] = None
    options: Optional[list[str]] = None
    message: Optional[str] = None
    # Revealed ONLY to the owning teacher OR to a student AFTER submission:
    correct_index: Optional[int] = None
    expected_answer: Optional[str] = None
    explanation: Optional[str] = None
    chosen_index: Optional[int] = None
    answer_text: Optional[str] = None
    score: Optional[float] = None
    correct: Optional[bool] = None
    feedback: Optional[str] = None


class QuizOut(BaseModel):
    id: uuid.UUID
    kind: str  # teacher | practice
    book_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    assignment_id: Optional[uuid.UUID] = None
    title: str
    question_count: int
    status: str  # open | submitted
    score: Optional[float] = None
    created_at: datetime
    submitted_at: Optional[datetime] = None
    questions: list[QuizQuestionOut] = []


class QuizSummaryOut(BaseModel):
    id: uuid.UUID
    kind: str
    book_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    assignment_id: Optional[uuid.UUID] = None
    title: str
    question_count: int
    status: str
    score: Optional[float] = None
    created_at: datetime
    submitted_at: Optional[datetime] = None

class StudentPracticeGenerateIn(BaseModel):
    book_id: Optional[uuid.UUID] = None
    chapter_id: Optional[uuid.UUID] = None
    question_count: Optional[int] = Field(default=None, ge=2, le=30)
    title: Optional[str] = Field(default=None, max_length=200)
    
def _format_quiz_out(
    db: Session,
    quiz: Quiz,
    *,
    reveal_keys: bool,
    student_id: Optional[uuid.UUID] = None,
) -> QuizOut:
    cids = {q.concept_id for q in quiz.questions if q.concept_id} | {
        q.related_concept_id for q in quiz.questions if q.related_concept_id
    }
    names = {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_(cids)))} if cids else {}

    resp_by_qid: dict[uuid.UUID, QuizResponse] = {}
    if student_id is not None:
        resps = db.scalars(
            select(QuizResponse).where(QuizResponse.quiz_id == quiz.id, QuizResponse.student_id == student_id)
        ).all()
        resp_by_qid = {r.question_id: r for r in resps}

    student_submitted = bool(resp_by_qid) or quiz.status == quiz_service.SUBMITTED
    show_keys = reveal_keys or student_submitted

    questions_out: list[QuizQuestionOut] = []
    for q in quiz.questions:
        item = QuizQuestionOut(
            id=q.id,
            position=q.position,
            concept_id=q.concept_id,
            concept_name=names.get(q.concept_id),
            related_concept_id=q.related_concept_id,
            related_concept_name=names.get(q.related_concept_id) if q.related_concept_id else None,
            question_type=q.question_type,
            answer_format=q.answer_format,
            status=q.status,
        )
        if q.status == "ready":
            item.question = q.question
            item.options = list(q.options) if q.options is not None else None
            if show_keys:
                item.correct_index = q.correct_index
                item.expected_answer = q.expected_answer
                item.explanation = q.explanation
            resp = resp_by_qid.get(q.id)
            if resp is not None and show_keys:
                item.chosen_index = resp.chosen_index
                item.answer_text = resp.answer_text
                item.score = resp.score
                item.correct = resp.correct
                item.feedback = resp.feedback
        else:
            item.message = FAILED_MESSAGE if q.status == "failed" else "This question is still being written."
        questions_out.append(item)

    student_score = quiz.score
    student_status = quiz.status
    if student_id is not None and resp_by_qid:
        student_status = quiz_service.SUBMITTED
        scores = [r.score for r in resp_by_qid.values() if r.score is not None]
        if scores:
            student_score = round(sum(scores) / len(scores), 4)

    return QuizOut(
        id=quiz.id,
        kind=quiz.kind,
        book_id=quiz.book_id,
        chapter_id=quiz.chapter_id,
        assignment_id=quiz.assignment_id,
        title=quiz.title,
        question_count=quiz.question_count,
        status=student_status,
        score=student_score,
        created_at=quiz.created_at,
        submitted_at=quiz.submitted_at,
        questions=questions_out,
    )


def _summary_out(quiz: Quiz) -> QuizSummaryOut:
    return QuizSummaryOut(
        id=quiz.id,
        kind=quiz.kind,
        book_id=quiz.book_id,
        chapter_id=quiz.chapter_id,
        assignment_id=quiz.assignment_id,
        title=quiz.title,
        question_count=quiz.question_count,
        status=quiz.status,
        score=quiz.score,
        created_at=quiz.created_at,
        submitted_at=quiz.submitted_at,
    )


# ---- teacher routes --------------------------------------------------------

@teacher_quiz_router.post("/generate", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
def generate_quiz(body: TeacherQuizGenerateIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    limiter.check("quiz", str(teacher.id), settings.rate_quizzes_per_hour, 3600)
    spec = quiz_service.TeacherQuizSpec(**body.model_dump())
    quiz = quiz_service.generate_teacher_quiz(db, teacher, spec)
    return _format_quiz_out(db, quiz, reveal_keys=True)


@teacher_quiz_router.post("/{quiz_id}/assign", response_model=QuizOut)
def assign_quiz(quiz_id: uuid.UUID, body: TeacherQuizAssignIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    quiz = quiz_service.assign_teacher_quiz(
        db, teacher, quiz_id,
        room_id=body.room_id, student_id=body.student_id,
        assignment_id=body.assignment_id, due_date=body.due_date,
    )
    return _format_quiz_out(db, quiz, reveal_keys=True)


@teacher_quiz_router.get("", response_model=list[QuizSummaryOut])
def list_quizzes(
    book_id: Optional[uuid.UUID] = None,
    chapter_id: Optional[uuid.UUID] = None,
    assignment_id: Optional[uuid.UUID] = None,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    return [_summary_out(q) for q in quiz_service.list_teacher_quizzes(db, teacher, book_id, chapter_id, assignment_id)]


@teacher_quiz_router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return _format_quiz_out(db, quiz_service.get_teacher_quiz(db, teacher, quiz_id), reveal_keys=True)


@teacher_quiz_router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(quiz_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    quiz = quiz_service.get_teacher_quiz(db, teacher, quiz_id)
    db.delete(quiz)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- student routes (viewing assigned quizzes; practice + submit in steps 3-4) ----

@student_quiz_router.get("", response_model=list[QuizSummaryOut])
def my_quizzes(assignment_id: Optional[uuid.UUID] = None, student=Depends(require_student), db: Session = Depends(get_db)):
    return [_summary_out(q) for q in quiz_service.list_student_quizzes(db, student, assignment_id)]


@student_quiz_router.get("/{quiz_id}", response_model=QuizOut)
def my_quiz(quiz_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    quiz = quiz_service.get_student_quiz(db, student, quiz_id)
    return _format_quiz_out(db, quiz, reveal_keys=False, student_id=student.id)

@student_practice_router.post("/generate", response_model=QuizOut, status_code=status.HTTP_201_CREATED)
def generate_practice_quiz(
    body: StudentPracticeGenerateIn = StudentPracticeGenerateIn(),
    student=Depends(require_student),
    db: Session = Depends(get_db),
):
    # Tenancy check happens inside _resolve_student_practice_pool before any LLM call; check rate limit after book/chapter 404 check
    spec = quiz_service.StudentPracticeSpec(**body.model_dump())
    quiz_service._resolve_student_practice_pool(db, student, spec.book_id, spec.chapter_id)
    limiter.check("quiz_practice", str(student.id), settings.rate_quizzes_per_hour, 3600)
    quiz = quiz_service.generate_student_practice_quiz(db, student, spec)
    return _format_quiz_out(db, quiz, reveal_keys=False, student_id=student.id)