"""Tables behind the administration, security and monitoring features:

  * UsageEvent: one row per paid / free-tier AI call (LLM, OCR, embeddings, speech): who, which provider, how much.
    The per-user daily caps and the admin usage page are sums over this table (usage/service.py).
  * AuditLog: who did what to whom (admin actions, resets, joins, removals, deletions). Rows are never edited; the
    actor and target are also copied as plain text so the history survives the deletion of the user it is about.
  * AppSetting: small runtime switches an administrator can flip without a deploy (the AI kill switch).
  * TeacherInvite: single-use codes that let a teacher register without waiting for approval (only a hash is stored).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_user_quota_created", "user_id", "quota", "created_at"),
        Index("ix_usage_events_quota_created", "quota", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    # NULL = no signed-in user (an admin script, the graph rebuild). The row stays when the user is deleted.
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    provider: Mapped[str] = mapped_column(String(40))  # "openai_compat", "azure_doc_intel", "azure_speech", "fake", ...
    operation: Mapped[str] = mapped_column(String(60))  # "llm.complete_json", "ocr.extract_layout", "embedding.embed", ...
    quota: Mapped[str] = mapped_column(String(20))  # "llm_tokens" | "ocr_pages" | "embedding_tokens" | "speech_calls"
    units: Mapped[int] = mapped_column(Integer, default=0)  # tokens, pages or calls (0 for a blocked attempt)
    unit_type: Mapped[str] = mapped_column(String(10))  # "tokens" | "pages" | "calls"
    estimated: Mapped[bool] = mapped_column(default=False, server_default="false")  # True: counted from text length, the provider sent no figure
    status: Mapped[str] = mapped_column(String(10), default="ok", server_default="ok")  # "ok" | "error" | "blocked"
    request_id: Mapped[str | None] = mapped_column(String(40), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_action_created", "action", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_username: Mapped[str | None] = mapped_column(String(30), nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(12), nullable=True)
    action: Mapped[str] = mapped_column(String(60))  # "user.disable", "room.member_removed", ...
    target_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    target_label: Mapped[str | None] = mapped_column(String(160), nullable=True)  # username, room name, book title...
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # small, secret-free facts about the action
    request_id: Mapped[str | None] = mapped_column(String(40), nullable=True)


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(60), primary_key=True)
    value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by: Mapped[str | None] = mapped_column(String(30), nullable=True)


class TeacherInvite(Base):
    __tablename__ = "teacher_invites"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # sha256 of the code; the code itself is shown once
    note: Mapped[str | None] = mapped_column(String(120), nullable=True)  # e.g. who it is for
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    used_by_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
