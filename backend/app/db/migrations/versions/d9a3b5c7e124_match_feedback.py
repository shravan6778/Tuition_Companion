"""teacher decisions about variant suggestions (Layer 5)

Revision ID: d9a3b5c7e124
Revises: c8f2a4b6d913
Create Date: 2026-10-10

`match_feedback` records, per (book, base book), whether the teacher confirmed, dismissed or retracted the
'this is a variant of that book' suggestion, together with the evidence the suggestion showed. Dismissed
suggestions are no longer offered for that book. Existing books have no rows.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd9a3b5c7e124'
down_revision: Union[str, None] = 'c8f2a4b6d913'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'match_feedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('base_book_id', sa.Uuid(), nullable=False),
        sa.Column('decision', sa.String(length=10), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('book_id <> base_book_id', name='ck_match_feedback_not_self'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['base_book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('book_id', 'base_book_id', name='uq_match_feedback_pair'),
    )
    op.create_index(op.f('ix_match_feedback_book_id'), 'match_feedback', ['book_id'])
    op.create_index(op.f('ix_match_feedback_base_book_id'), 'match_feedback', ['base_book_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_match_feedback_base_book_id'), table_name='match_feedback')
    op.drop_index(op.f('ix_match_feedback_book_id'), table_name='match_feedback')
    op.drop_table('match_feedback')
