"""concept graph

Revision ID: c4a91d6e3f72
Revises: b27e5f1c8d04
Create Date: 2026-10-04

concept_edges (prerequisite -> concept, per chapter), concept ordering/identity columns, and
chapters.graph_report. Existing concepts get position 0, a best-effort name_key and is_canonical=true;
run `python -m app.db.relink_chapters` to build graphs for chapters processed before this migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c4a91d6e3f72'
down_revision: Union[str, None] = 'b27e5f1c8d04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('concepts', sa.Column('position', sa.Integer(), server_default='0', nullable=False))
    op.add_column('concepts', sa.Column('name_key', sa.String(), nullable=True))
    op.add_column('concepts', sa.Column('is_canonical', sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_index(op.f('ix_concepts_name_key'), 'concepts', ['name_key'], unique=False)
    op.add_column('chapters', sa.Column('graph_report', sa.JSON(), nullable=True))

    op.create_table(
        'concept_edges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('concept_id', sa.Uuid(), nullable=False),
        sa.Column('prerequisite_id', sa.Uuid(), nullable=False),
        sa.Column('source', sa.String(length=8), nullable=False),
        sa.CheckConstraint('concept_id <> prerequisite_id', name='ck_concept_edge_not_self'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prerequisite_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', 'prerequisite_id', name='uq_concept_edge'),
    )
    op.create_index(op.f('ix_concept_edges_chapter_id'), 'concept_edges', ['chapter_id'], unique=False)
    op.create_index(op.f('ix_concept_edges_concept_id'), 'concept_edges', ['concept_id'], unique=False)
    op.create_index(op.f('ix_concept_edges_prerequisite_id'), 'concept_edges', ['prerequisite_id'], unique=False)


def downgrade() -> None:
    op.drop_table('concept_edges')
    op.drop_column('chapters', 'graph_report')
    op.drop_index(op.f('ix_concepts_name_key'), table_name='concepts')
    op.drop_column('concepts', 'is_canonical')
    op.drop_column('concepts', 'name_key')
    op.drop_column('concepts', 'position')
