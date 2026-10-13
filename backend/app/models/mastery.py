"""Phase 3 step 6: the append-only mastery log. Rows are only ever INSERTED by the app, never updated or deleted.

  kind 'check'      : a measured result for one concept in a submitted check (score = share correct, asked, correct)
  kind 'doubt'      : the student asked about the concept (no score); feeds the "ask first" ordering of the next check
  kind 'propagated' : a dependent concept marked "at risk" because a prerequisite TESTED weak. Never a score, and it ALWAYS
                      carries its reason (and the concept that caused it), so it is never shown as a direct measurement.

Current mastery of a concept = the score of its latest `check` event; weak = below WEAK_BELOW. A concept is "at risk" while its
latest check-or-propagated event is a propagated one; the next measured check on it clears that. `id` is the order of events
(a sequence), so events written in one transaction still sort in the order they were written.
`concept_name` is a snapshot so the history still reads after a chapter is re-processed (concept_id then goes NULL)."""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MasteryEvent(Base):
    __tablename__ = "mastery_events"
    __table_args__ = (
        CheckConstraint("kind IN ('check','doubt','propagated')", name="ck_mastery_kind"),
        CheckConstraint("kind <> 'propagated' OR (reason IS NOT NULL AND reason <> '')", name="ck_mastery_propagated_reason"),
        CheckConstraint("kind <> 'check' OR (score IS NOT NULL AND asked IS NOT NULL AND correct IS NOT NULL)", name="ck_mastery_check_scored"),
        CheckConstraint("kind = 'check' OR score IS NULL", name="ck_mastery_only_checks_score"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_mastery_score_range"),
    )

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), index=True, nullable=True)
    concept_name: Mapped[str] = mapped_column(String(300))
    kind: Mapped[str] = mapped_column(String(10))
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    asked: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assignments.id", ondelete="SET NULL"), nullable=True)
    check_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assignment_checks.id", ondelete="SET NULL"), index=True, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)  # propagated: the weak prerequisite
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
