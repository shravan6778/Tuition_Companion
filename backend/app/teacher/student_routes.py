"""Teacher-facing student analytics, session logs, and personalization briefing routes (Phase 5 & 6).

  Step 1: GET  /teacher/students/{student_id}/trends
  Step 2: POST /teacher/students/{student_id}/sessions
          GET  /teacher/students/{student_id}/sessions"""
import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.assessment import trends
from app.auth.dependencies import require_teacher
from app.db.session import get_db
from app.teacher import sessions as session_service

router = APIRouter(prefix="/teacher/students", tags=["teacher-students"], dependencies=[Depends(require_teacher)])


class WeeklyBucketOut(BaseModel):
    week_start: date
    week_end: date
    average_score: Optional[float] = None
    event_count: int


class ChapterTrendOut(BaseModel):
    chapter_id: uuid.UUID
    chapter_title: str
    subject: str
    book_id: uuid.UUID
    current_average: Optional[float] = None
    baseline_average: Optional[float] = None
    delta: Optional[float] = None
    trend: str  # improving | declining | stable | insufficient_data
    weeks: list[WeeklyBucketOut] = []


class SubjectTrendOut(BaseModel):
    subject: str
    current_average: Optional[float] = None
    baseline_average: Optional[float] = None
    delta: Optional[float] = None
    trend: str  # improving | declining | stable | insufficient_data
    weeks: list[WeeklyBucketOut] = []
    chapters: list[ChapterTrendOut] = []


class ConceptTrendOut(BaseModel):
    concept_id: uuid.UUID
    concept_name: str
    subject: Optional[str] = None
    chapter_id: Optional[uuid.UUID] = None
    chapter_title: Optional[str] = None
    status: str  # weak | at_risk | ok
    current_score: Optional[float] = None
    baseline_score: Optional[float] = None
    delta: Optional[float] = None
    trend: str  # improving | declining | stable | insufficient_data
    event_count: int
    last_checked: Optional[datetime] = None
    reason: Optional[str] = None
    flagged_by_concept_id: Optional[uuid.UUID] = None


class StudentTrendsOut(BaseModel):
    student_id: uuid.UUID
    student_name: str
    weeks_window: int
    weak_count: int
    at_risk_count: int
    ok_count: int
    improving_count: int
    declining_count: int
    stable_count: int
    subjects: list[SubjectTrendOut] = []
    concepts: list[ConceptTrendOut] = []


class SessionLogCreateIn(BaseModel):
    notes: str = Field(min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    session_date: Optional[date] = None


class SessionLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    teacher_id: uuid.UUID
    session_date: date
    notes: str
    tags: list[str] = []
    created_at: datetime


@router.get("/{student_id}/trends", response_model=StudentTrendsOut)
def get_student_trends(
    student_id: uuid.UUID,
    weeks: Optional[int] = Query(default=None, ge=1, le=12),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    report = trends.build_student_trends(db, teacher, student_id, weeks=weeks)
    return StudentTrendsOut(
        student_id=report.student_id,
        student_name=report.student_name,
        weeks_window=report.weeks_window,
        weak_count=report.weak_count,
        at_risk_count=report.at_risk_count,
        ok_count=report.ok_count,
        improving_count=report.improving_count,
        declining_count=report.declining_count,
        stable_count=report.stable_count,
        subjects=[
            SubjectTrendOut(
                subject=s.subject,
                current_average=s.current_average,
                baseline_average=s.baseline_average,
                delta=s.delta,
                trend=s.trend,
                weeks=[WeeklyBucketOut(**w.__dict__) for w in s.weeks],
                chapters=[
                    ChapterTrendOut(
                        chapter_id=ch.chapter_id,
                        chapter_title=ch.chapter_title,
                        subject=ch.subject,
                        book_id=ch.book_id,
                        current_average=ch.current_average,
                        baseline_average=ch.baseline_average,
                        delta=ch.delta,
                        trend=ch.trend,
                        weeks=[WeeklyBucketOut(**w.__dict__) for w in ch.weeks],
                    )
                    for ch in s.chapters
                ],
            )
            for s in report.subjects
        ],
        concepts=[ConceptTrendOut(**c.__dict__) for c in report.concepts],
    )


@router.post("/{student_id}/sessions", response_model=SessionLogOut, status_code=status.HTTP_201_CREATED)
def create_student_session_log(
    student_id: uuid.UUID,
    body: SessionLogCreateIn,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    entry = session_service.create_session_log(
        db,
        teacher,
        student_id,
        notes=body.notes,
        tags=body.tags,
        session_date=body.session_date,
    )
    return SessionLogOut.model_validate(entry)


@router.get("/{student_id}/sessions", response_model=list[SessionLogOut])
def list_student_session_logs(
    student_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    rows = session_service.list_session_logs(db, teacher, student_id, limit=limit)
    return [SessionLogOut.model_validate(r) for r in rows]