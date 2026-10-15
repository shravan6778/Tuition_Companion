"""Teacher session log service (Phase 5 & 6 Step 2).

  * Teachers record short post-session notes (free text + quick tags) against a student and date.
  * Strict tenant isolation: a teacher can only log or read sessions for a student who sits in one of
    that teacher's rooms (404 otherwise), and only sees their own session logs."""
import uuid
from datetime import date, datetime, timezone
from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment.trends import ensure_teacher_can_access_student
from app.models import SessionLog, User


def normalize_tags(tags: Optional[Sequence[str]]) -> list[str]:
    if not tags:
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in tags:
        t = " ".join((raw or "").split()).strip()
        if not t:
            continue
        if len(t) > 50:
            raise HTTPException(422, "Each tag must be at most 50 characters")
        key = t.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(t)
    if len(cleaned) > 20:
        raise HTTPException(422, "At most 20 tags are allowed per session log")
    return cleaned


def create_session_log(
    db: Session,
    teacher: User,
    student_id: uuid.UUID,
    notes: str,
    tags: Optional[Sequence[str]] = None,
    session_date: Optional[date] = None,
) -> SessionLog:
    student = ensure_teacher_can_access_student(db, teacher, student_id)
    cleaned_notes = " ".join((notes or "").split()).strip()
    if not cleaned_notes:
        raise HTTPException(422, "Session notes cannot be empty")
    if len(cleaned_notes) > 4000:
        raise HTTPException(422, "Session notes cannot exceed 4000 characters")

    cleaned_tags = normalize_tags(tags)
    eff_date = session_date or datetime.now(timezone.utc).date()

    entry = SessionLog(
        student_id=student.id,
        teacher_id=teacher.id,
        session_date=eff_date,
        notes=cleaned_notes,
        tags=cleaned_tags,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_session_logs(
    db: Session,
    teacher: User,
    student_id: uuid.UUID,
    limit: int = 50,
) -> list[SessionLog]:
    student = ensure_teacher_can_access_student(db, teacher, student_id)
    cap = max(1, min(100, limit))
    query = (
        select(SessionLog)
        .where(SessionLog.student_id == student.id, SessionLog.teacher_id == teacher.id)
        .order_by(SessionLog.session_date.desc(), SessionLog.created_at.desc())
        .limit(cap)
    )
    return list(db.scalars(query))