"""POST /student/doubts: the doubt's retrieval step (Phase 3 step 2). Text only; no explanation is written yet."""
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assignments import service as assignments
from app.auth.dependencies import require_student
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.content_library.upload import read_validated_upload
from app.doubts import browse as browse_module, photo, service
from app.doubts.query import DOUBT, PAGE, RETAKE_MESSAGE, TOO_SHORT, classify_doubt_text
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE
from app.models import Doubt

router = APIRouter(prefix="/student/doubts", tags=["doubts"], dependencies=[Depends(require_student)])
EXCERPT_CHARS = 1500


class DoubtIn(BaseModel):
    text: str = Field(default="", max_length=1000)
    assignment_id: uuid.UUID | None = None  # none = a standalone doubt over all the student's linked books
    # The concept a student picked from a photographed whole page (step 4). The doubt text is then built from the concept
    # and `text` is ignored.
    concept_id: uuid.UUID | None = None
    # Standalone "Ask a Doubt" (step 7): narrow the search to one chapter of a linked book. Not combined with an assignment.
    chapter_id: uuid.UUID | None = None
    # Set for a follow-up such as "explain simpler"; it deliberately bypasses answer reuse.
    parent_doubt_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def has_a_doubt(self):
        if self.assignment_id is not None and self.chapter_id is not None:
            raise ValueError("Send an assignment or a chapter, not both")
        self.text = " ".join(self.text.split())
        if not self.text and self.concept_id is None:
            raise ValueError("Write your doubt first")
        return self


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
    chapter_id: uuid.UUID | None = None  # the chapter the student narrowed a standalone doubt to
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
    parent_doubt_id: uuid.UUID | None = None
    reused: bool = False
    reused_from_created_at: datetime | None = None


class DoubtHistoryOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID | None
    text: str
    status: str
    answer_status: str
    answer: str | None = None
    refresher: str | None = None
    parent_doubt_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    created_at: datetime


VERIFY_NOTE = "auto-generated, please verify"
ANSWER_MESSAGES = {
    "unanswered": "Your book has related pages, but they don't answer this directly. Have a look at them below, or ask your teacher.",
    "failed": "We found the right pages but couldn't write an explanation just now. Have a look at the pages below and try again in a little while.",
}


def _reused_out(doubt: Doubt) -> DoubtOut:
    """Return a cached answer without retrieval or an LLM call."""
    asked_on = doubt.created_at.strftime("%Y-%m-%d")
    return DoubtOut(
        id=doubt.id,
        assignment_id=doubt.assignment_id,
        chapter_id=doubt.chapter_id,
        status=doubt.status,
        message=f"You asked this on {asked_on}. Here is the saved answer.",
        confidence=round(doubt.confidence, 3),
        threshold=settings.retrieval_min_similarity,
        answer_status=doubt.answer_status,
        answer=doubt.answer,
        refresher=doubt.refresher,
        sources=[],
        needs_review=doubt.needs_review,
        note=VERIFY_NOTE if doubt.needs_review else None,
        parent_doubt_id=doubt.parent_doubt_id,
        reused=True,
        reused_from_created_at=doubt.created_at,
    )


def _out(outcome: service.DoubtOutcome, book_id: uuid.UUID | None) -> DoubtOut:
    doubt, result, answer = outcome.doubt, outcome.result, outcome.answer
    if outcome.chapter is not None:
        book_id = outcome.chapter.book_id
    message = ANSWER_MESSAGES.get(doubt.answer_status) or (service.CHAPTER_OUTSIDE if outcome.chapter is not None and result.status == OUTSIDE
                                                           else service.MESSAGES[result.status])
    request = None
    return DoubtOut(
        id=doubt.id, assignment_id=doubt.assignment_id, chapter_id=outcome.chapter.id if outcome.chapter is not None else None,
        status=result.status, message=message,
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
        parent_doubt_id=doubt.parent_doubt_id,
    )


@router.post("", response_model=DoubtOut)
def ask(body: DoubtIn, student=Depends(require_student), db: Session = Depends(get_db)):
    # The assignment is checked first (404 when it isn't this student's), so a probe can't use the rate limit to learn anything.
    assignment = assignments.get_student_assignment(db, student, body.assignment_id) if body.assignment_id else None
    chapter = None
    if body.chapter_id is not None:
        chapter = service.get_ready_chapter(db, student, body.chapter_id)
        if chapter is None:
            raise HTTPException(404, "Chapter not found")
    text = body.text
    if body.concept_id is not None:
        text = service.concept_doubt_text(db, student, body.concept_id)
        if text is None:
            raise HTTPException(404, "Concept not found")
    if body.parent_doubt_id is not None:
        parent = db.scalar(
            select(Doubt).where(Doubt.id == body.parent_doubt_id, Doubt.student_id == student.id)
        )
        if parent is None:
            raise HTTPException(404, "Parent doubt not found")
        # A follow-up must point at an answered doubt; otherwise there is nothing useful to explain differently.
        if parent.answer_status != "answered" or not parent.answer:
            raise HTTPException(409, "This doubt does not have an answer to explain differently")

    # Rate-limit every doubt request, including cache hits, so repeated cached
    # requests cannot bypass the endpoint abuse limit. A cache hit still avoids
    # retrieval and LLM work.
    limiter.check("doubt", str(student.id), settings.rate_doubts_per_hour, 3600)

    if body.parent_doubt_id is None:
        cached = service.find_reusable_answer(
            db,
            student,
            text,
            assignment_id=assignment.id if assignment else None,
            chapter_id=chapter.id if chapter else None,
        )
        if cached is not None:
            return _reused_out(cached)
    return _out(
        service.raise_doubt(db, student, text, assignment, chapter, parent_doubt_id=body.parent_doubt_id),
        (assignments.resolve_student_target(db, student, assignment)[0].id if assignment and assignments.resolve_student_target(db, student, assignment)[0] else None)
        if assignment else (chapter.book_id if chapter else None),
    )


class PickConceptOut(BaseModel):
    concept_id: uuid.UUID
    name: str
    description: str


class PickPageOut(BaseModel):
    page_id: str
    page_number: int
    chapter_id: str
    chapter_title: str
    book_id: str
    concepts: list[PickConceptOut]  # the student picks one, then POST /student/doubts {concept_id}


class DoubtPhotoOut(BaseModel):
    kind: str  # too_short | doubt | page | unavailable
    words: int = 0
    text_read: str = ""  # what the OCR read, so the student can see why it was (not) understood. The photo itself is not kept.
    message: str
    status: str | None = None  # for a whole page: the retrieval status (grounded | outside_assignment | not_in_book | unavailable)
    doubt: DoubtOut | None = None  # kind == doubt: handled exactly like a typed doubt
    page: PickPageOut | None = None  # kind == page and its page was found
    request_chapter: RequestChapterOut | None = None  # a page that is not in the book yet


PAGE_MESSAGE = "This looks like a whole page. Pick the idea that confused you."
UNREADABLE_MESSAGE = "We couldn't read that photo right now. Please try again in a little while."


@router.post("/photo", response_model=DoubtPhotoOut)
def ask_by_photo(file: UploadFile = File(...), assignment_id: uuid.UUID | None = Form(default=None),
                 chapter_id: uuid.UUID | None = Form(default=None), student=Depends(require_student), db: Session = Depends(get_db)):
    """A photographed doubt. Order matters: the assignment is checked first (404), then the file by CONTENT and size, then the
    per-student limits, and only then is one OCR call paid for. The photo is never stored."""
    if assignment_id is not None and chapter_id is not None:
        raise HTTPException(422, "Send an assignment or a chapter, not both")
    assignment = assignments.get_student_assignment(db, student, assignment_id) if assignment_id else None
    chapter = service.get_ready_chapter(db, student, chapter_id) if chapter_id else None
    if chapter_id and chapter is None:
        raise HTTPException(404, "Chapter not found")
    upload = read_validated_upload(file, settings.max_doubt_photo_mb, images_only=True)
    limiter.check("doubt_photo", str(student.id), settings.rate_doubt_photos_per_hour, 3600)
    try:
        text = photo.read_photo(upload.data, upload.ext)
    except photo.PhotoUnreadable:
        return DoubtPhotoOut(kind="unavailable", message=UNREADABLE_MESSAGE)
    q = classify_doubt_text(text, from_photo=True)
    shown = text[:300]
    if q.kind == TOO_SHORT:
        return DoubtPhotoOut(kind=TOO_SHORT, words=q.words, text_read=shown, message=RETAKE_MESSAGE)
    limiter.check("doubt", str(student.id), settings.rate_doubts_per_hour, 3600)
    book_id = (assignments.resolve_student_target(db, student, assignment)[0].id if assignment and assignments.resolve_student_target(db, student, assignment)[0] else None) if assignment else (chapter.book_id if chapter else None)
    if q.kind == DOUBT:
        cached = service.find_reusable_answer(
            db,
            student,
            q.text[: photo.TEXT_CAP],
            assignment_id=assignment.id if assignment else None,
            chapter_id=chapter.id if chapter else None,
        )
        if cached is not None:
            return DoubtPhotoOut(
                kind=DOUBT, words=q.words, text_read=shown,
                message="We found your saved answer for this question.",
                doubt=_reused_out(cached),
            )
        outcome = service.raise_doubt(db, student, q.text[: photo.TEXT_CAP], assignment, chapter)
        return DoubtPhotoOut(kind=DOUBT, words=q.words, text_read=shown, message="Here is what we found for your photo.",
                             doubt=_out(outcome, book_id))
    pick = photo.match_page(db, student, q.text, assignment, chapter)
    status = pick.result.status
    if pick.page_id is None or not pick.concepts:
        message = service.MESSAGES[status] if status != GROUNDED else service.MESSAGES["outside_assignment"]
        request = None
        return DoubtPhotoOut(kind=PAGE, words=q.words, text_read=shown, message=message, status=status if pick.page_id is None else "outside_assignment",
                             request_chapter=request)
    top = pick.result.pages[0]
    return DoubtPhotoOut(
        kind=PAGE, words=q.words, text_read=shown, message=PAGE_MESSAGE, status=GROUNDED,
        page=PickPageOut(page_id=top.page_id, page_number=top.page_number, chapter_id=top.chapter_id, chapter_title=top.chapter_title,
                         book_id=top.book_id, concepts=[PickConceptOut(concept_id=c.id, name=c.name, description=c.description or "") for c in pick.concepts]))


@router.get("", response_model=list[DoubtHistoryOut])
def my_doubts(assignment_id: uuid.UUID | None = None, student=Depends(require_student), db: Session = Depends(get_db)):
    """This student's own doubts, newest first (never anyone else's)."""
    query = select(Doubt).where(Doubt.student_id == student.id)
    if assignment_id is not None:
        query = query.where(Doubt.assignment_id == assignment_id)
    return [
        DoubtHistoryOut(
            id=d.id,
            assignment_id=d.assignment_id,
            chapter_id=d.chapter_id,
            text=d.text,
            status=d.status,
            answer_status=d.answer_status,
            answer=d.answer,
            refresher=d.refresher,
            parent_doubt_id=d.parent_doubt_id,
            created_at=d.created_at,
        )
        for d in db.scalars(query.order_by(Doubt.created_at.desc()).limit(50))
    ]


# ---- standalone "Ask a Doubt": what the student can browse (step 7) ------------------------------------------------

class BrowseChapterOut(BaseModel):
    id: uuid.UUID
    number: int
    title: str


class BrowseBookOut(BaseModel):
    id: uuid.UUID
    label: str
    chapters: list[BrowseChapterOut]  # ready chapters only; send one as POST /student/doubts {chapter_id}


class BrowseSubjectOut(BaseModel):
    subject: str
    books: list[BrowseBookOut]


@router.get("/browse", response_model=list[BrowseSubjectOut])
def browse(student=Depends(require_student), db: Session = Depends(get_db)):
    """Subject -> book -> chapter over every book this student has linked (ready chapters only). A doubt asked with no
    `chapter_id` searches all of these at once."""
    return [BrowseSubjectOut(subject=s.subject, books=[BrowseBookOut(id=b.id, label=b.label, chapters=[
        BrowseChapterOut(id=c.id, number=c.number, title=c.title) for c in b.chapters]) for b in s.books])
        for s in browse_module.browse(db, student)]
