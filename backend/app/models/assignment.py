"""Assignments are curriculum targets, not pointers to one student's private book.

A teacher creates a room/student task using subject + chapter title + optional item
label. The same target is resolved against each student's own uploaded copy when
that student opens the assignment.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssignmentLevel:
    SUBJECT = "subject"
    CHAPTER = "chapter"
    CONCEPT = "concept"
    EXERCISE = "exercise"
    ALL = (SUBJECT, CHAPTER, CONCEPT, EXERCISE)


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint("level IN ('subject','chapter','concept','exercise')", name="ck_assignment_level"),
        CheckConstraint(
            "(room_id IS NOT NULL AND student_id IS NULL) OR (room_id IS NULL AND student_id IS NOT NULL)",
            name="ck_assignment_target"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    room_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=True)
    student_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    subject: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    chapter_title: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    item_label: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(200))
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    concepts: Mapped[list["AssignmentConcept"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="AssignmentConcept.position")


class AssignmentConcept(Base):
    __tablename__ = "assignment_concepts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), index=True)
    # This is a source-book concept id when available, but it is NOT used for student resolution.
    concept_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("concepts.id", ondelete="SET NULL"), nullable=True)
    concept_name: Mapped[str] = mapped_column(String(200), nullable=False)
    concept_key: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    assignment: Mapped[Assignment] = relationship(back_populates="concepts")
