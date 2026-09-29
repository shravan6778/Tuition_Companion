from __future__ import annotations

import enum
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from app.models.content import student_book

if TYPE_CHECKING:
    from app.models.content import Book


class Role(str, enum.Enum):
    teacher = "teacher"
    student = "student"
    parent = "parent"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supertokens_user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), index=True)  # contact info only — a household can share one number
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"))
    link_code: Mapped[str | None] = mapped_column(String(12), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Reverse relationship for student linking to books
    books: Mapped[list[Book]] = relationship(
        "Book", secondary=student_book, back_populates="students"
    )