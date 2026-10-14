"""Quizzes, their mixed-difficulty questions, and student responses (Phase 4).

  * `quizzes`: teacher-generated tests (`kind='teacher'`, length 10/20/30, optionally linked to an assignment) or
    student self-triggered practice quizzes (`kind='practice'`, default 10 questions weighted toward weak/at-risk concepts).
  * `quiz_questions`: holds `question_type` ('recall' | 'application' | 'cross_concept') and `answer_format`
    ('mcq' | 'short_answer'). Server-side keys (`correct_index`, `expected_answer`, `explanation`) never leave the
    server before submission (Rules.md §4). Cross-concept questions also set `related_concept_id`.
  * `quiz_responses`: stores the student's submitted answers (`chosen_index` for MCQ, `answer_text` for short-answer)
    alongside the graded outcome (`score` 0..1, `correct` bool, and `feedback` from the LLM short-answer grader)."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class QuizKind:
    TEACHER = "teacher"
    PRACTICE = "practice"


class QuestionType:
    RECALL = "recall"
    APPLICATION = "application"
    CROSS_CONCEPT = "cross_concept"


class AnswerFormat:
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"


class Quiz(Base):
    __tablename__ = "quizzes"
    __table_args__ = (
        CheckConstraint("kind IN ('teacher','practice')", name="ck_quiz_kind"),
        CheckConstraint("status IN ('open','submitted')", name="ck_quiz_status"),
        CheckConstraint("question_count >= 1 AND question_count <= 30", name="ck_quiz_question_count"),
        CheckConstraint(
            "(kind = 'teacher' AND teacher_id IS NOT NULL) OR (kind = 'practice' AND student_id IS NOT NULL)",
            name="ck_quiz_owner",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(10), nullable=False)  # teacher | practice
    teacher_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    book_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True, index=True)
    assignment_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("assignments.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="open")  # open | submitted
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0..1 across graded questions
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.position"
    )
    responses: Mapped[list["QuizResponse"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (
        CheckConstraint("status IN ('pending','ready','failed')", name="ck_quiz_question_status"),
        CheckConstraint("question_type IN ('recall','application','cross_concept')", name="ck_quiz_question_type"),
        CheckConstraint("answer_format IN ('mcq','short_answer')", name="ck_quiz_answer_format"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True, index=True)
    related_concept_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    question_type: Mapped[str] = mapped_column(String(16), nullable=False, default=QuestionType.RECALL)
    answer_format: Mapped[str] = mapped_column(String(16), nullable=False, default=AnswerFormat.MCQ)
    status: Mapped[str] = mapped_column(String(8), nullable=False, default="pending")  # pending | ready | failed
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)  # 4 strings for mcq; None for short_answer
    correct_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0..3 for mcq; NEVER sent before submit
    expected_answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # rubric/key for short_answer; NEVER sent before submit
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")

    quiz: Mapped[Quiz] = relationship(back_populates="questions")
    responses: Mapped[list["QuizResponse"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class QuizResponse(Base):
    __tablename__ = "quiz_responses"
    __table_args__ = (
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_quiz_response_score_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chosen_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for mcq
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # for short_answer
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0..1 (1.0/0.0 for mcq; 0.0..1.0 from LLM for short_answer)
    correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # True when score >= quiz_short_answer_pass_score (or exact match on mcq)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 1-sentence feedback from LLM grader or MCQ explanation
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    quiz: Mapped[Quiz] = relationship(back_populates="responses")
    question: Mapped[QuizQuestion] = relationship(back_populates="responses")