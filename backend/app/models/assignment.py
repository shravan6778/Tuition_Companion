"""Assignments are curriculum targets, not pointers to one student's private book.

A teacher creates a room/student task using subject + chapter title + optional item
label. The same target is resolved against each student's own uploaded copy when
that student opens the assignment.

The one exception is the `manual` level (school homework): it points at no book at all. It carries a free-text
subject, a title and a description, and is verified by the student's photo or spoken answer plus the teacher's
verdict (`ManualSubmission`), never by an AI-written check.
"""
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AssignmentLevel:
    SUBJECT = "subject"
    CHAPTER = "chapter"
    CONCEPT = "concept"
    EXERCISE = "exercise"  # legacy: one exercise label + proposed concepts; new work uses ITEMS
    ITEMS = "items"        # finer grain: specific examples / exercise questions / figures (+ optional concepts)
    MANUAL = "manual"      # school homework: no book, no concepts; verified by a photo / spoken answer + the teacher's verdict
    ALL = (SUBJECT, CHAPTER, CONCEPT, EXERCISE, ITEMS, MANUAL)


class SubmissionSource:
    PHOTO = "photo"  # a photo of the written work
    VOICE = "voice"  # the student's spoken answer, turned into text on their device
    ALL = (PHOTO, VOICE)


class Verdict:
    """The teacher's judgement of a manual task's work. `good` closes the task; the other two ask for another go."""
    GOOD = "good"
    NEEDS_WORK = "needs_work"
    REDO = "redo"
    ALL = (GOOD, NEEDS_WORK, REDO)


class AssignmentItemKind:
    """Page-item kinds a teacher can assign one by one. `concept` items are assigned through the concept list."""
    EXAMPLE = "example"
    EXERCISE_QUESTION = "exercise_question"
    DIAGRAM = "diagram"
    ACTIVITY = "activity"
    SIDEBAR = "sidebar"
    ALL = (EXAMPLE, EXERCISE_QUESTION, DIAGRAM, ACTIVITY, SIDEBAR)


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        CheckConstraint("level IN ('subject','chapter','concept','exercise','items','manual')", name="ck_assignment_level"),
        # a manual task points at no book, so it has no chapter or item target
        CheckConstraint("level <> 'manual' OR (chapter_title IS NULL AND item_label IS NULL)", name="ck_assignment_manual_shape"),
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
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # what to do (manual tasks); optional elsewhere
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    concepts: Mapped[list["AssignmentConcept"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="AssignmentConcept.position")
    items: Mapped[list["AssignmentItem"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="AssignmentItem.position")
    submissions: Mapped[list["ManualSubmission"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan", order_by="ManualSubmission.created_at")


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


class AssignmentItem(Base):
    """One example / exercise question / figure / activity the teacher picked.

    Like the concept list this is curriculum METADATA (kind + label), never a pointer into one student's private book:
    each student's own copy is searched for the item with the same kind and label key. `page_number` is only a tie-breaker
    for labels that repeat inside a chapter (every exercise has a "Q1"); `item_id` remembers the source-book row for the
    teacher's view and is NOT used to resolve a student's copy.
    """
    __tablename__ = "assignment_items"
    __table_args__ = (
        CheckConstraint("kind IN ('example','exercise_question','diagram','activity','sidebar')", name="ck_assignment_item_kind"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), index=True)
    item_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("page_items.id", ondelete="SET NULL"), nullable=True)
    kind: Mapped[str] = mapped_column(String(24), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    item_key: Mapped[str] = mapped_column(String(160), nullable=False, index=True)  # loose_key(label)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    assignment: Mapped[Assignment] = relationship(back_populates="items")


class ManualSubmission(Base):
    """A student's proof of work on a `manual` assignment: a photo of it, or a spoken answer (as text), then the teacher's verdict.

    Unlike a doubt's photo, the photo IS kept (stored by hash, like uploaded books): the teacher has to look at the real
    handwriting, and OCR of a child's exercise book is not good enough to judge by. Nothing here is graded by a model and
    nothing is written to the mastery log: manual work has no concepts, so the only judge is the teacher.
    A student may submit again after `needs_work` or `redo`; every attempt is kept, the newest one counts.
    """
    __tablename__ = "manual_submissions"
    __table_args__ = (
        CheckConstraint("source IN ('photo','voice')", name="ck_submission_source"),
        CheckConstraint("verdict IS NULL OR verdict IN ('good','needs_work','redo')", name="ck_submission_verdict"),
        CheckConstraint(
            "(source = 'photo' AND photo_path IS NOT NULL) OR (source = 'voice' AND text IS NOT NULL AND text <> '')",
            name="ck_submission_has_work"),
        CheckConstraint("(verdict IS NULL) = (reviewed_at IS NULL)", name="ck_submission_reviewed_together"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assignments.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(8))
    photo_path: Mapped[str | None] = mapped_column(String(300), nullable=True)  # relative to the storage root
    text: Mapped[str | None] = mapped_column(Text, nullable=True)  # voice: the transcript; photo: an optional note
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    verdict: Mapped[str | None] = mapped_column(String(10), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)  # the teacher's note to the student
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assignment: Mapped[Assignment] = relationship(back_populates="submissions")
