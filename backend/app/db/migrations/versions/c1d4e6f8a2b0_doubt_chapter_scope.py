"""store chapter scope for doubt reuse

Revision ID: c1d4e6f8a2b0
Revises: b7c9d1e5f3a2
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d4e6f8a2b0"
down_revision: Union[str, None] = "b7c9d1e5f3a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("doubts") as batch:
        batch.add_column(sa.Column("chapter_id", sa.Uuid(), nullable=True))
        batch.create_foreign_key("fk_doubts_chapter_id", "chapters", ["chapter_id"], ["id"], ondelete="SET NULL")
        batch.create_index("ix_doubts_chapter_id", ["chapter_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("doubts") as batch:
        batch.drop_index("ix_doubts_chapter_id")
        batch.drop_constraint("fk_doubts_chapter_id", type_="foreignkey")
        batch.drop_column("chapter_id")
