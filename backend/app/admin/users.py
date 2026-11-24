"""Administrator actions on people: disable (and end their sessions), enable, approve or reject a teacher, set AI caps,
and delete a user together with their data.

Every action writes its audit-log row in the same transaction as the change itself."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import audit
from app.auth import st_admin
from app.auth.admin import is_admin
from app.content_library import deletion
from app.core.storage import delete_file
from app.models import (AccountStatus, Assignment, Book, Chapter, Doubt, ManualSubmission, MasteryEvent, Role, Room,
                        RoomMember, UploadDraft, User)
from app.usage import service as usage

logger = logging.getLogger(__name__)


def get_user_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


def _protect(actor: User, target: User, verb: str) -> None:
    if target.id == actor.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"You cannot {verb} your own account.")
    if is_admin(target):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"{target.username} is an administrator (ADMIN_USERNAMES). Remove them from that list first.")


def mask_phone(phone: str) -> str:
    if not phone:
        return ""
    return ("•" * (len(phone) - 4)) + phone[-4:] if len(phone) > 6 else "•" * len(phone)


def effective_caps(user: User) -> dict[str, int]:
    return {q: usage.cap_for(user, q) for q in usage.QUOTAS}


def to_out(user: User, used: Optional[dict[str, int]] = None):
    from app.admin.schemas import AdminUserOut
    return AdminUserOut(
        id=user.id, username=user.username, name=user.name, phone_masked=mask_phone(user.phone),
        role=getattr(user.role, "value", user.role), status=user.status, is_admin=is_admin(user),
        created_at=user.created_at, status_changed_at=user.status_changed_at,
        usage_today=used or {}, caps=effective_caps(user), quota_overrides=user.quota_overrides or None)


def _set_status(user: User, new: str) -> None:
    user.status = new
    user.status_changed_at = datetime.now(timezone.utc)


def disable(db: Session, actor: User, target: User, reason: Optional[str]) -> dict:
    _protect(actor, target, "disable")
    if target.status != AccountStatus.ACTIVE:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only an active account can be disabled." if target.status == AccountStatus.PENDING
                            else "This account is already disabled.")
    _set_status(target, AccountStatus.DISABLED)
    audit.record(db, "user.disable", actor=actor, target_type="user", target_id=target.id, target_label=target.username,
                 detail={"reason": reason} if reason else None)
    db.commit()  # from here on every request of theirs is refused (auth/dependencies.py), whatever their access token says
    return {"sessions_revoked": _revoke(target)}


def _revoke(target: User) -> bool:
    try:
        st_admin.revoke_sessions(target.supertokens_user_id)
        return True
    except Exception:
        logger.exception("Could not revoke the SuperTokens sessions of %s; the account is disabled all the same", target.username)
        return False


def enable(db: Session, actor: User, target: User) -> None:
    if target.status != AccountStatus.DISABLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "This account is not disabled.")
    _set_status(target, AccountStatus.ACTIVE)
    audit.record(db, "user.enable", actor=actor, target_type="user", target_id=target.id, target_label=target.username)
    db.commit()


def approve(db: Session, actor: User, target: User) -> None:
    if target.status != AccountStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "This account is not waiting for approval.")
    _set_status(target, AccountStatus.ACTIVE)
    audit.record(db, "user.approve", actor=actor, target_type="user", target_id=target.id, target_label=target.username,
                 detail={"role": getattr(target.role, "value", target.role)})
    db.commit()


def set_caps(db: Session, actor: User, target: User, caps: dict[str, Optional[int]]) -> None:
    unknown = set(caps) - set(usage.QUOTAS)
    if unknown:
        raise HTTPException(422, f"Unknown quota: {', '.join(sorted(unknown))}")
    if any(v is not None and v < 0 for v in caps.values()):
        raise HTTPException(422, "A cap cannot be negative (0 means unlimited).")
    merged = dict(target.quota_overrides or {})
    for quota, value in caps.items():
        if value is None:
            merged.pop(quota, None)
        else:
            merged[quota] = int(value)
    target.quota_overrides = merged or None  # reassigned, so SQLAlchemy sees the JSON change
    audit.record(db, "user.caps_set", actor=actor, target_type="user", target_id=target.id, target_label=target.username,
                 detail={"caps": caps})
    db.commit()


# ---- delete a user with their data ----------------------------------------------------------------

def delete_preview(db: Session, target: User) -> dict:
    def count(model, *where) -> int:
        return int(db.scalar(select(func.count()).select_from(model).where(*where)) or 0)

    books = db.scalars(select(Book.id).where(Book.owner_student_id == target.id)).all()
    return {
        "username": target.username,
        "role": getattr(target.role, "value", target.role),
        "own_books": len(books),
        "own_chapters": count(Chapter, Chapter.book_id.in_(books)) if books else 0,
        "rooms_owned": count(Room, Room.teacher_id == target.id),
        "room_memberships": count(RoomMember, RoomMember.user_id == target.id),
        "doubts": count(Doubt, Doubt.student_id == target.id),
        "mastery_records": count(MasteryEvent, MasteryEvent.student_id == target.id),
        "assignments_made": count(Assignment, Assignment.teacher_id == target.id),
    }


def _files_of(db: Session, target: User) -> set[str]:
    paths: set[str] = set(db.scalars(select(UploadDraft.source_file).where(UploadDraft.student_id == target.id)).all())
    paths.update(p for p in db.scalars(select(ManualSubmission.photo_path).where(ManualSubmission.student_id == target.id)).all() if p)
    paths.update(p for p in db.scalars(
        select(ManualSubmission.photo_path).join(Assignment, Assignment.id == ManualSubmission.assignment_id)
        .where(Assignment.teacher_id == target.id)).all() if p)
    return paths


def _remove_if_unreferenced(db: Session, paths: set[str]) -> None:
    for path in {p for p in paths if p}:
        used = (db.scalar(select(Book.id).where(Book.front_pages_file == path).limit(1))
                or db.scalar(select(Chapter.id).where(Chapter.source_file == path).limit(1))
                or db.scalar(select(UploadDraft.id).where(UploadDraft.source_file == path).limit(1))
                or db.scalar(select(ManualSubmission.id).where(ManualSubmission.photo_path == path).limit(1)))
        if not used:
            delete_file(path)


def delete_user_and_data(db: Session, actor: User, target: User, *, action: str = "user.delete", reason: Optional[str] = None) -> dict:
    """Disable, remove the student's books (rows, Memgraph copy, stored files), remove the login identity, then the
    user row; the database's ON DELETE CASCADE removes everything else that belongs to them (rooms, doubts, answers,
    mastery, links...). Safe to run again after a failure: it starts by disabling the account."""
    _protect(actor, target, "delete")
    preview = delete_preview(db, target)
    username, st_id, role = target.username, target.supertokens_user_id, getattr(target.role, "value", target.role)

    if target.status != AccountStatus.DISABLED:
        _set_status(target, AccountStatus.DISABLED)
        db.commit()
    _revoke(target)

    files = _files_of(db, target)
    for book in db.scalars(select(Book).where(Book.owner_student_id == target.id)).all():
        deletion.delete_book(db, book)  # 409 while a chapter is processing: the account stays disabled, try again later

    try:
        st_admin.delete_identity(st_id)
    except Exception as exc:
        logger.exception("Could not remove %s from SuperTokens", username)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY,
                            "The login service did not answer, so nothing more was deleted. The account is disabled; try again in a moment.") from exc

    user_id = target.id
    audit.record(db, action, actor=actor, target_type="user", target_id=user_id, target_label=username,
                 detail={"role": role, "removed": preview, **({"reason": reason} if reason else {})})
    db.execute(delete(UploadDraft).where(UploadDraft.student_id == user_id))
    db.delete(target)
    db.commit()
    _remove_if_unreferenced(db, files)
    return preview
