"""page fingerprint index

Revision ID: d5b3e8f2a916
Revises: c4a91d6e3f72
Create Date: 2026-10-04

Fingerprints move from a comma-joined string (single-word MinHash) to 512 raw bytes (3-word-shingle
MinHash) plus an LSH lookup table (page_bands), so matching no longer scans every page.
The old signatures are incompatible and are dropped: run `python -m app.db.rebuild_fingerprints`
afterwards to recompute them from the stored page text. chapters.match_report holds the last
matching summary used for 'looks like a variant of X' suggestions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'd5b3e8f2a916'
down_revision: Union[str, None] = 'c4a91d6e3f72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('pages', 'fingerprint')
    op.add_column('pages', sa.Column('fingerprint', sa.LargeBinary(), nullable=True))
    op.add_column('chapters', sa.Column('match_report', sa.JSON(), nullable=True))
    op.create_table(
        'page_bands',
        sa.Column('page_id', sa.Uuid(), nullable=False),
        sa.Column('key', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('page_id', 'key'),
    )
    op.create_index(op.f('ix_page_bands_key'), 'page_bands', ['key'], unique=False)


def downgrade() -> None:
    op.drop_table('page_bands')
    op.drop_column('chapters', 'match_report')
    op.drop_column('pages', 'fingerprint')
    op.add_column('pages', sa.Column('fingerprint', sa.String(), nullable=True))
