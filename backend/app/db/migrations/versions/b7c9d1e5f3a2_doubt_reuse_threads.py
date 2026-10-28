"""add normalized doubt reuse key and follow-up thread links

Revision ID: b7c9d1e5f3a2
Revises: a9b8c7d6e5f4
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7c9d1e5f3a2"
down_revision: Union[str, None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("doubts") as batch:
        batch.add_column(sa.Column("normalized_text", sa.String(length=1000), nullable=True))
        batch.add_column(sa.Column("parent_doubt_id", sa.Uuid(), nullable=True))
        batch.create_foreign_key(
            "fk_doubts_parent_doubt_id", "doubts", ["parent_doubt_id"], ["id"], ondelete="SET NULL"
        )
        batch.create_index("ix_doubts_parent_doubt_id", ["parent_doubt_id"], unique=False)
        batch.create_index("ix_doubts_student_normalized_text", ["student_id", "normalized_text"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("doubts") as batch:
        batch.drop_index("ix_doubts_student_normalized_text")
        batch.drop_index("ix_doubts_parent_doubt_id")
        batch.drop_constraint("fk_doubts_parent_doubt_id", type_="foreignkey")
        batch.drop_column("parent_doubt_id")
        batch.drop_column("normalized_text")
