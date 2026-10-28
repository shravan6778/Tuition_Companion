"""add status and approved_at to parent_student_links

Revision ID: a9b8c7d6e5f4
Revises: f8c2d4e6b370
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "f8c2d4e6b370"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("parent_student_links") as batch:
        batch.add_column(sa.Column("status", sa.String(length=12), server_default="approved", nullable=False))
        batch.add_column(sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_check_constraint("ck_parent_student_link_status", "status IN ('pending','approved')")


def downgrade() -> None:
    with op.batch_alter_table("parent_student_links") as batch:
        batch.drop_constraint("ck_parent_student_link_status", type_="check")
        batch.drop_column("approved_at")
        batch.drop_column("status")