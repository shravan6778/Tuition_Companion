"""comprehension checks and their questions (Phase 3 step 5)

Revision ID: c5f8a1d3e947
Revises: b4e7f3a9d612
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c5f8a1d3e947"
down_revision: Union[str, None] = "b4e7f3a9d612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assignment_checks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=True),
        sa.Column("assignment_title", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=10), server_default="open", nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('open','submitted')", name="ck_check_status"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignment_checks_student_id"), "assignment_checks", ["student_id"])
    op.create_index(op.f("ix_assignment_checks_assignment_id"), "assignment_checks", ["assignment_id"])
    op.create_index("uq_one_open_check", "assignment_checks", ["student_id", "assignment_id"], unique=True, postgresql_where=sa.text("status = 'open'"))
    op.create_table(
        "check_questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("check_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=8), server_default="pending", nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("correct_index", sa.Integer(), nullable=True),
        sa.Column("explanation", sa.Text(), server_default="", nullable=False),
        sa.Column("chosen_index", sa.Integer(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.CheckConstraint("status IN ('pending','ready','failed')", name="ck_check_question_status"),
        sa.ForeignKeyConstraint(["check_id"], ["assignment_checks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_check_questions_check_id"), "check_questions", ["check_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_check_questions_check_id"), table_name="check_questions")
    op.drop_table("check_questions")
    op.drop_index("uq_one_open_check", table_name="assignment_checks", postgresql_where=sa.text("status = 'open'"))
    op.drop_index(op.f("ix_assignment_checks_assignment_id"), table_name="assignment_checks")
    op.drop_index(op.f("ix_assignment_checks_student_id"), table_name="assignment_checks")
    op.drop_table("assignment_checks")
