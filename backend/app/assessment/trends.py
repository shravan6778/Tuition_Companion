"""Longitudinal Progress Tracking & Trend Analytics (Phase 5 & 6 Step 1).

Decided in Phase 5 & 6 (phase_5_6.md):
  * `GET /teacher/students/{id}/trends` serves longitudinal mastery data for a student in the teacher's room(s).
  * Weekly buckets: aggregated weekly averages of measured (`check` / `quiz`) mastery scores per subject and chapter
    for the last `settings.trend_weeks` (4) weeks.
  * Concept trajectory ("improving" / "declining" / "stable" / "insufficient_data"): compares the current rolling
    window against the student's earlier baseline (or earliest measured scores when all events sit inside one month):
      - delta >= +0.10 -> "improving"
      - delta <= -0.10 -> "declining"
      - |delta| < 0.10 -> "stable"
      - < 2 measured events -> "insufficient_data"
  * Includes explainable weak and at_risk flags (every flagged concept states its direct or propagated reason)."""
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.assessment import mastery
from app.core.config import settings
from app.models import Book, Chapter, Concept, MasteryEvent, Page, Room, RoomMember, User

IMPROVING = "improving"
DECLINING = "declining"
STABLE = "stable"
INSUFFICIENT_DATA = "insufficient_data"
TREND_DELTA_THRESHOLD = 0.10  # >= +10% improving, <= -10% declining


def ensure_teacher_can_access_student(db: Session, teacher: User, student_id: uuid.UUID) -> User:
    """Enforces tenant isolation: the student must sit in at least one room owned by `teacher` (404 otherwise)."""
    in_room = db.scalar(
        select(RoomMember.id)
        .join(Room, Room.id == RoomMember.room_id)
        .where(RoomMember.user_id == student_id, Room.teacher_id == teacher.id)
    )
    if in_room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    student = db.get(User, student_id)
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Student not found")
    return student


@dataclass
class WeeklyBucket:
    week_start: date
    week_end: date
    average_score: Optional[float]
    event_count: int


@dataclass
class ChapterTrend:
    chapter_id: uuid.UUID
    chapter_title: str
    subject: str
    book_id: uuid.UUID
    current_average: Optional[float]
    baseline_average: Optional[float]
    delta: Optional[float]
    trend: str  # improving | declining | stable | insufficient_data
    weeks: list[WeeklyBucket] = field(default_factory=list)


@dataclass
class SubjectTrend:
    subject: str
    current_average: Optional[float]
    baseline_average: Optional[float]
    delta: Optional[float]
    trend: str  # improving | declining | stable | insufficient_data
    weeks: list[WeeklyBucket] = field(default_factory=list)
    chapters: list[ChapterTrend] = field(default_factory=list)


@dataclass
class ConceptTrendItem:
    concept_id: uuid.UUID
    concept_name: str
    subject: Optional[str]
    chapter_id: Optional[uuid.UUID]
    chapter_title: Optional[str]
    status: str  # weak | at_risk | ok
    current_score: Optional[float]  # 3-event rolling score
    baseline_score: Optional[float]
    delta: Optional[float]
    trend: str  # improving | declining | stable | insufficient_data
    event_count: int
    last_checked: Optional[datetime]
    reason: Optional[str] = None
    flagged_by_concept_id: Optional[uuid.UUID] = None


@dataclass
class StudentTrendsReport:
    student_id: uuid.UUID
    student_name: str
    weeks_window: int
    weak_count: int
    at_risk_count: int
    ok_count: int
    improving_count: int
    declining_count: int
    stable_count: int
    subjects: list[SubjectTrend] = field(default_factory=list)
    concepts: list[ConceptTrendItem] = field(default_factory=list)


def _as_utc_date(dt: datetime, fallback: date) -> date:
    if dt is None:
        return fallback
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).date()
    return dt.date()


def classify_delta(current: Optional[float], baseline: Optional[float], event_count: int) -> tuple[Optional[float], str]:
    if current is None or baseline is None or event_count < 2:
        return None, INSUFFICIENT_DATA
    delta = round(current - baseline, 4)
    if delta >= TREND_DELTA_THRESHOLD:
        return delta, IMPROVING
    if delta <= -TREND_DELTA_THRESHOLD:
        return delta, DECLINING
    return delta, STABLE


def compute_concept_trajectory(
    scores_with_dates: list[tuple[date, float]],
    reference_date: date,
) -> tuple[Optional[float], Optional[float], Optional[float], str]:
    """Given a chronological list of `(event_date, score)` for a concept, returns:
    `(current_rolling_score, baseline_score, delta, trend)`.

    Baseline rules:
      1. If there are fewer than 2 measured events, baseline is None and trend is `insufficient_data`.
      2. If events exist prior to the recent 14-day window (the previous month's baseline), baseline is the average of
         those earlier events.
      3. Otherwise (all events occurred recently), baseline is the average of the events preceding the latest rolling
         half (or the first event(s) before the most recent event), allowing multi-attempt trajectories within a month
         to be classified accurately."""
    if not scores_with_dates:
        return None, None, None, INSUFFICIENT_DATA
    scores = [sc for _, sc in scores_with_dates]
    current = mastery.rolling_score(scores)
    if len(scores) < 2:
        return current, None, None, INSUFFICIENT_DATA

    cutoff_recent = reference_date - timedelta(days=14)
    older_scores = [sc for dt, sc in scores_with_dates[:-1] if dt <= cutoff_recent]
    if older_scores:
        baseline = round(sum(older_scores) / len(older_scores), 4)
    else:
        # Compare the current rolling window against the earlier attempts
        window = settings.mastery_rolling_window
        if len(scores) > window:
            earlier = scores[:-window]
        else:
            earlier = scores[:-1]
        baseline = round(sum(earlier) / len(earlier), 4)

    delta, trend = classify_delta(current, baseline, len(scores))
    return current, baseline, delta, trend


def _build_week_ranges(reference_date: date, num_weeks: int) -> list[tuple[date, date]]:
    """Returns `num_weeks` contiguous 7-day `(start_date, end_date)` buckets ending on `reference_date`, oldest first."""
    ranges: list[tuple[date, date]] = []
    for i in range(num_weeks - 1, -1, -1):
        end_d = reference_date - timedelta(days=i * 7)
        start_d = end_d - timedelta(days=6)
        ranges.append((start_d, end_d))
    return ranges


def _weekly_buckets(
    dated_scores: list[tuple[date, float]],
    week_ranges: list[tuple[date, date]],
) -> tuple[list[WeeklyBucket], Optional[float], Optional[float], Optional[float], str]:
    buckets: list[WeeklyBucket] = []
    for start_d, end_d in week_ranges:
        in_week = [sc for dt, sc in dated_scores if start_d <= dt <= end_d]
        avg = round(sum(in_week) / len(in_week), 4) if in_week else None
        buckets.append(WeeklyBucket(week_start=start_d, week_end=end_d, average_score=avg, event_count=len(in_week)))

    if not dated_scores:
        return buckets, None, None, None, INSUFFICIENT_DATA

    non_empty_buckets = [b for b in buckets if b.average_score is not None]
    all_scores = [sc for _, sc in dated_scores]
    current_avg = non_empty_buckets[-1].average_score if non_empty_buckets else round(sum(all_scores[-3:]) / len(all_scores[-3:]), 4)

    # Baseline: earlier weekly buckets (or events older than the latest bucket start)
    latest_bucket_start = non_empty_buckets[-1].week_start if non_empty_buckets else week_ranges[-1][0]
    older_scores = [sc for dt, sc in dated_scores if dt < latest_bucket_start]
    if older_scores:
        baseline_avg = round(sum(older_scores) / len(older_scores), 4)
    elif len(all_scores) >= 2:
        baseline_avg = round(sum(all_scores[:-1]) / len(all_scores[:-1]), 4)
    else:
        baseline_avg = None

    delta, trend = classify_delta(current_avg, baseline_avg, len(all_scores))
    return buckets, current_avg, baseline_avg, delta, trend


def build_student_trends(
    db: Session,
    teacher: User,
    student_id: uuid.UUID,
    *,
    weeks: Optional[int] = None,
    reference_date: Optional[date] = None,
) -> StudentTrendsReport:
    student = ensure_teacher_can_access_student(db, teacher, student_id)
    num_weeks = max(1, min(12, weeks or settings.trend_weeks))
    ref_date = reference_date or datetime.now(timezone.utc).date()
    week_ranges = _build_week_ranges(ref_date, num_weeks)

    # Load all measured + propagated events for this student in chronological order
    events = list(
        db.scalars(
            select(MasteryEvent)
            .where(
                MasteryEvent.student_id == student.id,
                MasteryEvent.kind.in_([mastery.CHECK, mastery.QUIZ, mastery.PROPAGATED]),
                MasteryEvent.concept_id.is_not(None),
            )
            .order_by(MasteryEvent.id)
        )
    )
    concept_ids = list(dict.fromkeys(e.concept_id for e in events if e.concept_id is not None))

    # Map concept_id -> (Concept, Chapter, Book) restricted to books visible to this teacher (official or owned by teacher)
    meta_map: dict[uuid.UUID, tuple[Concept, Chapter, Book]] = {}
    if concept_ids:
        rows = db.execute(
            select(Concept, Chapter, Book)
            .join(Page, Page.id == Concept.page_id)
            .join(Chapter, Chapter.id == Page.chapter_id)
            .join(Book, Book.id == Chapter.book_id)
            .where(
                Concept.id.in_(concept_ids),
                or_(Book.is_reference.is_(True), Book.owner_student_id == student.id),
            )
        ).all()
        for c, ch, bk in rows:
            meta_map[c.id] = (c, ch, bk)

    # Filter to concepts the teacher is permitted to see (or concepts whose book is official/the student's own)
    visible_cids = [cid for cid in concept_ids if cid in meta_map]
    states = mastery.current_state(db, student.id, visible_cids)

    # Group measured events by concept, chapter, and subject
    by_concept: dict[uuid.UUID, list[tuple[date, float]]] = {cid: [] for cid in visible_cids}
    by_chapter: dict[uuid.UUID, list[tuple[date, float]]] = {}
    by_subject: dict[str, list[tuple[date, float]]] = {}
    chapter_info: dict[uuid.UUID, tuple[str, str, uuid.UUID, int]] = {}  # ch_id -> (title, subject, book_id, seq)

    for e in events:
        if e.concept_id not in meta_map or e.kind not in mastery.MEASURED or e.score is None:
            continue
        _, ch, bk = meta_map[e.concept_id]
        ev_date = _as_utc_date(e.created_at, ref_date)
        score = float(e.score)
        subj = (bk.subject or "General").strip()

        by_concept.setdefault(e.concept_id, []).append((ev_date, score))
        by_chapter.setdefault(ch.id, []).append((ev_date, score))
        by_subject.setdefault(subj, []).append((ev_date, score))
        chapter_info[ch.id] = (ch.title or "Chapter", subj, bk.id, ch.sequence_num or 0)

    # Build per-concept trend items
    concept_items: list[ConceptTrendItem] = []
    for cid in visible_cids:
        st = states.get(cid)
        if st is None:
            continue
        _, ch, bk = meta_map[cid]
        subj = (bk.subject or "General").strip()
        dated = by_concept.get(cid, [])
        curr, base, delta, tr = compute_concept_trajectory(dated, ref_date)
        concept_items.append(
            ConceptTrendItem(
                concept_id=cid,
                concept_name=st.name,
                subject=subj,
                chapter_id=ch.id,
                chapter_title=ch.title,
                status=st.status,
                current_score=st.score if st.score is not None else curr,
                baseline_score=base,
                delta=delta,
                trend=tr,
                event_count=len(dated),
                last_checked=st.last_checked,
                reason=st.reason,
                flagged_by_concept_id=st.flagged_by,
            )
        )

    order_map = {mastery.WEAK: 0, mastery.AT_RISK: 1, mastery.OK: 2}
    concept_items.sort(
        key=lambda x: (order_map.get(x.status, 3), x.current_score if x.current_score is not None else 1.0, x.concept_name)
    )

    # Build subject and chapter weekly trend breakdowns
    subjects_out: list[SubjectTrend] = []
    for subj in sorted(by_subject):
        s_buckets, s_curr, s_base, s_delta, s_trend = _weekly_buckets(by_subject[subj], week_ranges)
        ch_ids = [
            chid for chid, info in sorted(chapter_info.items(), key=lambda kv: (kv[1][3], kv[1][0])) if info[1] == subj
        ]
        ch_trends: list[ChapterTrend] = []
        for chid in ch_ids:
            ch_title, _, bk_id, _ = chapter_info[chid]
            c_buckets, c_curr, c_base, c_delta, c_trend = _weekly_buckets(by_chapter.get(chid, []), week_ranges)
            ch_trends.append(
                ChapterTrend(
                    chapter_id=chid,
                    chapter_title=ch_title,
                    subject=subj,
                    book_id=bk_id,
                    current_average=c_curr,
                    baseline_average=c_base,
                    delta=c_delta,
                    trend=c_trend,
                    weeks=c_buckets,
                )
            )
        subjects_out.append(
            SubjectTrend(
                subject=subj,
                current_average=s_curr,
                baseline_average=s_base,
                delta=s_delta,
                trend=s_trend,
                weeks=s_buckets,
                chapters=ch_trends,
            )
        )

    return StudentTrendsReport(
        student_id=student.id,
        student_name=student.name,
        weeks_window=num_weeks,
        weak_count=sum(1 for c in concept_items if c.status == mastery.WEAK),
        at_risk_count=sum(1 for c in concept_items if c.status == mastery.AT_RISK),
        ok_count=sum(1 for c in concept_items if c.status == mastery.OK),
        improving_count=sum(1 for c in concept_items if c.trend == IMPROVING),
        declining_count=sum(1 for c in concept_items if c.trend == DECLINING),
        stable_count=sum(1 for c in concept_items if c.trend == STABLE),
        subjects=subjects_out,
        concepts=concept_items,
    )