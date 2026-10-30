"""Assignments target curriculum metadata, then resolve to each student's own book copy."""
import uuid
from datetime import date, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.assignments import service
from app.auth.dependencies import require_student, require_teacher
from app.db.session import get_db
from app.models import Assignment, AssignmentCheck, Concept, Doubt, Quiz

teacher_router = APIRouter(prefix="/teacher/assignments", tags=["assignments"], dependencies=[Depends(require_teacher)])
student_router = APIRouter(prefix="/student/assignments", tags=["assignments"], dependencies=[Depends(require_student)])


class AssignmentCreate(BaseModel):
    level: Literal["subject", "chapter", "concept", "exercise"]
    # Source book is only used to select/validate the teacher's metadata target. It is NOT stored on Assignment.
    book_id: uuid.UUID
    room_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    concept_ids: list[uuid.UUID] | None = Field(default=None, max_length=60)
    concept_names: list[str] | None = Field(default=None, max_length=60)
    item_label: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, max_length=200)
    due_date: date | None = None


class ExerciseProposalIn(BaseModel):
    book_id: uuid.UUID
    chapter_id: uuid.UUID
    page_numbers: list[int] | None = Field(default=None, max_length=60)


class ProposedConceptOut(BaseModel):
    concept_id: uuid.UUID
    name: str
    similarity: float
    pages: list[int]


class ExerciseProposalOut(BaseModel):
    status: str
    chapter_title: str
    exercise_pages: list[int]
    proposed: list[ProposedConceptOut]


class AssignmentConceptOut(BaseModel):
    name: str


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    level: str
    title: str
    room_id: uuid.UUID | None
    student_id: uuid.UUID | None
    subject: str
    chapter_title: str | None
    item_label: str | None
    due_date: date | None
    created_at: datetime
    concept_count: int = 0
    concepts: list[AssignmentConceptOut] = []
    resolved_book_id: uuid.UUID | None = None
    resolved_chapter_id: uuid.UUID | None = None
    available: bool = True
    availability_message: str | None = None


def _out(db: Session, a: Assignment, *, student=None, with_concepts=True) -> AssignmentOut:
    book = chapter = None
    available = True
    message = None
    if student is not None:
        book, chapter = service.resolve_student_target(db, student, a)
        if a.chapter_title and chapter is None:
            available = False
            message = "Upload this chapter to see this task."
        elif a.item_label and chapter is not None:
            # resolve_student_target already checks the item label
            available = True
    return AssignmentOut(
        id=a.id, level=a.level, title=a.title, room_id=a.room_id, student_id=a.student_id,
        subject=a.subject, chapter_title=a.chapter_title, item_label=a.item_label,
        due_date=a.due_date, created_at=a.created_at, concept_count=len(a.concepts),
        concepts=[AssignmentConceptOut(name=c.concept_name) for c in a.concepts] if with_concepts else [],
        resolved_book_id=book.id if book else None, resolved_chapter_id=chapter.id if chapter else None,
        available=available, availability_message=message,
    )


@teacher_router.post("/exercise-proposal", response_model=ExerciseProposalOut)
def exercise_proposal(body: ExerciseProposalIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    chapter, mapping = service.exercise_proposal(db, teacher, body.book_id, body.chapter_id, body.page_numbers)
    return ExerciseProposalOut(
        status=mapping.status, chapter_title=chapter.title, exercise_pages=mapping.exercise_pages,
        proposed=[ProposedConceptOut(concept_id=p.concept_id, name=p.name, similarity=round(p.similarity, 3), pages=sorted(set(p.pages)))
                  for p in mapping.proposed],
    )


@teacher_router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(body: AssignmentCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return _out(db, service.create_assignment(db, teacher, service.NewAssignment(**body.model_dump())))


@teacher_router.get("", response_model=list[AssignmentOut])
def list_assignments(room_id: uuid.UUID | None = None, student_id: uuid.UUID | None = None,
                     teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return [_out(db, a, with_concepts=False) for a in service.list_teacher_assignments(db, teacher, room_id, student_id)]


@teacher_router.get("/{assignment_id}", response_model=AssignmentOut)
def get_assignment(assignment_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return _out(db, service.get_teacher_assignment(db, teacher, assignment_id))


@teacher_router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(assignment_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    assignment = service.get_teacher_assignment(db, teacher, assignment_id)
    db.execute(update(Doubt).where(Doubt.assignment_id == assignment.id).values(assignment_id=None))
    db.execute(update(AssignmentCheck).where(AssignmentCheck.assignment_id == assignment.id).values(assignment_id=None))
    db.execute(update(Quiz).where(Quiz.assignment_id == assignment.id).values(assignment_id=None))
    db.delete(assignment); db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@student_router.get("", response_model=list[AssignmentOut])
def todays_work(student=Depends(require_student), db: Session = Depends(get_db)):
    return [_out(db, a, student=student, with_concepts=False) for a in service.list_student_assignments(db, student)]


@student_router.get("/{assignment_id}", response_model=AssignmentOut)
def my_assignment(assignment_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _out(db, service.get_student_assignment(db, student, assignment_id), student=student)
