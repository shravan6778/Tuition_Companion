"""Teacher invite codes: single use, optional expiry, only a SHA-256 hash is stored (the code is shown once)."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import TeacherInvite


def hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().encode("utf-8")).hexdigest()


def new_code() -> str:
    return secrets.token_urlsafe(9)  # 12 characters, 72 bits


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    return dt if dt is None or dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def invite_state(inv: TeacherInvite, now: Optional[datetime] = None) -> str:
    """'used' | 'revoked' | 'expired' | 'active'"""
    now = now or utcnow()
    if inv.used_at is not None:
        return "used"
    if inv.revoked_at is not None:
        return "revoked"
    if inv.expires_at is not None and _aware(inv.expires_at) <= now:
        return "expired"
    return "active"


def create_invite(db: Session, created_by_id, note: Optional[str], days: Optional[int]) -> tuple[str, TeacherInvite]:
    code = new_code()
    days = settings.teacher_invite_default_days if days is None else days
    inv = TeacherInvite(code_hash=hash_code(code), note=(note or "").strip()[:120] or None, created_by_id=created_by_id,
                        expires_at=(utcnow() + timedelta(days=days)) if days else None)
    db.add(inv)
    db.flush()
    return code, inv


def find_active(db: Session, code: str) -> Optional[TeacherInvite]:
    if not code or not code.strip():
        return None
    inv = db.scalar(select(TeacherInvite).where(TeacherInvite.code_hash == hash_code(code)))
    return inv if inv is not None and invite_state(inv) == "active" else None


def consume(db: Session, invite_id, user_id) -> bool:
    """Mark the invite used by this user. Atomic: of two people holding the same code, only one gets True."""
    now = utcnow()
    result = db.execute(
        update(TeacherInvite)
        .where(TeacherInvite.id == invite_id, TeacherInvite.used_at.is_(None), TeacherInvite.revoked_at.is_(None),
               (TeacherInvite.expires_at.is_(None)) | (TeacherInvite.expires_at > now))
        .values(used_at=now, used_by_id=user_id))
    return result.rowcount == 1
