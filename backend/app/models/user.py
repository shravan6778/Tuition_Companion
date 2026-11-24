from __future__ import annotations

import enum
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from app.models.content import student_book

if TYPE_CHECKING:
    from app.models.content import Book


class Role(str, enum.Enum):
    teacher = "teacher"
    student = "student"
    parent = "parent"


class AccountStatus:
    """active: normal. pending: a teacher waiting for an administrator (can log in, can do nothing else).
    disabled: locked out by an administrator (sessions revoked; every request is refused)."""
    ACTIVE = "active"
    PENDING = "pending"
    DISABLED = "disabled"
    ALL = (ACTIVE, PENDING, DISABLED)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("status IN ('active','pending','disabled')", name="ck_user_status"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supertokens_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)  # contact info only — a household can share one number
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"))
    link_code: Mapped[str | None] = mapped_column(String(12), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(12), default=AccountStatus.ACTIVE, server_default=AccountStatus.ACTIVE)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Per-user daily AI caps that replace the defaults, e.g. {"llm_tokens": 500000}. 0 = unlimited. See usage/service.py.
    quota_overrides: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Reverse relationship for student linking to books
    books: Mapped[list[Book]] = relationship(
        "Book", secondary=student_book, back_populates="students"
    )