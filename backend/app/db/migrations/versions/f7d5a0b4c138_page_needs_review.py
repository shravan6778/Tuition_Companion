"""page needs_review replaces verified

Revision ID: f7d5a0b4c138
Revises: e6c4f9a3b027
Create Date: 2026-10-05

`verified` (teacher vs student upload) stopped meaning anything once student uploads were removed: every page
was True. It becomes `needs_review` + `review_note`: set by the pipeline when a page looks wrong (e.g. lots of
text but no concepts found), so teachers can re-scan it.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f7d5a0b4c138'
down_revision: Union[str, None] = 'e6c4f9a3b027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('pages', sa.Column('needs_review', sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column('pages', sa.Column('review_note', sa.String(length=200), nullable=True))
    op.drop_column('pages', 'verified')


def downgrade() -> None:
    op.add_column('pages', sa.Column('verified', sa.Boolean(), nullable=True))
    op.execute("UPDATE pages SET verified = true")
    op.drop_column('pages', 'review_note')
    op.drop_column('pages', 'needs_review')
