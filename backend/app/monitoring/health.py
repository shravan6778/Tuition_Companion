"""Health checks behind /health/ready and the admin status page."""
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.metrics import metrics
from app.graph_store import get_graph_store
from app.models import AccountStatus, Chapter, ChapterStatus, IndexStatus, TeacherInvite, User
from app.pipeline.jobs import is_actively_processing
from app.usage import service as usage

logger = logging.getLogger(__name__)
_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="healthcheck")


def _timed(fn, timeout_s: float) -> dict:
    started = time.perf_counter()
    try:
        detail = _pool.submit(fn).result(timeout=timeout_s)
        return {"ok": True, "latency_ms": round((time.perf_counter() - started) * 1000), "detail": detail}
    except FutureTimeout:
        return {"ok": False, "latency_ms": None, "detail": f"no answer within {timeout_s:g}s"}
    except Exception as exc:  # the detail is for the administrator; no secrets are in these messages
        return {"ok": False, "latency_ms": round((time.perf_counter() - started) * 1000), "detail": f"{type(exc).__name__}: {str(exc)[:160]}"}


def check_database(db: Session) -> dict:
    started = time.perf_counter()
    try:
        db.execute(text("SELECT 1"))
        return {"ok": True, "latency_ms": round((time.perf_counter() - started) * 1000), "detail": None}
    except Exception as exc:
        return {"ok": False, "latency_ms": None, "detail": f"{type(exc).__name__}: {str(exc)[:160]}"}


def check_supertokens() -> dict:
    def ping():
        headers = {"api-key": settings.supertokens_api_key} if settings.supertokens_api_key else {}
        r = httpx.get(settings.supertokens_connection_uri.rstrip("/") + "/hello", headers=headers, timeout=3.0)
        if r.status_code != 200:
            raise RuntimeError(f"core answered HTTP {r.status_code}")
        return "core answers"
    return _timed(ping, 4.0)


def check_memgraph() -> dict:
    try:
        store = get_graph_store()
    except Exception as exc:
        return {"ok": False, "latency_ms": None, "detail": f"{type(exc).__name__}: {str(exc)[:160]}"}
    if store is None:
        return {"ok": None, "latency_ms": None, "detail": "switched off (GRAPH_STORE_PROVIDER=none)"}

    def ping():
        stats = store.stats() if hasattr(store, "stats") else {}
        return {"chapters": stats.get("Chapter"), "concepts": stats.get("Concept")} if isinstance(stats, dict) else None
    return _timed(ping, 4.0)


def chapter_health(db: Session) -> dict:
    failed = db.scalar(select(func.count(Chapter.id)).where(Chapter.status == ChapterStatus.FAILED)) or 0
    processing = db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.PROCESSING)).all()
    stuck = sum(1 for c in processing if not is_actively_processing(c))
    index_failed = db.scalar(select(func.count(Chapter.id)).where(
        (Chapter.embedding_status == IndexStatus.FAILED) | (Chapter.graph_sync_status == IndexStatus.FAILED))) or 0
    return {"failed": int(failed), "stuck": int(stuck), "processing": len(processing) - stuck, "search_index_failed": int(index_failed)}


def people_health(db: Session) -> dict:
    pending = db.scalar(select(func.count(User.id)).where(User.status == AccountStatus.PENDING)) or 0
    disabled = db.scalar(select(func.count(User.id)).where(User.status == AccountStatus.DISABLED)) or 0
    now = datetime.now(timezone.utc)
    open_invites = db.scalar(select(func.count(TeacherInvite.id)).where(
        TeacherInvite.used_at.is_(None), TeacherInvite.revoked_at.is_(None),
        (TeacherInvite.expires_at.is_(None)) | (TeacherInvite.expires_at > now))) or 0
    return {"pending_teachers": int(pending), "disabled_users": int(disabled), "open_invites": int(open_invites)}


def status_report(db: Session) -> dict:
    database = check_database(db)
    supertokens = check_supertokens()
    memgraph = check_memgraph()
    traffic = metrics.snapshot(settings.error_rate_window_min)
    components = {"database": database, "supertokens": supertokens, "memgraph": memgraph}
    if not database["ok"]:
        overall = "down"
    elif supertokens["ok"] is False or memgraph["ok"] is False or traffic["error_rate"] >= settings.error_rate_warn:
        overall = "degraded"
    else:
        overall = "ok"
    out = {
        "checked_at": datetime.now(timezone.utc),
        "overall": overall,
        "components": components,
        "traffic": {**traffic, "note": "this API process only; resets on restart"},
    }
    if database["ok"]:
        ks = usage.kill_switch_state(db, fresh=True)
        out["chapters"] = chapter_health(db)
        out["people"] = people_health(db)
        out["ai"] = {
            "kill_switch": {"engaged": ks.engaged, "source": ks.source, "reason": ks.reason, "since": ks.since, "by": ks.by},
            "llm_provider": settings.llm_provider,
            "ocr_provider": settings.ocr_provider,
            "embedding_provider": settings.embedding_provider,
            "speech_provider": settings.speech_provider,
            "llm_no_training_confirmed": settings.llm_no_training_confirmed,
            "metering_enabled": settings.usage_metering_enabled,
            "usage_today": {q: usage.used_today(db, q) for q in usage.QUOTAS},
        }
    out["monitoring"] = {
        "uptime_ping_configured": bool(settings.uptime_ping_url),
        "teacher_signup_mode": settings.teacher_signup_mode,
        "supertokens_api_key_set": bool(settings.supertokens_api_key),
    }
    return out


# ---- outbound heartbeat (dead-man's switch such as healthchecks.io) -----------------------------

_stop = threading.Event()
_thread: threading.Thread | None = None


def _heartbeat_loop() -> None:
    from app.db.session import SessionLocal
    while not _stop.wait(settings.uptime_ping_interval_s):
        db = SessionLocal()
        try:
            if not check_database(db)["ok"]:
                continue  # stay silent: the missing ping is the alarm
        finally:
            db.close()
        try:
            httpx.get(settings.uptime_ping_url, timeout=10.0)
        except Exception as exc:
            logger.warning("Uptime ping failed: %s", type(exc).__name__)


def start_heartbeat() -> None:
    global _thread
    if not settings.uptime_ping_url or (_thread and _thread.is_alive()):
        return
    _stop.clear()
    _thread = threading.Thread(target=_heartbeat_loop, name="uptime-heartbeat", daemon=True)
    _thread.start()
    logger.info("Uptime heartbeat started (every %ss)", settings.uptime_ping_interval_s)


def stop_heartbeat() -> None:
    _stop.set()
