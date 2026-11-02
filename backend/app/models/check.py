"""Phase 3 step 5: the comprehension check a student takes after marking an assignment complete.

The server keeps every question WITH its key; a student only ever receives `assessment.checks.student_view` until the
check is submitted. `assignment_id` goes NULL when the teacher deletes the assignment (the student's record stays, as
doubts do); `assignment_title` is kept so the record still reads. Step 6 writes mastery events from a submitted check."""
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, Uuid, Boolean, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .answers import WrittenAnswerMixin
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
    subject: Mapped[str | None] = mapped_column(String(120), nullable=True)  # the assignment's subject, kept for the maths-type rule if it is deleted
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # share of the graded questions answered right, set on submit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    questions: Mapped[list["CheckQuestion"]] = relationship(
        back_populates="check", cascade="all, delete-orphan", order_by="CheckQuestion.position")


class CheckQuestion(WrittenAnswerMixin, Base):
    __tablename__ = "check_questions"
    __table_args__ = (
        CheckConstraint("status IN ('pending','ready','failed')", name="ck_check_question_status"),
        CheckConstraint("answer_format IN ('mcq','short_answer','long_answer')", name="ck_check_question_format"),
        CheckConstraint("input_method IN ('typed','voice')", name="ck_check_question_input_method"),
        CheckConstraint("score_source IS NULL OR score_source IN ('ai','teacher')", name="ck_check_question_score_source"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_check_question_score_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    check_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignment_checks.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    # pending = planned, not written yet; ready = written; failed = the model never gave a valid question (shown as "couldn't generate")
    status: Mapped[str] = mapped_column(String(8), default="pending", server_default="pending")
    question: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # mcq (the default, graded in code) | short_answer | long_answer (graded against `key_points`; see assessment/llm_grader.py)
    answer_format: Mapped[str] = mapped_column(String(16), default="mcq", server_default="mcq", nullable=False)
    correct_index: Mapped[int | None] = mapped_column(Integer, nullable=True)  # THE KEY: never sent before submission
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)  # model answer of a written question: never sent before submission
    key_points: Mapped[list | None] = mapped_column(JSON, nullable=True)  # the rubric [{"point","marks"}]: never sent before submission
    explanation: Mapped[str] = mapped_column(Text, default="", server_default="")
    chosen_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # a written / spoken answer (after the student reviewed it)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0..1 for a written answer (marks won / marks available)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)  # the grader's one-sentence note

    check: Mapped[AssignmentCheck] = relationship(back_populates="questions")
