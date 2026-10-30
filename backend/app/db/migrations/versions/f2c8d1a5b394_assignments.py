"""assignments as curriculum targets rather than book pointers."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

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
        sa.Column("subject", sa.String(length=120), nullable=False),
        sa.Column("chapter_title", sa.String(length=200), nullable=True),
        sa.Column("item_label", sa.String(length=120), nullable=True),
        sa.Column("level", sa.String(length=10), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("level IN ('subject','chapter','concept','exercise')", name="ck_assignment_level"),
        sa.CheckConstraint("(room_id IS NOT NULL AND student_id IS NULL) OR (room_id IS NULL AND student_id IS NOT NULL)", name="ck_assignment_target"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name in ("teacher_id", "room_id", "student_id"):
        op.create_index(op.f(f"ix_assignments_{name}"), "assignments", [name])
    op.create_index(op.f("ix_assignments_subject"), "assignments", ["subject"])
    op.create_index(op.f("ix_assignments_chapter_title"), "assignments", ["chapter_title"])
    op.create_index(op.f("ix_assignments_item_label"), "assignments", ["item_label"])

    op.create_table(
        "assignment_concepts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("concept_name", sa.String(length=200), nullable=False),
        sa.Column("concept_key", sa.String(length=240), nullable=False),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignment_concepts_assignment_id"), "assignment_concepts", ["assignment_id"])
    op.create_index(op.f("ix_assignment_concepts_concept_id"), "assignment_concepts", ["concept_id"])
    op.create_index(op.f("ix_assignment_concepts_concept_key"), "assignment_concepts", ["concept_key"])


def downgrade() -> None:
    op.drop_index(op.f("ix_assignment_concepts_concept_key"), table_name="assignment_concepts")
    op.drop_index(op.f("ix_assignment_concepts_concept_id"), table_name="assignment_concepts")
    op.drop_index(op.f("ix_assignment_concepts_assignment_id"), table_name="assignment_concepts")
    op.drop_table("assignment_concepts")
    for name in ("item_label", "chapter_title", "subject", "student_id", "room_id", "teacher_id"):
        op.drop_index(op.f(f"ix_assignments_{name}"), table_name="assignments")
    op.drop_table("assignments")
