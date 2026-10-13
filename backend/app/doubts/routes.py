"""POST /student/doubts: the doubt's retrieval step (Phase 3 step 2). Text only; no explanation is written yet."""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assignments import service as assignments
from app.auth.dependencies import require_student
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.doubts import service
from app.doubts.retrieval import NOT_IN_BOOK
from app.models import Doubt

router = APIRouter(prefix="/student/doubts", tags=["doubts"], dependencies=[Depends(require_student)])
EXCERPT_CHARS = 1500


class DoubtIn(BaseModel):
    text: str = Field(max_length=1000)
    assignment_id: uuid.UUID | None = None  # none = a standalone doubt over all the student's linked books

    @field_validator("text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("Write your doubt first")
        return v


class PageOut(BaseModel):
    page_id: str
    page_number: int
    chapter_id: str
    chapter_title: str
    book_id: str
    similarity: float
    excerpt: str


class ConceptOut(BaseModel):
    concept_id: str
    name: str
    similarity: float


class PrerequisiteOut(BaseModel):
    concept_id: str
    name: str
    depth: int


class ElsewhereOut(BaseModel):
    concept_id: str
    name: str
    chapter_id: str
    book_id: str
    similarity: float


class RequestChapterOut(BaseModel):
    book_id: uuid.UUID
    path: str  # the existing chapter-request route to call


class SourceOut(BaseModel):
    page_number: int
    chapter_title: str


class DoubtOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    status: str  # grounded | outside_assignment | not_in_book | unavailable
    message: str
    confidence: float
    threshold: float
    pages: list[PageOut] = []
    concepts: list[ConceptOut] = []
    prerequisites: list[PrerequisiteOut] = []
    elsewhere: list[ElsewhereOut] = []
    request_chapter: RequestChapterOut | None = None  # only for not_in_book on an assignment's book
    # The Tutor's explanation (only ever for a grounded doubt). answer_status: none | answered | unanswered | failed
    answer_status: str = "none"
    answer: str | None = None
    refresher: str | None = None
    sources: list[SourceOut] = []  # the pages the explanation is built from
    needs_review: bool = False
    note: str | None = None  # "auto-generated, please verify" when retrieval confidence was low


class DoubtHistoryOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    text: str
    status: str
    created_at: datetime


VERIFY_NOTE = "auto-generated, please verify"
ANSWER_MESSAGES = {
    "unanswered": "Your book has related pages, but they don't answer this directly. Have a look at them below, or ask your teacher.",
    "failed": "We found the right pages but couldn't write an explanation just now. Have a look at the pages below and try again in a little while.",
}


def _out(outcome: service.DoubtOutcome, book_id: uuid.UUID | None) -> DoubtOut:
    doubt, result, answer = outcome.doubt, outcome.result, outcome.answer
    request = None
    if result.status == NOT_IN_BOOK and book_id is not None:
        request = RequestChapterOut(book_id=book_id, path=f"/student/books/{book_id}/chapter-requests")
    return DoubtOut(
        id=doubt.id, assignment_id=doubt.assignment_id, status=result.status, message=ANSWER_MESSAGES.get(doubt.answer_status) or service.MESSAGES[result.status],
        confidence=round(result.confidence, 3), threshold=result.threshold,
        pages=[PageOut(page_id=p.page_id, page_number=p.page_number, chapter_id=p.chapter_id, chapter_title=p.chapter_title,
                       book_id=p.book_id, similarity=round(p.similarity, 3), excerpt=" ".join(p.text.split())[:EXCERPT_CHARS])
               for p in result.pages],
        concepts=[ConceptOut(concept_id=c.concept_id, name=c.name, similarity=round(c.similarity, 3)) for c in result.concepts],
        prerequisites=[PrerequisiteOut(concept_id=p.concept_id, name=p.name, depth=p.depth) for p in result.prerequisites],
        elsewhere=[ElsewhereOut(concept_id=h.concept_id, name=h.name, chapter_id=h.chapter_id, book_id=h.book_id,
                                similarity=round(h.similarity, 3)) for h in result.elsewhere],
        request_chapter=request,
        answer_status=doubt.answer_status, answer=doubt.answer, refresher=doubt.refresher,
        sources=[SourceOut(page_number=p.page_number, chapter_title=p.chapter_title) for p in (answer.sources if answer else [])],
        needs_review=doubt.needs_review, note=VERIFY_NOTE if doubt.needs_review else None,
    )


@router.post("", response_model=DoubtOut)
def ask(body: DoubtIn, student=Depends(require_student), db: Session = Depends(get_db)):
    # The assignment is checked first (404 when it isn't this student's), so a probe can't use the rate limit to learn anything.
    assignment = assignments.get_student_assignment(db, student, body.assignment_id) if body.assignment_id else None
    limiter.check("doubt", str(student.id), settings.rate_doubts_per_hour, 3600)
    return _out(service.raise_doubt(db, student, body.text, assignment), assignment.book_id if assignment else None)


@router.get("", response_model=list[DoubtHistoryOut])
def my_doubts(assignment_id: uuid.UUID | None = None, student=Depends(require_student), db: Session = Depends(get_db)):
    """This student's own doubts, newest first (never anyone else's)."""
    query = select(Doubt).where(Doubt.student_id == student.id)
    if assignment_id is not None:
        query = query.where(Doubt.assignment_id == assignment_id)
    return [DoubtHistoryOut(id=d.id, assignment_id=d.assignment_id, text=d.text, status=d.status, created_at=d.created_at)
            for d in db.scalars(query.order_by(Doubt.created_at.desc()).limit(50))]
