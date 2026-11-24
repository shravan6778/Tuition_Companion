"""Metering and limits for every AI call that spends a free-tier or paid quota.

  * `check_allowed(quota, ...)` runs BEFORE a call: AI kill switch, the user's daily cap, the global daily cap.
  * `record(...)` runs AFTER it: one usage_events row (provider, operation, tokens or pages, user).
Both use their own short database session, never the request's, so a metering problem can not roll back or commit
anything of the request. If the database can not be reached they let the call through and log the problem (the same
outage would stop the request anyway); that is the one place this module fails open on purpose.

The user comes from core/requestctx.py (set by get_current_user, or by `acting_as` in background jobs)."""
import logging
import math
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import requestctx
from app.core.config import settings
from app.core.errors import QuotaExceededError
from app.models import AppSetting, Role, UsageEvent, User

logger = logging.getLogger(__name__)

# quota -> (unit type, label shown to people)
QUOTAS: dict[str, tuple[str, str]] = {
    "llm_tokens": ("tokens", "AI answers and question writing"),
    "ocr_pages": ("pages", "reading uploaded pages and photos"),
    "embedding_tokens": ("tokens", "searching your books"),
    "speech_calls": ("calls", "voice answers"),
}
KILL_SWITCH_KEY = "ai_kill_switch"

_session_factory_override = None  # tests point this at their own database


def set_session_factory(factory) -> None:
    global _session_factory_override
    _session_factory_override = factory


@contextmanager
def _session() -> Iterator[Session]:
    if _session_factory_override is not None:
        factory = _session_factory_override
    else:
        from app.db.session import SessionLocal as factory
    db = factory()
    try:
        yield db
    finally:
        db.close()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _tz() -> ZoneInfo | timezone:
    try:
        return ZoneInfo(settings.usage_day_timezone)
    except Exception:
        return timezone.utc


def day_start(now: Optional[datetime] = None) -> datetime:
    """Start of the current usage day (local midnight in USAGE_DAY_TIMEZONE) as a UTC time."""
    local = (now or utcnow()).astimezone(_tz())
    return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def seconds_until_reset(now: Optional[datetime] = None) -> int:
    start = day_start(now)
    local_next = (start.astimezone(_tz()) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((local_next - (now or utcnow())).total_seconds()))


def estimate_tokens(*texts: str) -> int:
    """Rough token count for a provider that reports none: ~3 characters per token (safe for Hindi and Telugu too)."""
    return max(1, math.ceil(sum(len(t or "") for t in texts) / 3))


# ---- caps -------------------------------------------------------------------

def default_cap(quota: str, role: Role | str | None) -> int:
    base = int(getattr(settings, f"usage_cap_{quota}"))
    if base and (getattr(role, "value", role) == Role.teacher.value):
        base = int(base * settings.usage_teacher_multiplier)
    return base


def cap_for(user: Optional[User], quota: str) -> int:
    """The user's daily cap for a quota; 0 = unlimited. A per-user override beats the defaults."""
    if user is None:
        return 0
    overrides = user.quota_overrides or {}
    if quota in overrides and overrides[quota] is not None:
        return max(0, int(overrides[quota]))
    return default_cap(quota, user.role)


def global_cap(quota: str) -> int:
    return int(getattr(settings, f"usage_global_cap_{quota}"))


def used_today(db: Session, quota: str, user_id: Optional[uuid.UUID] = None, now: Optional[datetime] = None) -> int:
    q = select(func.coalesce(func.sum(UsageEvent.units), 0)).where(
        UsageEvent.quota == quota, UsageEvent.status == "ok", UsageEvent.created_at >= day_start(now))
    if user_id is not None:
        q = q.where(UsageEvent.user_id == user_id)
    return int(db.scalar(q) or 0)


# ---- kill switch ---------------------------------------------------------------

@dataclass(frozen=True)
class KillSwitch:
    engaged: bool
    source: Optional[str] = None  # "env" | "admin"
    reason: Optional[str] = None
    since: Optional[str] = None
    by: Optional[str] = None


_ks_lock = threading.Lock()
_ks_cache: tuple[float, KillSwitch] | None = None
_KS_TTL_S = 5.0  # other API processes notice a flip within this long


def _read_kill_switch(db: Session) -> KillSwitch:
    if settings.ai_kill_switch:
        return KillSwitch(True, "env", "AI_KILL_SWITCH is set in the server settings")
    row = db.get(AppSetting, KILL_SWITCH_KEY)
    value = (row.value or {}) if row else {}
    if value.get("engaged"):
        return KillSwitch(True, "admin", value.get("reason"), value.get("at"), value.get("by"))
    return KillSwitch(False)


def kill_switch_state(db: Optional[Session] = None, *, fresh: bool = False) -> KillSwitch:
    global _ks_cache
    if settings.ai_kill_switch:
        return KillSwitch(True, "env", "AI_KILL_SWITCH is set in the server settings")
    with _ks_lock:
        if not fresh and _ks_cache and time.monotonic() - _ks_cache[0] < _KS_TTL_S:
            return _ks_cache[1]
    if db is not None:
        state = _read_kill_switch(db)
    else:
        with _session() as own:
            state = _read_kill_switch(own)
    with _ks_lock:
        _ks_cache = (time.monotonic(), state)
    return state


def forget_cached_kill_switch() -> None:
    global _ks_cache
    with _ks_lock:
        _ks_cache = None


def set_kill_switch(db: Session, engaged: bool, reason: Optional[str], by: str) -> KillSwitch:
    """Writes the switch in the caller's transaction (the caller commits, together with its audit row)."""
    value = {"engaged": bool(engaged), "reason": (reason or "")[:200] or None, "at": utcnow().isoformat(), "by": by}
    row = db.get(AppSetting, KILL_SWITCH_KEY)
    if row is None:
        db.add(AppSetting(key=KILL_SWITCH_KEY, value=value, updated_by=by))
    else:
        row.value = value
        row.updated_by = by
    forget_cached_kill_switch()
    return KillSwitch(bool(engaged), "admin" if engaged else None, value["reason"], value["at"], by)


# ---- before / after an AI call --------------------------------------------------------

def check_allowed(quota: str, *, provider: str, operation: str, needed: int = 0,
                  error_cls: type[QuotaExceededError] = QuotaExceededError) -> None:
    """Raise `error_cls` (a QuotaExceededError) if this call must not be made. `needed` is the call's expected size
    in the quota's unit; the call is refused when it would not fit into what is left of today's cap."""
    if not settings.usage_metering_enabled:
        return
    ctx = requestctx.current()
    user_id = uuid.UUID(ctx.user_id) if ctx.user_id else None
    label = QUOTAS[quota][1]
    problem: Optional[tuple[str, str, Optional[int]]] = None
    try:
        with _session() as db:
            if kill_switch_state(db).engaged:
                problem = ("kill_switch", "AI features are paused by the administrator for now. Please try again later.", None)
            else:
                user = db.get(User, user_id) if user_id else None
                cap = cap_for(user, quota)
                if cap:
                    used = used_today(db, quota, user_id)
                    # One oversized FIRST request of the day is still allowed; otherwise it could never succeed.
                    if used + needed > cap and not (used == 0 and needed > cap):
                        problem = ("user_cap", f"You have reached today's limit for {label}. It resets at midnight.", seconds_until_reset())
                gcap = global_cap(quota)
                if problem is None and gcap and used_today(db, quota) + needed > gcap:
                    problem = ("global_cap", f"The app has reached its daily limit for {label}. Please try again tomorrow.", seconds_until_reset())
    except Exception:
        logger.exception("Usage check failed; letting the call through")
        return
    if problem:
        kind, message, retry = problem
        record(quota=quota, provider=provider, operation=operation, units=0, status="blocked", user_id=user_id)
        logger.warning("AI call refused (%s) quota=%s operation=%s", kind, quota, operation)
        raise error_cls(message, kind=kind, retry_after=retry)


def record(*, quota: str, provider: str, operation: str, units: int, status: str = "ok",
           estimated: bool = False, user_id=None) -> None:
    if not settings.usage_metering_enabled:
        return
    ctx = requestctx.current()
    if user_id is None and ctx.user_id:
        user_id = uuid.UUID(ctx.user_id)
    try:
        with _session() as db:
            db.add(UsageEvent(
                user_id=user_id, provider=provider[:40], operation=operation[:60], quota=quota,
                units=max(0, int(units)), unit_type=QUOTAS[quota][0], estimated=estimated, status=status,
                request_id=(ctx.request_id if ctx.request_id != "-" else None), created_at=utcnow()))
            db.commit()
    except Exception:
        logger.exception("Could not record usage (%s, %s, %s units)", provider, operation, units)


# ---- numbers for the admin pages ----------------------------------------------------------

def usage_today_by_user(db: Session, user_ids: list[uuid.UUID]) -> dict[uuid.UUID, dict[str, int]]:
    if not user_ids:
        return {}
    rows = db.execute(
        select(UsageEvent.user_id, UsageEvent.quota, func.sum(UsageEvent.units))
        .where(UsageEvent.user_id.in_(user_ids), UsageEvent.status == "ok", UsageEvent.created_at >= day_start())
        .group_by(UsageEvent.user_id, UsageEvent.quota)).all()
    out: dict[uuid.UUID, dict[str, int]] = {}
    for uid, quota, total in rows:
        out.setdefault(uid, {})[quota] = int(total or 0)
    return out


def usage_overview(db: Session, days: int = 7) -> dict:
    start = day_start()
    totals = {q: used_today(db, q) for q in QUOTAS}
    blocked = db.scalar(select(func.count(UsageEvent.id)).where(UsageEvent.status == "blocked", UsageEvent.created_at >= start)) or 0
    errors = db.scalar(select(func.count(UsageEvent.id)).where(UsageEvent.status == "error", UsageEvent.created_at >= start)) or 0
    by_provider = db.execute(
        select(UsageEvent.provider, UsageEvent.quota, func.sum(UsageEvent.units), func.count(UsageEvent.id))
        .where(UsageEvent.status == "ok", UsageEvent.created_at >= start)
        .group_by(UsageEvent.provider, UsageEvent.quota)).all()
    top = db.execute(
        select(User.id, User.username, User.name, User.role, UsageEvent.quota, func.sum(UsageEvent.units))
        .join(User, User.id == UsageEvent.user_id)
        .where(UsageEvent.status == "ok", UsageEvent.created_at >= start)
        .group_by(User.id, User.username, User.name, User.role, UsageEvent.quota)).all()
    per_user: dict[uuid.UUID, dict] = {}
    for uid, username, name, role, quota, total in top:
        row = per_user.setdefault(uid, {"user_id": uid, "username": username, "name": name, "role": getattr(role, "value", role), "used": {}})
        row["used"][quota] = int(total or 0)
    ranked = sorted(per_user.values(), key=lambda r: -sum(r["used"].values()))[:15]
    history_start = day_start() - timedelta(days=max(1, days) - 1)
    hist_rows = db.execute(
        select(UsageEvent.created_at, UsageEvent.quota, UsageEvent.units)
        .where(UsageEvent.status == "ok", UsageEvent.created_at >= history_start)).all()
    tz = _tz()
    daily: dict[str, dict[str, int]] = {}
    for created, quota, units in hist_rows:
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        key = created.astimezone(tz).date().isoformat()
        daily.setdefault(key, {})[quota] = daily.setdefault(key, {}).get(quota, 0) + int(units)
    return {
        "day_starts_at": start,
        "resets_in_seconds": seconds_until_reset(),
        "totals_today": totals,
        "global_caps": {q: global_cap(q) for q in QUOTAS},
        "default_caps": {"student_parent": {q: default_cap(q, Role.student) for q in QUOTAS},
                         "teacher": {q: default_cap(q, Role.teacher) for q in QUOTAS}},
        "blocked_today": int(blocked),
        "errors_today": int(errors),
        "by_provider": [{"provider": p, "quota": q, "units": int(u or 0), "calls": int(c)} for p, q, u, c in by_provider],
        "top_users": ranked,
        "daily": [{"date": d, **v} for d, v in sorted(daily.items())],
    }
