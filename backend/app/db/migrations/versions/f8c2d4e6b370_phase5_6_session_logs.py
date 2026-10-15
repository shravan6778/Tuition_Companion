"""phase 5 & 6 step 0: create session_logs table

Revision ID: f8c2d4e6b370
Revises: e7b1c3d5a269
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8c2d4e6b370"
down_revision: Union[str, None] = "e7b1c3d5a269"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column("session_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(" notes <> '' ", name="ck_session_log_notes_nonempty"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_session_logs_student_id"), "session_logs", ["student_id"])
    op.create_index(op.f("ix_session_logs_teacher_id"), "session_logs", ["teacher_id"])
    op.create_index(op.f("ix_session_logs_session_date"), "session_logs", ["session_date"])


def downgrade() -> None:
    op.drop_index(op.f("ix_session_logs_session_date"), table_name="session_logs")
    op.drop_index(op.f("ix_session_logs_teacher_id"), table_name="session_logs")
    op.drop_index(op.f("ix_session_logs_student_id"), table_name="session_logs")
    op.drop_table("session_logs")