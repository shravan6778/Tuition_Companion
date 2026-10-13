"""assignments and their confirmed concept lists (Phase 3 step 1)

Revision ID: f2c8d1a5b394
Revises: e1b4c7d9a203
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2c8d1a5b394"
down_revision: Union[str, None] = "e1b4c7d9a203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=True),
        sa.Column("student_id", sa.Uuid(), nullable=True),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=True),
        sa.Column("level", sa.String(length=10), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("exercise_pages", sa.JSON(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("level IN ('subject','chapter','concept','exercise')", name="ck_assignment_level"),
        sa.CheckConstraint(
            "(room_id IS NOT NULL AND student_id IS NULL) OR (room_id IS NULL AND student_id IS NOT NULL)",
            name="ck_assignment_target"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignments_teacher_id"), "assignments", ["teacher_id"])
    op.create_index(op.f("ix_assignments_room_id"), "assignments", ["room_id"])
    op.create_index(op.f("ix_assignments_student_id"), "assignments", ["student_id"])
    op.create_index(op.f("ix_assignments_book_id"), "assignments", ["book_id"])
    op.create_table(
        "assignment_concepts",
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("assignment_id", "concept_id"),
    )
    op.create_index(op.f("ix_assignment_concepts_concept_id"), "assignment_concepts", ["concept_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_assignment_concepts_concept_id"), table_name="assignment_concepts")
    op.drop_table("assignment_concepts")
    for name in ("book_id", "student_id", "room_id", "teacher_id"):
        op.drop_index(op.f(f"ix_assignments_{name}"), table_name="assignments")
    op.drop_table("assignments")
