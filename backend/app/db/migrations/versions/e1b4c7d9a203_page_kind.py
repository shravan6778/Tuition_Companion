"""page_kind: what each page is (content / recap / exercise / other)

Revision ID: e1b4c7d9a203
Revises: d9a3b5c7e124
Create Date: 2026-10-12

Phase 2 already decided a page's kind while reading it but threw the answer away. Phase 3 needs it: an exercise
assignment ("Ex.9.5") is scoped from the chapter's exercise pages. Existing rows default to `content`; run
`python -m app.db.backfill_page_kind` to label them (no OCR, no LLM calls).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e1b4c7d9a203'
down_revision: Union[str, None] = 'd9a3b5c7e124'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('pages') as batch:
        batch.add_column(sa.Column('page_kind', sa.String(length=10), server_default='content', nullable=False))
        batch.create_check_constraint('ck_page_kind', "page_kind IN ('content','recap','exercise','other')")


def downgrade() -> None:
    with op.batch_alter_table('pages') as batch:
        batch.drop_constraint('ck_page_kind', type_='check')
        batch.drop_column('page_kind')
