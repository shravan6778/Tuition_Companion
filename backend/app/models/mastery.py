"""Append-only mastery log (Phase 3 step 6, extended in Phase 4 step 0 for quizzes).

Decided in Phase 3 & Phase 4:
  * rows are NEVER updated or deleted by the app: every check, quiz, doubt and propagated weak flag is a dated event,
    and current mastery is read from the log (Phase 7 trends and briefings read the same rows).
  * `check` / `quiz`: a concept was tested in a comprehension check (`check`) or a full/practice quiz (`quiz`).
                 `asked`, `correct` and `score` = correct / asked (0..1) are always set.
                 Current mastery of a concept = the score of its latest `check` or `quiz` event; weak means score < WEAK_BELOW.
  * `propagated` a concept was NOT tested: a prerequisite of it tested weak, so this concept is marked "at risk". `score` is
                 always NULL (it is never presented as a measurement) and `reason` is always set, e.g.
                 "flagged because it depends on Cell, which tested weak". Cleared by the next measured check or quiz on that concept.
  * `doubt`      the student asked a grounded doubt about this concept (`score` is NULL). Feeds the "ask first" ordering."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MasteryEvent(Base):
    __tablename__ = "mastery_events"
    __table_args__ = (
        CheckConstraint("kind IN ('check','quiz','doubt','propagated')", name="ck_mastery_kind"),
        CheckConstraint("kind <> 'propagated' OR (reason IS NOT NULL AND reason <> '')", name="ck_mastery_propagated_reason"),
        CheckConstraint(
            "kind NOT IN ('check','quiz') OR (score IS NOT NULL AND asked IS NOT NULL AND correct IS NOT NULL)",
            name="ck_mastery_check_scored",
        ),
        CheckConstraint("kind IN ('check','quiz') OR score IS NULL", name="ck_mastery_only_checks_score"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_mastery_score_range"),
    )

    # BigInteger sequence: two events written in the same millisecond still have a strict, unambiguous order.
    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True, index=True)
    # Kept on the row so a student's history stays readable if a teacher later re-uploads the chapter.
    concept_name: Mapped[str] = mapped_column(String(300), nullable=False)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)  # check | quiz | doubt | propagated
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    asked: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    correct: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("assignments.id", ondelete="SET NULL"), nullable=True)
    check_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("assignment_checks.id", ondelete="SET NULL"), nullable=True, index=True)
    quiz_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True, index=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)