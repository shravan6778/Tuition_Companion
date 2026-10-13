"""doubts: what a student asked and how retrieval judged it (Phase 3 step 2)

Revision ID: a3d9e2c6f581
Revises: f2c8d1a5b394
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3d9e2c6f581"
down_revision: Union[str, None] = "f2c8d1a5b394"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "doubts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("confidence", sa.Float(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('grounded','outside_assignment','not_in_book','unavailable')", name="ck_doubt_status"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_doubts_student_id"), "doubts", ["student_id"])
    op.create_index(op.f("ix_doubts_assignment_id"), "doubts", ["assignment_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_doubts_assignment_id"), table_name="doubts")
    op.drop_index(op.f("ix_doubts_student_id"), table_name="doubts")
    op.drop_table("doubts")
