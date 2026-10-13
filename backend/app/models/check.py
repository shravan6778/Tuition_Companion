"""Phase 3 step 5: the comprehension check a student takes after marking an assignment complete.

The server keeps every question WITH its key; a student only ever receives `assessment.checks.student_view` until the
check is submitted. `assignment_id` goes NULL when the teacher deletes the assignment (the student's record stays, as
doubts do); `assignment_title` is kept so the record still reads. Step 6 writes mastery events from a submitted check."""
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, Uuid, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssignmentCheck(Base):
    __tablename__ = "assignment_checks"
    __table_args__ = (
        CheckConstraint("status IN ('open','submitted')", name="ck_check_status"),
        # one OPEN check per student and assignment: a double click (or a second device) resumes it instead of paying for another
        Index("uq_one_open_check", "student_id", "assignment_id", unique=True,
              postgresql_where=text("status = 'open'"), sqlite_where=text("status = 'open'")),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    assignment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assignments.id", ondelete="SET NULL"), index=True, nullable=True)
    assignment_title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(10), default="open", server_default="open")
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # share of the graded questions answered right, set on submit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    questions: Mapped[list["CheckQuestion"]] = relationship(
        back_populates="check", cascade="all, delete-orphan", order_by="CheckQuestion.position")


class CheckQuestion(Base):
    __tablename__ = "check_questions"
    __table_args__ = (CheckConstraint("status IN ('pending','ready','failed')", name="ck_check_question_status"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    check_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignment_checks.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    # pending = planned, not written yet; ready = written; failed = the model never gave a valid question (shown as "couldn't generate")
    status: Mapped[str] = mapped_column(String(8), default="pending", server_default="pending")
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_index: Mapped[int | None] = mapped_column(Integer, nullable=True)  # THE KEY: never sent before submission
    explanation: Mapped[str] = mapped_column(Text, default="", server_default="")
    chosen_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    check: Mapped[AssignmentCheck] = relationship(back_populates="questions")
