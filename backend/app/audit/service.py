"""Write audit-log rows.

`record(db, ...)` only ADDS the row to the caller's session, so the log entry is committed (or rolled back) together
with the action it describes: there is never an action without its entry, nor an entry for an action that failed.
`record_now(...)` is for actions that have no transaction of their own to join (a failed login lock, a signup)."""
import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core import requestctx
from app.models import AuditLog, User

logger = logging.getLogger(__name__)


def _make(actor: Optional[User], action: str, target_type: Optional[str], target_id: Any,
          target_label: Optional[str], detail: Optional[dict]) -> AuditLog:
    ctx = requestctx.current()
    return AuditLog(
        actor_user_id=actor.id if actor is not None else None,
        actor_username=actor.username if actor is not None else None,
        actor_role=(getattr(actor.role, "value", actor.role) if actor is not None else None),
        action=action[:60],
        target_type=target_type,
        target_id=str(target_id)[:64] if target_id is not None else None,
        target_label=(target_label or None) and str(target_label)[:160],
        detail=detail or None,
        request_id=ctx.request_id if ctx.request_id != "-" else None,
    )


def record(db: Session, action: str, *, actor: Optional[User] = None, target_type: Optional[str] = None,
           target_id: Any = None, target_label: Optional[str] = None, detail: Optional[dict] = None) -> None:
    db.add(_make(actor, action, target_type, target_id, target_label, detail))


def record_now(action: str, *, actor: Optional[User] = None, target_type: Optional[str] = None, target_id: Any = None,
               target_label: Optional[str] = None, detail: Optional[dict] = None, session_factory=None) -> None:
    """Own session and commit. Never raises: an audit failure must not break the user's request."""
    try:
        if session_factory is None:
            from app.db.session import SessionLocal as session_factory
        db = session_factory()
        try:
            db.add(_make(actor, action, target_type, target_id, target_label, detail))
            db.commit()
        finally:
            db.close()
    except Exception:
        logger.exception("Could not write audit entry %s", action)
