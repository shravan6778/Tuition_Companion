"""cross-chapter prerequisite edges

Revision ID: c8f2a4b6d913
Revises: b3d7f1a9c562
Create Date: 2026-10-09

`cross_chapter_edges` links a concept to prerequisites in EARLIER chapters of the same book. It is separate from
`concept_edges` so every chapter's own graph stays a self-contained DAG. Existing books have no rows until
`python -m app.db.crosslink` is run (or a chapter finishes processing).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c8f2a4b6d913'
down_revision: Union[str, None] = 'b3d7f1a9c562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cross_chapter_edges',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('concept_id', sa.Uuid(), nullable=False),
        sa.Column('prerequisite_id', sa.Uuid(), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=True),
        sa.CheckConstraint('concept_id <> prerequisite_id', name='ck_cross_edge_not_self'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['concept_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prerequisite_id'], ['concepts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('concept_id', 'prerequisite_id', name='uq_cross_chapter_edge'),
    )
    op.create_index(op.f('ix_cross_chapter_edges_chapter_id'), 'cross_chapter_edges', ['chapter_id'])
    op.create_index(op.f('ix_cross_chapter_edges_concept_id'), 'cross_chapter_edges', ['concept_id'])
    op.create_index(op.f('ix_cross_chapter_edges_prerequisite_id'), 'cross_chapter_edges', ['prerequisite_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_cross_chapter_edges_prerequisite_id'), table_name='cross_chapter_edges')
    op.drop_index(op.f('ix_cross_chapter_edges_concept_id'), table_name='cross_chapter_edges')
    op.drop_index(op.f('ix_cross_chapter_edges_chapter_id'), table_name='cross_chapter_edges')
    op.drop_table('cross_chapter_edges')
