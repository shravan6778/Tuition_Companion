"""Phase 3 step 1: what a teacher assigns. One row per assignment, plus the CONFIRMED concept list it covers.

The concept list is stored (not recomputed on every read) so a later re-processing of a chapter can never
silently change what a student was assigned, and so the Doubt button, the comprehension check and the weak-area
flags (steps 2-6) all start from the same list."""
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssignmentLevel:
    SUBJECT = "subject"    # every ready chapter of the chosen book
    CHAPTER = "chapter"    # one chapter
    CONCEPT = "concept"    # concepts the teacher picked
    EXERCISE = "exercise"  # an exercise's pages -> proposed concepts -> the teacher edits and confirms
    ALL = (SUBJECT, CHAPTER, CONCEPT, EXERCISE)


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint("level IN ('subject','chapter','concept','exercise')", name="ck_assignment_level"),
        # given to a whole room OR to one student, never both and never neither
        CheckConstraint("(room_id IS NOT NULL AND student_id IS NULL) OR (room_id IS NULL AND student_id IS NOT NULL)",
                        name="ck_assignment_target"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    room_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), index=True, nullable=True)
    student_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    book_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    level: Mapped[str] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(200))
    exercise_pages: Mapped[list | None] = mapped_column(JSON, nullable=True)  # page numbers the teacher picked (exercise level)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    concepts: Mapped[list["AssignmentConcept"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="AssignmentConcept.position")


class AssignmentConcept(Base):
    __tablename__ = "assignment_concepts"

    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True)
    concept_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True, index=True)
    position: Mapped[int] = mapped_column(default=0, server_default="0")

    assignment: Mapped[Assignment] = relationship(back_populates="concepts")
