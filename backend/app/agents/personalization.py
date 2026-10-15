"""Personalization Agent & Pre-Session Briefing (Phase 5 & 6 Steps 3 & 4).

Decided in Phase 5 & 6 (phase_5_6.md):
  * Context Assembly (`assemble_briefing_context`) fetches:
      (a) The last 3 teacher session logs (`session_logs`) for this student & teacher.
      (b) Current `weak` and `at_risk` concepts with their explainable reasons ("tested weak directly..." vs.
          "flagged because it depends on X, which tested weak").
      (c) Recent longitudinal trend trajectories (`improving` / `declining` / `stable`) from `trends.build_student_trends`.
  * Grounded Anti-Hallucination Generation (`generate_briefing`):
      Outputs a concise, plain-language JSON briefing (`last_covered`, `weak_areas`, `suggested_focus`, `focus_concepts`).
      Every concept in `focus_concepts` must belong to the student's allowed book concepts (no hallucinated concepts).
  * Real-Time Generation with Brief Cache (`get_or_generate_briefing`):
      Cached in-memory for `settings.briefing_cache_ttl_s` (300s = 5 minutes) keyed by `(teacher_id, student_id)` AND
      invalidated immediately if a new `MasteryEvent` or `SessionLog` is recorded."""
import logging
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.assessment import mastery, trends
from app.core.config import settings
from app.core.errors import ProcessingError
from app.llm import get_llm_provider
from app.models import (
    Book, Chapter, ChapterStatus, Concept, MasteryEvent, Page, SessionLog, User, student_book,
)
from app.teacher import sessions as session_service

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

SYSTEM = (
    "You are the Personalization Agent for a school tutoring platform. Before a tutoring session begins, you write a "
    "concise, plain-language pre-session briefing for the teacher based ONLY on the student's provided session logs, "
    "weak/at-risk concepts (with their explainable reasons), and recent mastery trends. "
    "Reply with JSON only: "
    '{"last_covered":str,"weak_areas":str,"suggested_focus":str,"focus_concepts":[str,...]}. '
    "Rules: "
    "(1) 'last_covered' (1-2 sentences, 15-450 chars): summarize what was covered in the recent session logs (or recent "
    "checks/quizzes if no session logs exist yet). "
    "(2) 'weak_areas' (1-3 sentences, 15-600 chars): explain what is currently weak or at risk AND WHY, preserving the "
    "exact distinction between concepts that tested weak directly vs. concepts flagged at risk because a prerequisite "
    "tested weak. If nothing is weak or at risk, state that clearly. "
    "(3) 'suggested_focus' (1-2 sentences, 15-450 chars): recommend a concrete focus for today's session (prioritizing "
    "foundational weak prerequisites before their downstream at-risk dependents). "
    "(4) 'focus_concepts' (list of 0 to 5 strings): exact concept names chosen ONLY from the ALLOWED_CONCEPT list in "
    "the prompt. NEVER invent or hallucinate a concept name that is not in ALLOWED_CONCEPT."
)


class PersonalizationError(ProcessingError):
    pass


class BriefingSchema(BaseModel):
    last_covered: str = Field(min_length=10, max_length=600)
    weak_areas: str = Field(min_length=10, max_length=800)
    suggested_focus: str = Field(min_length=10, max_length=600)
    focus_concepts: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("last_covered", "weak_areas", "suggested_focus")
    @classmethod
    def _clean_text(cls, value: str) -> str:
        cleaned = " ".join(value.split()).strip()
        if len(cleaned) < 10:
            raise ValueError("field must be a meaningful sentence (at least 10 characters)")
        return cleaned

    @field_validator("focus_concepts")
    @classmethod
    def _clean_concepts(cls, items: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for raw in items:
            c = " ".join((raw or "").split()).strip()
            if c and c.lower() not in seen:
                seen.add(c.lower())
                out.append(c)
        return out


@dataclass
class BriefingContext:
    student_id: uuid.UUID
    student_name: str
    recent_sessions: list[SessionLog] = field(default_factory=list)
    trends_report: Optional[trends.StudentTrendsReport] = None
    allowed_concepts: dict[str, str] = field(default_factory=dict)  # lowercase_name -> canonical Concept.name
    data_signature: str = ""


@dataclass
class BriefingResult:
    student_id: uuid.UUID
    student_name: str
    last_covered: str
    weak_areas: str
    suggested_focus: str
    focus_concepts: list[str]
    weak_count: int
    at_risk_count: int
    improving_count: int
    declining_count: int
    recent_session_count: int
    model: str
    generated_at: datetime
    cached: bool = False


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def _compute_data_signature(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID) -> str:
    """Lightweight signature of the student's mastery events and the teacher's session logs for this student."""
    ev_count, last_event_id = db.execute(
        select(func.count(MasteryEvent.id), func.max(MasteryEvent.id)).where(MasteryEvent.student_id == student_id)
    ).one()
    sess_count = db.scalar(
        select(func.count()).select_from(SessionLog).where(
            SessionLog.student_id == student_id, SessionLog.teacher_id == teacher_id
        )
    )
    last_session = db.execute(
        select(SessionLog.id, SessionLog.session_date, SessionLog.notes)
        .where(SessionLog.student_id == student_id, SessionLog.teacher_id == teacher_id)
        .order_by(SessionLog.session_date.desc(), SessionLog.created_at.desc())
        .limit(1)
    ).first()
    sess_part = f"{sess_count}:{last_session[0]}:{last_session[1].isoformat()}:{len(last_session[2])}" if last_session else "0:none"
    return f"ev:{ev_count}:{last_event_id or 0}|sess:{sess_part}"


def assemble_briefing_context(db: Session, teacher: User, student_id: uuid.UUID) -> BriefingContext:
    """Fetches (a) last 3 session logs, (b) weak & at_risk concepts with explainable reasons, (c) trend trajectories,
    and the student's allowed concept names from linked/visible books."""
    student = trends.ensure_teacher_can_access_student(db, teacher, student_id)
    recent_sessions = session_service.list_session_logs(db, teacher, student.id, limit=3)
    report = trends.build_student_trends(db, teacher, student.id)

    # Collect allowed concept names from:
    # 1. Concepts already present in the student's visible trends report
    allowed: dict[str, str] = {c.concept_name.lower(): c.concept_name for c in report.concepts if c.concept_name}

    # 2. Canonical concepts in ready chapters of books the student has linked AND the teacher can see
    linked_book_ids = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    book_concepts = db.scalars(
        select(Concept.name)
        .join(Page, Page.id == Concept.page_id)
        .join(Chapter, Chapter.id == Page.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(
            Chapter.book_id.in_(linked_book_ids),
            Chapter.status == ChapterStatus.READY,
            Concept.is_canonical.is_(True),
            or_(Book.is_reference.is_(True), Book.owner_teacher_id == teacher.id),
        )
        .order_by(Chapter.sequence_num, Page.page_number, Concept.position)
        .limit(200)
    ).all()
    for name in book_concepts:
        if name:
            cleaned = " ".join(name.split()).strip()
            allowed.setdefault(cleaned.lower(), cleaned)

    sig = _compute_data_signature(db, teacher.id, student.id)
    return BriefingContext(
        student_id=student.id,
        student_name=student.name,
        recent_sessions=recent_sessions,
        trends_report=report,
        allowed_concepts=allowed,
        data_signature=sig,
    )


def _build_user_prompt(ctx: BriefingContext) -> str:
    lines = [
        "PERSONALIZATION BRIEFING",
        f"STUDENT: {ctx.student_name}",
        "\nRECENT SESSION LOGS (newest first, up to 3):",
    ]
    if ctx.recent_sessions:
        for s in ctx.recent_sessions:
            tag_str = f" [tags: {', '.join(s.tags)}]" if s.tags else ""
            lines.append(f"- [{s.session_date.isoformat()}] {s.notes}{tag_str}")
    else:
        lines.append("- None recorded yet.")

    report = ctx.trends_report
    lines.append("\nCURRENT WEAK & AT-RISK CONCEPTS (with explainable reasons):")
    flagged = [c for c in (report.concepts if report else []) if c.status in (mastery.WEAK, mastery.AT_RISK)]
    if flagged:
        for c in flagged[:15]:
            score_str = f"score={c.current_score:.0%}, " if c.current_score is not None else ""
            lines.append(
                f"- {c.status.upper()}: {c.concept_name} ({score_str}trend={c.trend}, reason: {c.reason or 'n/a'})"
            )
    else:
        lines.append("- None currently flagged.")

    lines.append("\nRECENT MASTERY TRAJECTORIES (last 4 weeks):")
    if report and report.concepts:
        for c in report.concepts[:20]:
            curr_s = f"{c.current_score:.0%}" if c.current_score is not None else "n/a"
            base_s = f"{c.baseline_score:.0%}" if c.baseline_score is not None else "n/a"
            lines.append(
                f"- {c.concept_name} [{c.subject or 'Subject'} / {c.chapter_title or 'Chapter'}]: "
                f"status={c.status}, current={curr_s}, baseline={base_s}, trend={c.trend}"
            )
    else:
        lines.append("- No check or quiz history recorded yet.")

    lines.append("\nALLOWED_CONCEPT LIST (focus_concepts MUST be chosen ONLY from these exact names):")
    if ctx.allowed_concepts:
        for cname in list(ctx.allowed_concepts.values())[:60]:
            lines.append(f"ALLOWED_CONCEPT: {cname}")
    else:
        lines.append("ALLOWED_CONCEPT: (none — leave focus_concepts empty [])")

    return "\n".join(lines)


def generate_briefing(provider, ctx: BriefingContext) -> BriefingResult:
    """Calls `provider.complete_json`, validates schema AND verifies that `focus_concepts` contains zero hallucinated
    concepts outside `ctx.allowed_concepts`. Retries up to `MAX_RETRIES` times with an explicit correction prompt."""
    if provider is None:
        raise PersonalizationError("Couldn't generate the pre-session briefing right now. Please try again in a moment.")

    user_prompt = _build_user_prompt(ctx)
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user_prompt + (
            f"\n\nYour previous reply was invalid: {last_error}\n"
            "Return valid JSON only matching the schema, and ensure focus_concepts only uses names from ALLOWED_CONCEPT."
            if attempt
            else ""
        )
        try:
            raw = provider.complete_json(SYSTEM, prompt)
        except Exception as exc:
            raise PersonalizationError("Couldn't generate the pre-session briefing right now. Please try again in a moment.") from exc

        try:
            parsed = BriefingSchema.model_validate_json(_strip_fences(raw))
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue

        # Anti-hallucination check: every focus_concept must match a concept in ctx.allowed_concepts
        if not ctx.allowed_concepts:
            canonical_focus: list[str] = []
        else:
            unknown = [c for c in parsed.focus_concepts if c.lower() not in ctx.allowed_concepts]
            if unknown:
                last_error = (
                    f"focus_concepts contained unknown/hallucinated concept(s) {unknown}; "
                    f"choose ONLY from ALLOWED_CONCEPT: {list(ctx.allowed_concepts.values())[:15]}"
                )
                continue
            canonical_focus = [ctx.allowed_concepts[c.lower()] for c in parsed.focus_concepts]

        report = ctx.trends_report
        return BriefingResult(
            student_id=ctx.student_id,
            student_name=ctx.student_name,
            last_covered=parsed.last_covered,
            weak_areas=parsed.weak_areas,
            suggested_focus=parsed.suggested_focus,
            focus_concepts=canonical_focus,
            weak_count=report.weak_count if report else 0,
            at_risk_count=report.at_risk_count if report else 0,
            improving_count=report.improving_count if report else 0,
            declining_count=report.declining_count if report else 0,
            recent_session_count=len(ctx.recent_sessions),
            model=getattr(provider, "model_name", "") or settings.llm_model,
            generated_at=datetime.now(timezone.utc),
            cached=False,
        )

    raise PersonalizationError("Couldn't generate the pre-session briefing right now. Please try again in a moment.")


# ---- Step 4: Brief 5-minute TTL cache (never cached indefinitely) ---------------------------------------------

@dataclass
class _CacheEntry:
    result: BriefingResult
    signature: str
    expires_at: float


class BriefingCache:
    """Thread-safe short-lived TTL cache for pre-session briefings."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], _CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, teacher_id: uuid.UUID, student_id: uuid.UUID, signature: str, now_mono: Optional[float] = None) -> Optional[BriefingResult]:
        now = time.monotonic() if now_mono is None else now_mono
        key = (str(teacher_id), str(student_id))
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if now >= entry.expires_at or entry.signature != signature:
                self._entries.pop(key, None)
                return None
            # Return a shallow copy marked cached=True
            r = entry.result
            return BriefingResult(
                student_id=r.student_id,
                student_name=r.student_name,
                last_covered=r.last_covered,
                weak_areas=r.weak_areas,
                suggested_focus=r.suggested_focus,
                focus_concepts=list(r.focus_concepts),
                weak_count=r.weak_count,
                at_risk_count=r.at_risk_count,
                improving_count=r.improving_count,
                declining_count=r.declining_count,
                recent_session_count=r.recent_session_count,
                model=r.model,
                generated_at=r.generated_at,
                cached=True,
            )

    def put(self, teacher_id: uuid.UUID, student_id: uuid.UUID, signature: str, result: BriefingResult,
            ttl_s: Optional[int] = None, now_mono: Optional[float] = None) -> None:
        ttl = settings.briefing_cache_ttl_s if ttl_s is None else ttl_s
        if ttl <= 0:
            return
        now = time.monotonic() if now_mono is None else now_mono
        key = (str(teacher_id), str(student_id))
        with self._lock:
            self._entries[key] = _CacheEntry(result=result, signature=signature, expires_at=now + ttl)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


briefing_cache = BriefingCache()


def _llm():
    try:
        return get_llm_provider()
    except Exception:
        logger.warning("Personalization LLM provider could not start", exc_info=True)
        return None


def get_or_generate_briefing(
    db: Session,
    teacher: User,
    student_id: uuid.UUID,
    *,
    refresh: bool = False,
    now_mono: Optional[float] = None,
) -> tuple[BriefingResult, bool]:
    """Returns `(briefing_result, was_cached)`.
    Checks tenant access first (404 if not in teacher's room), then checks the 5-minute TTL cache (unless `refresh=True`
    or underlying session/mastery data changed), and otherwise invokes the Personalization Agent."""
    student = trends.ensure_teacher_can_access_student(db, teacher, student_id)
    sig = _compute_data_signature(db, teacher.id, student.id)
    if not refresh:
        cached = briefing_cache.get(teacher.id, student.id, sig, now_mono=now_mono)
        if cached is not None:
            return cached, True

    ctx = assemble_briefing_context(db, teacher, student.id)
    try:
        res = generate_briefing(_llm(), ctx)
    except PersonalizationError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    briefing_cache.put(teacher.id, student.id, ctx.data_signature, res, now_mono=now_mono)
    return res, False