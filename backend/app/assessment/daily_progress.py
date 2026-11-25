"""Day-by-day progress for one student: what was assigned, what the student did, tests and results, doubts, session notes.

One builder serves every reader. The caller has already proved the reader may see this student:
  * teacher route -> `teacher_id` is set, so only that teacher's own work, tests and notes are shown;
  * (parent route, a later step) -> `teacher_id` stays None and `include_session_notes` is False.

Days are calendar days in `settings.usage_day_timezone`. Only days with something on them are returned, newest first.
No tables are added: every row below already exists.
"""
import uuid
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    Assignment, AssignmentCheck, Book, Chapter, Doubt, ManualSubmission, Quiz, RoomMember, SessionLog, User,
)

MAX_SPAN_DAYS = 92
DEFAULT_SPAN_DAYS = 14


class DayAssigned(BaseModel):
    assignment_id: uuid.UUID
    title: str
    subject: str
    chapter_title: Optional[str] = None
    level: str
    due_date: Optional[date] = None


class DayWork(BaseModel):
    kind: str  # check | homework
    assignment_id: Optional[uuid.UUID] = None
    title: str
    subject: Optional[str] = None
    score: Optional[float] = None  # 0..1, a finished check
    verdict: Optional[str] = None  # good | needs_work | redo, a reviewed homework hand-in (None = not reviewed yet)
    at: datetime


class DayTest(BaseModel):
    quiz_id: uuid.UUID
    title: str
    subject: Optional[str] = None
    kind: str  # teacher | practice
    score: Optional[float] = None  # 0..1
    at: datetime


class DayDoubt(BaseModel):
    text: str
    subject: Optional[str] = None
    at: datetime


class DaySession(BaseModel):
    notes: str
    tags: list[str] = []


class DayProgressOut(BaseModel):
    day: date
    subjects_worked: list[str] = []  # subjects the student actually did something in (not merely assigned)
    assigned: list[DayAssigned] = []
    worked: list[DayWork] = []
    tests: list[DayTest] = []
    doubts: list[DayDoubt] = []
    sessions: list[DaySession] = []
    average_test_score: Optional[float] = None


class DailyProgressOut(BaseModel):
    student_id: uuid.UUID
    student_name: str
    date_from: date
    date_to: date
    days_active: int
    checks_done: int
    tests_taken: int
    average_test_score: Optional[float] = None
    days: list[DayProgressOut] = []


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.usage_day_timezone)


def _local_day(ts: datetime) -> date:
    if ts.tzinfo is None:  # some databases hand timestamps back naive; ours are stored in UTC
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(_tz()).date()


def resolve_range(date_from: Optional[date], date_to: Optional[date]) -> tuple[date, date]:
    """Fills in defaults (the last 14 days) and rejects a backwards or over-long range with a ValueError."""
    end = date_to or datetime.now(_tz()).date()
    start = date_from or end - timedelta(days=DEFAULT_SPAN_DAYS - 1)
    if start > end:
        raise ValueError("The start date must not be after the end date")
    if (end - start).days + 1 > MAX_SPAN_DAYS:
        raise ValueError(f"Pick at most {MAX_SPAN_DAYS} days at a time")
    return start, end


def _avg(values: list[Optional[float]]) -> Optional[float]:
    vals = [v for v in values if v is not None]
    return sum(vals) / len(vals) if vals else None


def build_daily_progress(
    db: Session,
    student: User,
    date_from: date,
    date_to: date,
    teacher_id: Optional[uuid.UUID] = None,
    include_session_notes: bool = False,
) -> DailyProgressOut:
    tz = _tz()
    start = datetime.combine(date_from, time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(date_to + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc)

    def in_range(col):
        return and_(col >= start, col < end)

    my_rooms = select(RoomMember.room_id).where(RoomMember.user_id == student.id)
    mine = or_(Assignment.student_id == student.id, Assignment.room_id.in_(my_rooms))
    if teacher_id is not None:
        mine = and_(mine, Assignment.teacher_id == teacher_id)
    visible_assignment_ids = select(Assignment.id).where(mine)

    days: dict[date, DayProgressOut] = {}

    def day(d: date) -> DayProgressOut:
        if d not in days:
            days[d] = DayProgressOut(day=d)
        return days[d]

    subjects_by_day: dict[date, set[str]] = defaultdict(set)

    # ---- assigned that day ----
    for a in db.scalars(select(Assignment).where(mine, in_range(Assignment.created_at)).order_by(Assignment.created_at)):
        day(_local_day(a.created_at)).assigned.append(DayAssigned(
            assignment_id=a.id, title=a.title, subject=a.subject, chapter_title=a.chapter_title, level=a.level, due_date=a.due_date,
        ))

    # ---- finished checks ----
    checks = db.scalars(
        select(AssignmentCheck)
        .where(AssignmentCheck.student_id == student.id, AssignmentCheck.submitted_at.is_not(None),
               in_range(AssignmentCheck.submitted_at),
               *([AssignmentCheck.assignment_id.in_(visible_assignment_ids)] if teacher_id is not None else []))
        .order_by(AssignmentCheck.submitted_at)
    ).all()
    for c in checks:
        d = _local_day(c.submitted_at)
        day(d).worked.append(DayWork(kind="check", assignment_id=c.assignment_id, title=c.assignment_title, subject=c.subject,
                                     score=c.score, at=c.submitted_at))
        if c.subject:
            subjects_by_day[d].add(c.subject)

    # ---- homework hand-ins (school tasks verified by a photo / spoken answer) ----
    subs = db.execute(
        select(ManualSubmission, Assignment)
        .join(Assignment, Assignment.id == ManualSubmission.assignment_id)
        .where(ManualSubmission.student_id == student.id, in_range(ManualSubmission.created_at), Assignment.id.in_(visible_assignment_ids))
        .order_by(ManualSubmission.created_at)
    ).all()
    for s, a in subs:
        d = _local_day(s.created_at)
        day(d).worked.append(DayWork(kind="homework", assignment_id=a.id, title=a.title, subject=a.subject, verdict=s.verdict, at=s.created_at))
        subjects_by_day[d].add(a.subject)

    # ---- tests (teacher tests and the student's own practice) ----
    quiz_filter = [Quiz.student_id == student.id, Quiz.submitted_at.is_not(None), in_range(Quiz.submitted_at)]
    if teacher_id is not None:
        quiz_filter.append(or_(Quiz.kind == "practice", Quiz.teacher_id == teacher_id))
    for q, subject in db.execute(select(Quiz, Book.subject).join(Book, Book.id == Quiz.book_id).where(*quiz_filter).order_by(Quiz.submitted_at)).all():
        d = _local_day(q.submitted_at)
        day(d).tests.append(DayTest(quiz_id=q.id, title=q.title, subject=subject, kind=q.kind, score=q.score, at=q.submitted_at))
        if subject:
            subjects_by_day[d].add(subject)

    # ---- doubts the student asked ----
    doubt_filter = [Doubt.student_id == student.id, in_range(Doubt.created_at)]
    if teacher_id is not None:
        doubt_filter.append(or_(Doubt.assignment_id.is_(None), Doubt.assignment_id.in_(visible_assignment_ids)))
    doubts = db.scalars(select(Doubt).where(*doubt_filter).order_by(Doubt.created_at)).all()
    assignment_subject = {a_id: subj for a_id, subj in db.execute(
        select(Assignment.id, Assignment.subject).where(Assignment.id.in_([x.assignment_id for x in doubts if x.assignment_id])))} if doubts else {}
    chapter_subject = {c_id: subj for c_id, subj in db.execute(
        select(Chapter.id, Book.subject).join(Book, Book.id == Chapter.book_id).where(Chapter.id.in_([x.chapter_id for x in doubts if x.chapter_id])))} if doubts else {}
    for x in doubts:
        subject = assignment_subject.get(x.assignment_id) or chapter_subject.get(x.chapter_id)
        d = _local_day(x.created_at)
        day(d).doubts.append(DayDoubt(text=x.text[:200], subject=subject, at=x.created_at))
        if subject:
            subjects_by_day[d].add(subject)

    # ---- the teacher's session notes (never shown to a parent) ----
    if include_session_notes and teacher_id is not None:
        for sl in db.scalars(select(SessionLog).where(
                SessionLog.student_id == student.id, SessionLog.teacher_id == teacher_id,
                SessionLog.session_date >= date_from, SessionLog.session_date <= date_to).order_by(SessionLog.created_at)):
            day(sl.session_date).sessions.append(DaySession(notes=sl.notes, tags=list(sl.tags or [])))

    ordered = sorted(days.values(), key=lambda x: x.day, reverse=True)
    for dp in ordered:
        dp.subjects_worked = sorted(subjects_by_day.get(dp.day, set()))
        dp.average_test_score = _avg([t.score for t in dp.tests])

    all_tests = [t for dp in ordered for t in dp.tests]
    return DailyProgressOut(
        student_id=student.id,
        student_name=student.name,
        date_from=date_from,
        date_to=date_to,
        days_active=len(ordered),
        checks_done=sum(1 for dp in ordered for w in dp.worked if w.kind == "check"),
        tests_taken=len(all_tests),
        average_test_score=_avg([t.score for t in all_tests]),
        days=ordered,
    )
