"""embeddings table + graph-sync status on chapters

Revision ID: b3d7f1a9c562
Revises: a8e2c5d7f419
Create Date: 2026-10-07

`content_embeddings` is the durable copy of every embedding vector (raw float32 bytes, one row per page or
canonical concept); Memgraph is rebuilt from it. Chapters get `embedding_status`, `graph_sync_status`,
`index_error` and `indexed_at` so a failed or pending derived copy is visible and retryable. Existing chapters
start as 'pending': run `python -m app.db.sync_graph` once embeddings / Memgraph are configured.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b3d7f1a9c562'
down_revision: Union[str, None] = 'a8e2c5d7f419'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chapters', sa.Column('embedding_status', sa.String(length=10), server_default='pending', nullable=False))
    op.add_column('chapters', sa.Column('graph_sync_status', sa.String(length=10), server_default='pending', nullable=False))
    op.add_column('chapters', sa.Column('index_error', sa.Text(), nullable=True))
    op.add_column('chapters', sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint('ck_chapter_embedding_status', 'chapters',
                               "embedding_status IN ('pending','done','skipped','failed')")
    op.create_check_constraint('ck_chapter_graph_sync_status', 'chapters',
                               "graph_sync_status IN ('pending','done','skipped','failed')")

    op.create_table(
        'content_embeddings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('page_id', sa.Uuid(), nullable=True),
        sa.Column('concept_id', sa.Uuid(), nullable=True),
        sa.Column('model', sa.String(length=60), nullable=False),
        sa.Column('dim', sa.Integer(), nullable=False),
        sa.Column('text_sha256', sa.String(length=64), nullable=False),
        sa.Column('vector', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            '(page_id IS NOT NULL AND concept_id IS NULL) OR (page_id IS NULL AND concept_id IS NOT NULL)',
            name='ck_embedding_page_xor_concept',
        ),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', name='uq_embedding_concept'),
        sa.UniqueConstraint('page_id', name='uq_embedding_page'),
    )
    op.create_index(op.f('ix_content_embeddings_chapter_id'), 'content_embeddings', ['chapter_id'], unique=False)
    op.create_index('ix_embedding_model_hash', 'content_embeddings', ['model', 'text_sha256'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_embedding_model_hash', table_name='content_embeddings')
    op.drop_index(op.f('ix_content_embeddings_chapter_id'), table_name='content_embeddings')
    op.drop_table('content_embeddings')
    op.drop_constraint('ck_chapter_graph_sync_status', 'chapters', type_='check')
    op.drop_constraint('ck_chapter_embedding_status', 'chapters', type_='check')
    op.drop_column('chapters', 'indexed_at')
    op.drop_column('chapters', 'index_error')
    op.drop_column('chapters', 'graph_sync_status')
    op.drop_column('chapters', 'embedding_status')
