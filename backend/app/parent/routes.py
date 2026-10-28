import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.assessment import mastery
from app.auth.dependencies import require_parent
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models import MasteryEvent, ParentStudentLink, Role, Room, RoomMember, User
from app.models.links import ParentLinkStatus
from app.schemas import (
    ChildOut,
    LinkStudentIn,
    ParentChildProgressOut,
    ParentDigestOut,
    ParentRecentEventOut,
    ParentWeakAreaOut,
    RoomBrief,
)

router = APIRouter(prefix="/parent", tags=["parent"], dependencies=[Depends(require_parent)])


@router.get("/ping")
def ping(parent: User = Depends(require_parent)):
    return {"role": parent.role}


def _student_rooms(db: Session, student_id: uuid.UUID) -> list[RoomBrief]:
    rooms = db.scalars(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student_id)
        .order_by(Room.created_at)
    ).all()
    return [RoomBrief.model_validate(r) for r in rooms]


def _get_approved_child(db: Session, parent: User, child_id: uuid.UUID) -> User:
    """Verify the child is linked to this parent through ParentStudentLink AND approved, otherwise 404."""
    link = db.scalar(
        select(ParentStudentLink).where(
            ParentStudentLink.parent_id == parent.id,
            ParentStudentLink.student_id == child_id,
            ParentStudentLink.status == ParentLinkStatus.APPROVED,
        )
    )
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Child not found")
    child = db.get(User, child_id)
    if child is None or child.role != Role.student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Child not found")
    return child


@router.post("/children/link", response_model=ChildOut)
def link_child(
    body: LinkStudentIn,
    parent: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    limiter.check("parent_link", str(parent.id), settings.rate_parent_link_per_min, 60)
    code = body.link_code.strip().upper()
    student = db.scalar(select(User).where(User.link_code == code, User.role == Role.student))
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid student link code")

    existing = db.scalar(
        select(ParentStudentLink).where(
            ParentStudentLink.parent_id == parent.id,
            ParentStudentLink.student_id == student.id,
        )
    )
    if existing is None:
        existing = ParentStudentLink(
            parent_id=parent.id,
            student_id=student.id,
            status=ParentLinkStatus.PENDING,
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)

    rooms = _student_rooms(db, student.id) if existing.status == ParentLinkStatus.APPROVED else []
    return ChildOut(
        id=student.id,
        name=student.name,
        rooms=rooms,
        status=existing.status,
    )


@router.post("/link", response_model=ChildOut)
def legacy_link_child(
    body: LinkStudentIn,
    parent: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    """Backward-compatible Phase 1 endpoint. New clients should use /children/link, which creates a pending request.
    Existing clients/tests using /parent/link retain the original immediate-link behavior.
    """
    limiter.check("parent_link", str(parent.id), settings.rate_parent_link_per_min, 60)
    code = body.link_code.strip().upper()
    student = db.scalar(select(User).where(User.link_code == code, User.role == Role.student))
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid student link code")
    existing = db.scalar(select(ParentStudentLink).where(
        ParentStudentLink.parent_id == parent.id, ParentStudentLink.student_id == student.id
    ))
    if existing is None:
        existing = ParentStudentLink(
            parent_id=parent.id, student_id=student.id, status=ParentLinkStatus.APPROVED,
            approved_at=datetime.now(timezone.utc),
        )
        db.add(existing)
        db.commit()
        db.refresh(existing)
    elif existing.status != ParentLinkStatus.APPROVED:
        existing.status = ParentLinkStatus.APPROVED
        existing.approved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
    return ChildOut(id=student.id, name=student.name, rooms=_student_rooms(db, student.id), status=existing.status)


@router.get("/children", response_model=list[ChildOut])
def list_children(
    include_pending: bool = False,
    parent: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    query = (
        select(User, ParentStudentLink.status)
        .join(ParentStudentLink, ParentStudentLink.student_id == User.id)
        .where(ParentStudentLink.parent_id == parent.id)
    )
    if not include_pending:
        query = query.where(ParentStudentLink.status == ParentLinkStatus.APPROVED)
    rows = db.execute(query.order_by(ParentStudentLink.created_at)).all()
    return [
        ChildOut(
            id=u.id,
            name=u.name,
            rooms=_student_rooms(db, u.id) if st == ParentLinkStatus.APPROVED else [],
            status=st,
        )
        for u, st in rows
    ]


@router.get("/children/{child_id}/progress", response_model=ParentChildProgressOut)
def get_child_progress(
    child_id: uuid.UUID,
    days: int = Query(default=7, ge=1, le=90),
    parent: User = Depends(require_parent),
    db: Session = Depends(get_db),
):
    child = _get_approved_child(db, parent, child_id)

    states = list(mastery.current_state(db, child.id).values())
    order_map = {mastery.WEAK: 0, mastery.AT_RISK: 1, mastery.OK: 2}
    states.sort(key=lambda s: (order_map.get(s.status, 3), s.score if s.score is not None else 1.0, s.name))

    weak_count = sum(1 for s in states if s.status == mastery.WEAK)
    at_risk_count = sum(1 for s in states if s.status == mastery.AT_RISK)
    ok_count = sum(1 for s in states if s.status == mastery.OK)

    weak_areas = [
        ParentWeakAreaOut(
            concept_id=s.concept_id,
            concept_name=s.name,
            status=s.status,
            score=s.score,
            reason=s.reason,
            last_checked=s.last_checked,
        )
        for s in states
        if s.status in (mastery.WEAK, mastery.AT_RISK)
    ]

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    # Read the full requested window for the digest (no arbitrary 200-event cap), then keep
    # a small newest slice for the recent activity panel.
    window_events = list(
        db.scalars(
            select(MasteryEvent)
            .where(
                MasteryEvent.student_id == child.id,
                MasteryEvent.created_at >= cutoff,
            )
            .order_by(MasteryEvent.id.desc())
        )
    )
    all_events = list(
        db.scalars(
            select(MasteryEvent)
            .where(MasteryEvent.student_id == child.id)
            .order_by(MasteryEvent.id.desc())
            .limit(25)
        )
    )
    measured_window = [e for e in window_events if e.kind in mastery.MEASURED]

    concepts_covered = len({e.concept_id for e in measured_window if e.concept_id is not None})
    checks_taken = len(
        {e.check_id for e in measured_window if e.kind == mastery.CHECK and e.check_id is not None}
    ) or sum(1 for e in measured_window if e.kind == mastery.CHECK and e.check_id is None)
    quizzes_taken = len(
        {e.quiz_id for e in measured_window if e.kind == mastery.QUIZ and e.quiz_id is not None}
    ) or sum(1 for e in measured_window if e.kind == mastery.QUIZ and e.quiz_id is None)

    scores = [float(e.score) for e in measured_window if e.score is not None]
    pass_rate = (
        round(sum(1 for sc in scores if sc >= settings.weak_below) / len(scores), 4)
        if scores
        else None
    )

    flagged_this_week = len(
        {
            e.concept_id
            for e in window_events
            if e.concept_id is not None
            and (
                e.kind == mastery.PROPAGATED
                or (e.kind in mastery.MEASURED and e.score is not None and e.score < settings.weak_below)
            )
        }
    )

    recent = [
        ParentRecentEventOut(
            id=e.id,
            kind=e.kind,
            concept_id=e.concept_id,
            concept_name=e.concept_name,
            score=e.score,
            asked=e.asked,
            correct=e.correct,
            reason=e.reason,
            created_at=e.created_at,
        )
        for e in all_events[:25]
    ]

    return ParentChildProgressOut(
        digest=ParentDigestOut(
            concepts_covered=concepts_covered,
            checks_taken=checks_taken,
            quizzes_taken=quizzes_taken,
            pass_rate=pass_rate,
            flagged_this_week=flagged_this_week,
        ),
        weak=weak_count,
        at_risk=at_risk_count,
        ok=ok_count,
        weak_areas=weak_areas,
        recent=recent,
    )