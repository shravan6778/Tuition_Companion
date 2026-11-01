"""Manual (school homework) tasks: how a student shows the work and how the teacher judges it.

Rules.md requires every comprehension check to be grounded in a book. A manual task has no book, so it never gets an
AI-written check (`POST /student/assignments/{id}/complete` answers it here instead). Verification is human:

    1. the student sends a PHOTO of the work, or a SPOKEN answer (turned into text on their own device; the server only
       ever receives the text, so no audio is stored and no speech service is paid for)
    2. the teacher looks at it and gives a verdict: good | needs_work | redo, with an optional note
    3. `good` closes the task; the other two reopen it and the student may send new work. Every attempt is kept.

Nothing here calls a model, and nothing is written to the mastery log: the task has no concepts to measure.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assignments import service
from app.auth.dependencies import require_student, require_teacher
from app.content_library.upload import read_validated_upload
from app.core import storage
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models import Assignment, AssignmentLevel, ManualSubmission, SubmissionSource, User, Verdict

# What the student sees for a manual task. `todo` / `submitted` come from the submissions; the rest is the teacher's verdict.
TODO, SUBMITTED = "todo", "submitted"
STATES = (TODO, SUBMITTED, *Verdict.ALL)

_MEDIA = {"png": "image/png", "jpg": "image/jpeg"}
# Words shown to the student with each state (the UI adds nothing the server did not say)
MESSAGES = {
    TODO: "Send a photo of your work, or say your answer out loud.",
    SUBMITTED: "Sent. Your teacher will take a look.",
    Verdict.GOOD: "Your teacher marked this good.",
    Verdict.NEEDS_WORK: "Your teacher says this needs a bit more work. Have another go and send it again.",
    Verdict.REDO: "Your teacher asked you to redo this. Send your new work when it is ready.",
}


# ---- state ------------------------------------------------------------------------------------------------------------

def require_manual(assignment: Assignment) -> None:
    if assignment.level != AssignmentLevel.MANUAL:
        raise HTTPException(409, "Only homework tasks are handed in this way")


def _attempts(db: Session, assignment_id: uuid.UUID, student_id: uuid.UUID) -> list[ManualSubmission]:
    """This student's submissions on the task, oldest first."""
    return list(db.scalars(select(ManualSubmission).where(
        ManualSubmission.assignment_id == assignment_id, ManualSubmission.student_id == student_id
    ).order_by(ManualSubmission.created_at, ManualSubmission.id)))


def latest(db: Session, assignment_id: uuid.UUID, student_id: uuid.UUID) -> ManualSubmission | None:
    attempts = _attempts(db, assignment_id, student_id)
    return attempts[-1] if attempts else None


def state_of(last: ManualSubmission | None) -> str:
    """The newest attempt decides: no attempt -> todo; not yet judged -> submitted; judged -> the verdict."""
    if last is None:
        return TODO
    return last.verdict or SUBMITTED


def can_hand_in(state: str) -> bool:
    return state != Verdict.GOOD


def pending_review_count(db: Session, assignment: Assignment) -> int:
    """How many students' NEWEST attempt on this task still waits for the teacher."""
    newest: dict[uuid.UUID, ManualSubmission] = {}
    for sub in db.scalars(select(ManualSubmission).where(ManualSubmission.assignment_id == assignment.id)
                          .order_by(ManualSubmission.created_at, ManualSubmission.id)):
        newest[sub.student_id] = sub
    return sum(1 for sub in newest.values() if sub.verdict is None)


# ---- student side -----------------------------------------------------------------------------------------------------

def hand_in(db: Session, student: User, assignment: Assignment, source: str, text: str, photo: UploadFile | None) -> ManualSubmission:
    """Order matters, like every paid-or-stored upload here: the task (404) and its kind first, then the content of the
    file and its size, then the per-student limit, and only then is anything stored."""
    require_manual(assignment)
    text = " ".join((text or "").split())
    if len(text) > settings.manual_text_max_chars:
        raise HTTPException(422, f"Please keep it under {settings.manual_text_max_chars} characters")
    if not can_hand_in(state_of(latest(db, assignment.id, student.id))):
        raise HTTPException(409, "Your teacher already marked this good")

    photo_path = None
    if source == SubmissionSource.PHOTO:
        if photo is None:
            raise HTTPException(422, "Add a photo of your work")
        upload = read_validated_upload(photo, settings.max_manual_photo_mb, images_only=True)
        limiter.check("manual_submission", str(student.id), settings.rate_manual_submissions_per_hour, 3600)
        photo_path = storage.save_by_hash(upload.data, upload.sha256, upload.ext)
    elif source == SubmissionSource.VOICE:
        if photo is not None:
            raise HTTPException(422, "Send either a photo or a spoken answer, not both")
        if len(text.split()) < settings.manual_voice_min_words:
            raise HTTPException(422, "We didn't catch enough of that. Please say your answer again.")
        limiter.check("manual_submission", str(student.id), settings.rate_manual_submissions_per_hour, 3600)
    else:
        raise HTTPException(422, "Send a photo or a spoken answer")

    sub = ManualSubmission(assignment_id=assignment.id, student_id=student.id, source=source, photo_path=photo_path,
                           text=text or None, created_at=datetime.now(timezone.utc))
    db.add(sub); db.commit(); db.refresh(sub)
    return sub


def get_own_submission(db: Session, student: User, submission_id: uuid.UUID) -> ManualSubmission:
    found = db.scalar(select(ManualSubmission).where(ManualSubmission.id == submission_id, ManualSubmission.student_id == student.id))
    if found is None:
        raise HTTPException(404, "Submission not found")
    return found


# ---- teacher side -----------------------------------------------------------------------------------------------------

def get_teacher_submission(db: Session, teacher: User, submission_id: uuid.UUID) -> ManualSubmission:
    """Only the teacher who set the task can see its submissions."""
    found = db.scalar(select(ManualSubmission).join(Assignment, Assignment.id == ManualSubmission.assignment_id).where(
        ManualSubmission.id == submission_id, Assignment.teacher_id == teacher.id))
    if found is None:
        raise HTTPException(404, "Submission not found")
    return found


def review(db: Session, sub: ManualSubmission, verdict: str, feedback: str | None) -> ManualSubmission:
    """Give (or change) the verdict on a student's NEWEST attempt. An older attempt has been superseded, so judging it
    would leave the task in a state the student never saw."""
    newest = latest(db, sub.assignment_id, sub.student_id)
    if newest is None or newest.id != sub.id:
        raise HTTPException(409, "The student has sent newer work since. Review that one instead.")
    sub.verdict = verdict
    sub.feedback = (feedback or "").strip() or None
    sub.reviewed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(sub)
    return sub


# ---- shapes -----------------------------------------------------------------------------------------------------------

class SubmissionOut(BaseModel):
    id: uuid.UUID
    assignment_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str | None = None  # the teacher's list only
    source: str  # photo | voice
    has_photo: bool
    text: str | None
    created_at: datetime
    verdict: str | None
    feedback: str | None
    reviewed_at: datetime | None


class ManualCompletionOut(BaseModel):
    """What `POST /student/assignments/{id}/complete` returns for a manual task, in place of a check."""
    kind: str = "manual"
    assignment_id: uuid.UUID
    assignment_title: str
    state: str  # todo | submitted | good | needs_work | redo
    message: str
    can_submit: bool
    latest: SubmissionOut | None = None


def _out(sub: ManualSubmission, student_name: str | None = None) -> SubmissionOut:
    return SubmissionOut(id=sub.id, assignment_id=sub.assignment_id, student_id=sub.student_id, student_name=student_name,
                         source=sub.source, has_photo=sub.photo_path is not None, text=sub.text, created_at=sub.created_at,
                         verdict=sub.verdict, feedback=sub.feedback, reviewed_at=sub.reviewed_at)


def completion(db: Session, student: User, assignment: Assignment) -> ManualCompletionOut:
    """"Mark complete" on a manual task. It starts no check and calls no model: it reports where the work stands and
    whether the student can hand something in. Safe to call repeatedly."""
    last = latest(db, assignment.id, student.id)
    state = state_of(last)
    return ManualCompletionOut(assignment_id=assignment.id, assignment_title=assignment.title, state=state,
                               message=MESSAGES[state], can_submit=can_hand_in(state), latest=_out(last) if last else None)


def student_view(db: Session, student: User, assignment: Assignment) -> tuple[str, str | None]:
    """(state, the teacher's note on the newest attempt) for the student's task list."""
    last = latest(db, assignment.id, student.id)
    return state_of(last), (last.feedback if last else None)


# ---- routes -----------------------------------------------------------------------------------------------------------

student_router = APIRouter(prefix="/student", tags=["manual-tasks"], dependencies=[Depends(require_student)])
teacher_router = APIRouter(prefix="/teacher", tags=["manual-tasks"], dependencies=[Depends(require_teacher)])


class ReviewIn(BaseModel):
    verdict: str = Field(pattern="^(good|needs_work|redo)$")
    feedback: str | None = Field(default=None, max_length=1000)


def _photo_response(sub: ManualSubmission) -> Response:
    if sub.photo_path is None:
        raise HTTPException(404, "This submission has no photo")
    try:
        data = storage.read_file(sub.photo_path)
    except FileNotFoundError:
        raise HTTPException(404, "The photo is no longer available") from None
    ext = sub.photo_path.rsplit(".", 1)[-1]
    # a child's exercise book: never cached by a shared proxy, and never sniffed into something executable
    return Response(content=data, media_type=_MEDIA.get(ext, "application/octet-stream"),
                    headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})


@student_router.post("/assignments/{assignment_id}/submissions", response_model=SubmissionOut, status_code=201)
def hand_in_work(assignment_id: uuid.UUID, source: str = Form(...), text: str = Form(default=""),
                 photo: UploadFile | None = File(default=None), student=Depends(require_student), db: Session = Depends(get_db)):
    """Photo: `source=photo` + the image file (`photo`, optional `text` as a note). Voice: `source=voice` + `text`, the transcript
    the device made (the student can correct it before sending)."""
    assignment = service.get_student_assignment(db, student, assignment_id)
    return _out(hand_in(db, student, assignment, source, text, photo))


@student_router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def my_submissions(assignment_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    assignment = service.get_student_assignment(db, student, assignment_id)
    require_manual(assignment)
    return [_out(s) for s in reversed(_attempts(db, assignment.id, student.id))]


@student_router.get("/submissions/{submission_id}/photo")
def my_submission_photo(submission_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _photo_response(get_own_submission(db, student, submission_id))


@teacher_router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def assignment_submissions(assignment_id: uuid.UUID, student_id: uuid.UUID | None = None, teacher=Depends(require_teacher),
                           db: Session = Depends(get_db)):
    """Everything students handed in for this task, newest first. Needs the teacher who set it."""
    assignment = service.get_teacher_assignment(db, teacher, assignment_id)
    require_manual(assignment)
    query = select(ManualSubmission, User.name).join(User, User.id == ManualSubmission.student_id).where(
        ManualSubmission.assignment_id == assignment.id)
    if student_id is not None:
        query = query.where(ManualSubmission.student_id == student_id)
    rows = db.execute(query.order_by(ManualSubmission.created_at.desc(), ManualSubmission.id)).all()
    return [_out(sub, name) for sub, name in rows]


@teacher_router.get("/submissions/{submission_id}/photo")
def submission_photo(submission_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return _photo_response(get_teacher_submission(db, teacher, submission_id))


@teacher_router.post("/submissions/{submission_id}/review", response_model=SubmissionOut)
def review_submission(submission_id: uuid.UUID, body: ReviewIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    sub = review(db, get_teacher_submission(db, teacher, submission_id), body.verdict, body.feedback)
    return _out(sub, db.scalar(select(User.name).where(User.id == sub.student_id)))
