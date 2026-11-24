import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminUserOut(BaseModel):
    id: uuid.UUID
    username: str
    name: str
    phone_masked: str
    role: str
    status: str
    is_admin: bool
    created_at: datetime
    status_changed_at: Optional[datetime] = None
    usage_today: dict[str, int] = {}
    caps: dict[str, int] = {}  # effective daily caps (0 = unlimited)
    quota_overrides: Optional[dict[str, int]] = None


class AdminUserList(BaseModel):
    total: int
    items: list[AdminUserOut]


class ReasonIn(BaseModel):
    reason: Optional[str] = Field(default=None, max_length=200)


class DeleteUserIn(BaseModel):
    confirm_username: str = Field(min_length=1, max_length=30)
    reason: Optional[str] = Field(default=None, max_length=200)


class CapsIn(BaseModel):
    # Any subset of: llm_tokens, ocr_pages, embedding_tokens, speech_calls. 0 = unlimited. null = back to the default.
    caps: dict[str, Optional[int]]


class KillSwitchIn(BaseModel):
    engaged: bool
    reason: Optional[str] = Field(default=None, max_length=200)


class InviteIn(BaseModel):
    note: Optional[str] = Field(default=None, max_length=120)
    expires_in_days: Optional[int] = Field(default=None, ge=0, le=90)  # 0 = never; null = the default


class InviteOut(BaseModel):
    id: uuid.UUID
    note: Optional[str]
    state: str  # active | used | expired | revoked
    created_at: datetime
    expires_at: Optional[datetime]
    used_at: Optional[datetime]
    used_by_username: Optional[str]
    created_by_username: Optional[str]


class InviteCreatedOut(InviteOut):
    code: str  # shown ONCE: only its hash is stored


class FailedChapterOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    state: str  # failed | stuck
    error_message: Optional[str]
    book_id: uuid.UUID
    book_label: str
    is_reference: bool
    owner_username: Optional[str]
    owner_name: Optional[str]
    processing_started_at: Optional[datetime]
    can_retry: bool


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    actor_username: Optional[str]
    actor_role: Optional[str]
    action: str
    target_type: Optional[str]
    target_id: Optional[str]
    target_label: Optional[str]
    detail: Optional[dict[str, Any]]
    request_id: Optional[str]


class AuditList(BaseModel):
    total: int
    items: list[AuditOut]
