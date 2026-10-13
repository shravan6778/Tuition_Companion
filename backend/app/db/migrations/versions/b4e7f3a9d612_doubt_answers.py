"""the Tutor's explanation stored on the doubt (Phase 3 step 3)

Revision ID: b4e7f3a9d612
Revises: a3d9e2c6f581
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b4e7f3a9d612"
down_revision: Union[str, None] = "a3d9e2c6f581"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("doubts", sa.Column("answer_status", sa.String(length=12), server_default="none", nullable=False))
    op.add_column("doubts", sa.Column("answer", sa.Text(), nullable=True))
    op.add_column("doubts", sa.Column("refresher", sa.Text(), nullable=True))
    op.add_column("doubts", sa.Column("needs_review", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("doubts", sa.Column("answer_model", sa.String(length=60), nullable=True))


def downgrade() -> None:
    for name in ("answer_model", "needs_review", "refresher", "answer", "answer_status"):
        op.drop_column("doubts", name)
