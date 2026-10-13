"""Phase 3 step 2: every doubt a student raises, with how retrieval judged it. Step 3 adds the explanation to it."""
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Doubt(Base):
    __tablename__ = "doubts"
    __table_args__ = (
        CheckConstraint("status IN ('grounded','outside_assignment','not_in_book','unavailable')", name="ck_doubt_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # None = a standalone doubt (no assignment). Deleting an assignment keeps the student's doubt history.
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assignments.id", ondelete="SET NULL"), index=True, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20))
    concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)  # best concept hit when grounded
    confidence: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")  # best similarity inside the scope
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
