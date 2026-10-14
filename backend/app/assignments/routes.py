"""Assignment routes (Phase 3 step 1): the teacher creates, the student sees "Today's Work"."""
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
from app.models import Assignment, AssignmentCheck, Chapter, Concept, Doubt, Quiz

teacher_router = APIRouter(prefix="/teacher/assignments", tags=["assignments"], dependencies=[Depends(require_teacher)])
student_router = APIRouter(prefix="/student/assignments", tags=["assignments"], dependencies=[Depends(require_student)])


class AssignmentCreate(BaseModel):
    level: Literal["subject", "chapter", "concept", "exercise"]
    book_id: uuid.UUID
    room_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    concept_ids: list[uuid.UUID] | None = Field(default=None, max_length=60)
    page_numbers: list[int] | None = Field(default=None, max_length=60)
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
    status: str  # ok | no_exercise_pages | no_vectors
    chapter_title: str
    exercise_pages: list[int]
    proposed: list[ProposedConceptOut]


class AssignmentConceptOut(BaseModel):
    id: uuid.UUID
    name: str


class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    level: str
    title: str
    room_id: uuid.UUID | None
    student_id: uuid.UUID | None
    book_id: uuid.UUID
    chapter_id: uuid.UUID | None
    chapter_title: str | None = None
    exercise_pages: list[int] | None
    due_date: date | None
    created_at: datetime
    concept_count: int = 0
    concepts: list[AssignmentConceptOut] = []


def _out(db: Session, a: Assignment, with_concepts: bool = True) -> AssignmentOut:
    ids = [ac.concept_id for ac in a.concepts]
    names = {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_(ids)))} if ids else {}
    chapter = db.get(Chapter, a.chapter_id) if a.chapter_id else None
    return AssignmentOut(
        id=a.id, level=a.level, title=a.title, room_id=a.room_id, student_id=a.student_id, book_id=a.book_id,
        chapter_id=a.chapter_id, chapter_title=chapter.title if chapter else None, exercise_pages=a.exercise_pages,
        due_date=a.due_date, created_at=a.created_at, concept_count=len(ids),
        concepts=[AssignmentConceptOut(id=i, name=names[i]) for i in ids if i in names] if with_concepts else [],
    )


# ---- teacher ---------------------------------------------------------------

@teacher_router.post("/exercise-proposal", response_model=ExerciseProposalOut)
def exercise_proposal(body: ExerciseProposalIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """The concepts an exercise seems to practise, to be edited by the teacher. Writes nothing."""
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
    # Students' doubt history outlives the assignment (done here, not left to the database, so SQLite tests agree with PostgreSQL).
    db.execute(update(Doubt).where(Doubt.assignment_id == assignment.id).values(assignment_id=None))
    db.execute(update(AssignmentCheck).where(AssignmentCheck.assignment_id == assignment.id).values(assignment_id=None))  # so is their check record
    db.execute(update(Quiz).where(Quiz.assignment_id == assignment.id).values(assignment_id=None))
    db.delete(assignment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- student ---------------------------------------------------------------

@student_router.get("", response_model=list[AssignmentOut])
def todays_work(student=Depends(require_student), db: Session = Depends(get_db)):
    return [_out(db, a, with_concepts=False) for a in service.list_student_assignments(db, student)]


@student_router.get("/{assignment_id}", response_model=AssignmentOut)
def my_assignment(assignment_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _out(db, service.get_student_assignment(db, student, assignment_id))
