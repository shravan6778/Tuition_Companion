"""Teacher session log entries for Phase 6 (Personalization & Session Continuity).

  * Recorded by a teacher against a specific student and date (`session_date`).
  * Stores free-text `notes` and `tags` (JSON list of quick-tag strings).
  * Read by the Personalization Agent alongside `mastery_events` to generate pre-session briefings."""
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, JSON, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SessionLog(Base):
    __tablename__ = "session_logs"
    __table_args__ = (
        CheckConstraint(" notes <> '' ", name="ck_session_log_notes_nonempty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    session_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )