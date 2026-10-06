"""page concepts_model

Revision ID: a8e2c5d7f419
Revises: f7d5a0b4c138
Create Date: 2026-10-06

Records which model produced each page's concepts. 'fake' marks placeholder concepts (never reused by a real
run). Pages processed before this migration stay NULL ('origin unknown'): they are not reused until their
chapter is reprocessed (python -m app.db.reprocess <book-id>).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a8e2c5d7f419'
down_revision: Union[str, None] = 'f7d5a0b4c138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pages', sa.Column('concepts_model', sa.String(length=60), nullable=True))


def downgrade() -> None:
    op.drop_column('pages', 'concepts_model')
