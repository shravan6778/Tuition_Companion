"""The administrator area (who is an administrator: ADMIN_USERNAMES).

  * Official books: delete a book or chapter of the shared library. Students remove their own books themselves
    (DELETE /student/books/{id}).
  * People: list, disable (ends their sessions), enable, approve or reject a teacher, delete a user with their data.
  * Failed chapters: list them and retry.
  * AI usage: today's totals, per-user caps, the global kill switch.
  * Teacher invites, the audit log, and the status page.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app import audit
from app.admin import users as people
from app.admin.schemas import (AdminUserList, AdminUserOut, AuditList, AuditOut, CapsIn, DeleteUserIn, FailedChapterOut,
                               InviteCreatedOut, InviteIn, InviteOut, KillSwitchIn, ReasonIn)
from app.auth import invites
from app.auth.admin import is_admin, require_admin
from app.content_library import deletion
from app.core.config import settings
from app.db.session import get_db, get_session_factory
from app.models import AccountStatus, AuditLog, Book, Chapter, ChapterStatus, Role, TeacherInvite, User
from app.monitoring import health
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job
from app.usage import service as usage

router = APIRouter(prefix="/admin", tags=["admin"])


def _official_book(db: Session, book_id: uuid.UUID) -> Book:
    book = db.get(Book, book_id)
    if book is None or not book.is_reference:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Official book not found")
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_book(book_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    book = _official_book(db, book_id)
    # The audit row is added first and committed by delete_book's own commit: both happen, or neither.
    audit.record(db, "book.delete_official", actor=admin, target_type="book", target_id=book.id,
                 target_label=f"{book.class_name} {book.subject} ({book.publisher})", detail={"chapters": len(book.chapters)})
    deletion.delete_book(db, book)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_official_chapter(book_id: uuid.UUID, chapter_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    book = _official_book(db, book_id)
    chapter = db.get(Chapter, chapter_id)
    if chapter is None or chapter.book_id != book.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    audit.record(db, "chapter.delete_official", actor=admin, target_type="chapter", target_id=chapter.id,
                 target_label=chapter.title, detail={"book_id": str(book.id)})
    deletion.delete_chapter(db, chapter)
    return Response(status_code=status.HTTP_204_NO_CONTENT)



# ---- people ----------------------------------------------------------------------------------------

@router.get("/users", response_model=AdminUserList)
def list_users(
    q: Optional[str] = Query(default=None, max_length=60),
    role: Optional[Role] = None,
    account_status: Optional[Literal["active", "pending", "disabled"]] = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    cond = []
    if q:
        like = f"%{q.strip().lower()}%"
        cond.append(or_(func.lower(User.username).like(like), func.lower(User.name).like(like)))
    if role:
        cond.append(User.role == role)
    if account_status:
        cond.append(User.status == account_status)
    total = db.scalar(select(func.count(User.id)).where(*cond)) or 0
    rows = db.scalars(select(User).where(*cond).order_by(User.created_at.desc(), User.username).limit(limit).offset(offset)).all()
    used = usage.usage_today_by_user(db, [u.id for u in rows])
    return AdminUserList(total=total, items=[people.to_out(u, used.get(u.id)) for u in rows])


@router.post("/users/{user_id}/disable")
def disable_user(user_id: uuid.UUID, body: ReasonIn = ReasonIn(), admin=Depends(require_admin), db: Session = Depends(get_db)):
    target = people.get_user_or_404(db, user_id)
    result = people.disable(db, admin, target, body.reason)
    return {"user": people.to_out(target), **result}


@router.post("/users/{user_id}/enable", response_model=AdminUserOut)
def enable_user(user_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    target = people.get_user_or_404(db, user_id)
    people.enable(db, admin, target)
    return people.to_out(target)


@router.post("/users/{user_id}/approve", response_model=AdminUserOut)
def approve_user(user_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    target = people.get_user_or_404(db, user_id)
    people.approve(db, admin, target)
    return people.to_out(target)


@router.post("/users/{user_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_user(user_id: uuid.UUID, body: ReasonIn = ReasonIn(), admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Turn down a teacher who is waiting for approval: the account and its login are removed."""
    target = people.get_user_or_404(db, user_id)
    if target.status != AccountStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only an account waiting for approval can be rejected.")
    people.delete_user_and_data(db, admin, target, action="user.reject", reason=body.reason)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/{user_id}/caps", response_model=AdminUserOut)
def set_user_caps(user_id: uuid.UUID, body: CapsIn, admin=Depends(require_admin), db: Session = Depends(get_db)):
    target = people.get_user_or_404(db, user_id)
    people.set_caps(db, admin, target, body.caps)
    return people.to_out(target, usage.usage_today_by_user(db, [target.id]).get(target.id))


@router.get("/users/{user_id}/delete-preview")
def user_delete_preview(user_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    return people.delete_preview(db, people.get_user_or_404(db, user_id))


@router.delete("/users/{user_id}")
def delete_user(user_id: uuid.UUID, body: DeleteUserIn, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Delete a user and everything that belongs to them. The typed username must match."""
    target = people.get_user_or_404(db, user_id)
    if body.confirm_username.strip() != target.username:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Typed username does not match")
    return {"deleted": True, "removed": people.delete_user_and_data(db, admin, target, reason=body.reason)}


# ---- failed chapters ----------------------------------------------------------------------------------

def _stuck_cutoff() -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=settings.chapter_processing_timeout_min)


@router.get("/chapters/failed", response_model=list[FailedChapterOut])
def failed_chapters(limit: int = Query(default=100, ge=1, le=500), admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Chapters whose last run failed, plus ones stuck in 'processing' past the timeout (e.g. the server restarted)."""
    rows = db.execute(
        select(Chapter, Book, User)
        .join(Book, Book.id == Chapter.book_id)
        .outerjoin(User, User.id == Book.owner_student_id)
        .where(or_(Chapter.status == ChapterStatus.FAILED,
                   (Chapter.status == ChapterStatus.PROCESSING)
                   & (Chapter.processing_started_at.is_(None) | (Chapter.processing_started_at < _stuck_cutoff()))))
        .order_by(Chapter.processing_started_at.desc().nullslast(), Chapter.title).limit(limit)).all()
    out = []
    for chapter, book, owner in rows:
        out.append(FailedChapterOut(
            id=chapter.id, title=chapter.title, state="failed" if chapter.status == ChapterStatus.FAILED else "stuck",
            error_message=chapter.error_message, book_id=book.id,
            book_label=f"{book.class_name} {book.subject}" + (f" ({book.publisher})" if book.publisher else ""),
            is_reference=bool(book.is_reference), owner_username=owner.username if owner else None,
            owner_name=owner.name if owner else None, processing_started_at=chapter.processing_started_at,
            can_retry=bool(chapter.source_file)))
    return out


@router.post("/chapters/{chapter_id}/retry", status_code=status.HTTP_202_ACCEPTED)
def retry_failed_chapter(chapter_id: uuid.UUID, background_tasks: BackgroundTasks, admin=Depends(require_admin),
                         db: Session = Depends(get_db), session_factory=Depends(get_session_factory)):
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed.")
    if chapter.status not in (ChapterStatus.FAILED, ChapterStatus.PROCESSING) or not chapter.source_file:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nothing to retry: the chapter did not fail, or its uploaded file is gone. Ask the owner to upload it again.")
    book = db.get(Book, chapter.book_id)
    # The retry's AI use is counted against the student who owns the book (an official book: the administrator).
    pays = book.owner_student_id or admin.id
    title, before = chapter.title, chapter.error_message
    mark_processing(chapter)
    audit.record(db, "chapter.retry", actor=admin, target_type="chapter", target_id=chapter.id, target_label=title,
                 detail={"book_id": str(book.id), "previous_error": (before or "")[:200], "charged_to": str(pays)})
    db.commit()
    background_tasks.add_task(run_chapter_job, chapter.id, pays, session_factory)
    return {"id": chapter.id, "status": ChapterStatus.PROCESSING}


# ---- AI usage and the kill switch --------------------------------------------------------------------

@router.get("/usage")
def usage_overview(days: int = Query(default=7, ge=1, le=31), admin=Depends(require_admin), db: Session = Depends(get_db)):
    return usage.usage_overview(db, days)


@router.get("/ai/kill-switch")
def get_kill_switch(admin=Depends(require_admin), db: Session = Depends(get_db)):
    ks = usage.kill_switch_state(db, fresh=True)
    return {"engaged": ks.engaged, "source": ks.source, "reason": ks.reason, "since": ks.since, "by": ks.by}


@router.post("/ai/kill-switch")
def set_kill_switch(body: KillSwitchIn, admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Engaged: every LLM / OCR / embedding / speech call is refused until it is released. (AI_KILL_SWITCH=true in the
    server settings does the same and can only be released there.)"""
    if not body.engaged and settings.ai_kill_switch:
        raise HTTPException(status.HTTP_409_CONFLICT, "The switch is also set by AI_KILL_SWITCH in the server settings; change it there.")
    ks = usage.set_kill_switch(db, body.engaged, body.reason, admin.username)
    audit.record(db, "ai.kill_switch_on" if body.engaged else "ai.kill_switch_off", actor=admin, target_type="ai",
                 detail={"reason": body.reason} if body.reason else None)
    db.commit()
    return {"engaged": ks.engaged, "source": ks.source, "reason": ks.reason, "since": ks.since, "by": ks.by}


# ---- teacher invites -----------------------------------------------------------------------------------

def _invite_out(db: Session, inv: TeacherInvite) -> dict:
    used_by = db.get(User, inv.used_by_id) if inv.used_by_id else None
    created_by = db.get(User, inv.created_by_id) if inv.created_by_id else None
    return dict(id=inv.id, note=inv.note, state=invites.invite_state(inv), created_at=inv.created_at, expires_at=inv.expires_at,
                used_at=inv.used_at, used_by_username=used_by.username if used_by else None,
                created_by_username=created_by.username if created_by else None)


@router.get("/teacher-invites", response_model=list[InviteOut])
def list_invites(admin=Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(TeacherInvite).order_by(TeacherInvite.created_at.desc()).limit(200)).all()
    return [InviteOut(**_invite_out(db, r)) for r in rows]


@router.post("/teacher-invites", response_model=InviteCreatedOut, status_code=status.HTTP_201_CREATED)
def create_invite(body: InviteIn = InviteIn(), admin=Depends(require_admin), db: Session = Depends(get_db)):
    code, inv = invites.create_invite(db, admin.id, body.note, body.expires_in_days)
    audit.record(db, "invite.create", actor=admin, target_type="invite", target_id=inv.id, target_label=inv.note,
                 detail={"expires_at": inv.expires_at.isoformat() if inv.expires_at else None})
    db.commit()
    db.refresh(inv)
    return InviteCreatedOut(**_invite_out(db, inv), code=code)


@router.delete("/teacher-invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invite(invite_id: uuid.UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    inv = db.get(TeacherInvite, invite_id)
    if inv is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invite not found")
    if invites.invite_state(inv) != "active":
        raise HTTPException(status.HTTP_409_CONFLICT, "Only an unused invite can be revoked.")
    inv.revoked_at = datetime.now(timezone.utc)
    audit.record(db, "invite.revoke", actor=admin, target_type="invite", target_id=inv.id, target_label=inv.note)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---- audit log and status ---------------------------------------------------------------------------------

@router.get("/audit-log", response_model=AuditList)
def audit_log(
    action: Optional[str] = Query(default=None, max_length=60, description="exact action, or a prefix ending in '.' such as 'user.'"),
    actor: Optional[str] = Query(default=None, max_length=30),
    target: Optional[str] = Query(default=None, max_length=60),
    days: Optional[int] = Query(default=None, ge=1, le=3650),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    cond = []
    if action:
        cond.append(AuditLog.action.like(action + "%") if action.endswith(".") else AuditLog.action == action)
    if actor:
        cond.append(func.lower(AuditLog.actor_username) == actor.strip().lower())
    if target:
        cond.append(func.lower(AuditLog.target_label).like(f"%{target.strip().lower()}%"))
    if days:
        cond.append(AuditLog.created_at >= datetime.now(timezone.utc) - timedelta(days=days))
    total = db.scalar(select(func.count(AuditLog.id)).where(*cond)) or 0
    rows = db.scalars(select(AuditLog).where(*cond).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)).all()
    return AuditList(total=total, items=[AuditOut.model_validate(r) for r in rows])


@router.get("/status")
def status_page(admin=Depends(require_admin), db: Session = Depends(get_db)):
    """Database, Memgraph, SuperTokens, failed chapters, error rate, AI switch and usage in one answer."""
    return health.status_report(db)
