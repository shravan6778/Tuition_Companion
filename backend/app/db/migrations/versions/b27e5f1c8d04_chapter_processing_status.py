"""chapter processing status

Revision ID: b27e5f1c8d04
Revises: 9c1d4e7a2b38
Create Date: 2026-10-04

Chapters get a processing lifecycle (empty -> processing -> ready | failed), the stored source file
(for retry) and its hash (identical re-upload is a no-op). Existing chapters that already have pages
become 'ready'; the rest are 'empty'.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b27e5f1c8d04'
down_revision: Union[str, None] = '9c1d4e7a2b38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapters', sa.Column('status', sa.String(length=16), server_default='empty', nullable=False))
    op.add_column('chapters', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('chapters', sa.Column('source_file', sa.String(), nullable=True))
    op.add_column('chapters', sa.Column('source_sha256', sa.String(length=64), nullable=True))
    op.add_column('chapters', sa.Column('processing_started_at', sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE chapters SET status = 'ready' WHERE EXISTS (SELECT 1 FROM pages WHERE pages.chapter_id = chapters.id)")
    op.create_check_constraint('ck_chapter_status', 'chapters', "status IN ('empty','processing','ready','failed')")


def downgrade() -> None:
    op.drop_constraint('ck_chapter_status', 'chapters', type_='check')
    op.drop_column('chapters', 'processing_started_at')
    op.drop_column('chapters', 'source_sha256')
    op.drop_column('chapters', 'source_file')
    op.drop_column('chapters', 'error_message')
    op.drop_column('chapters', 'status')
