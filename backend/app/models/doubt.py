"""Phase 3 step 2: every doubt a student raises, with how retrieval judged it. Step 3 adds the explanation to it."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, String, Text, Uuid, func
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
    # Step 3: the Tutor's explanation. answer_status: none (not grounded, nothing asked of the Tutor) | answered |
    # unanswered (the pages don't answer it) | failed (couldn't generate; the pages are still shown)
    answer_status: Mapped[str] = mapped_column(String(12), default="none", server_default="none")
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresher: Mapped[str | None] = mapped_column(Text, nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")  # low retrieval confidence: "auto-generated, please verify"
    answer_model: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
