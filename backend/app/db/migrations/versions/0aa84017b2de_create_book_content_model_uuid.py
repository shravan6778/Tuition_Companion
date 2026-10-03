"""create_book_content_model_uuid

Revision ID: 0aa84017b2de
Revises: 483e86509e12
Create Date: 2026-09-30 09:54:46.303627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0aa84017b2de'
down_revision: Union[str, None] = '483e86509e12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cleanly drop obsolete legacy tables with CASCADE to prevent dependency conflicts
    op.execute("DROP TABLE IF EXISTS chapter_concepts CASCADE;")
    op.execute("DROP TABLE IF EXISTS chapter_extractions CASCADE;")
    op.execute("DROP TABLE IF EXISTS room_subjects CASCADE;")
    op.execute("DROP TABLE IF EXISTS chapters CASCADE;")
    op.execute("DROP TABLE IF EXISTS subjects CASCADE;")

    # 2. Create books table
    op.create_table(
        'books',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('board', sa.String(), nullable=True),
        sa.Column('class_name', sa.String(), nullable=True),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('publisher', sa.String(), nullable=True),
        sa.Column('edition', sa.String(), nullable=True),
        sa.Column('is_customized', sa.Boolean(), nullable=True),
        sa.Column('school', sa.String(), nullable=True),
        sa.Column('variant_of_id', sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(['variant_of_id'], ['books.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_board'), 'books', ['board'], unique=False)
    op.create_index(op.f('ix_books_class_name'), 'books', ['class_name'], unique=False)
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    op.create_index(op.f('ix_books_publisher'), 'books', ['publisher'], unique=False)
    op.create_index(op.f('ix_books_subject'), 'books', ['subject'], unique=False)

    # 3. Create student_book association table
    op.create_table(
        'student_book',
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id', 'book_id')
    )

    # 4. Create chapters table
    op.create_table(
        'chapters',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('sequence_num', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chapters_id'), 'chapters', ['id'], unique=False)
    op.create_index(op.f('ix_chapters_title'), 'chapters', ['title'], unique=False)

    # 5. Create pages table
    op.create_table(
        'pages',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('layout_data', sa.JSON(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('uploaded_by_id', sa.Uuid(), nullable=True),
        sa.Column('fingerprint', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pages_id'), 'pages', ['id'], unique=False)

    # 6. Create concepts table
    op.create_table(
        'concepts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('page_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['page_id'], ['pages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_concepts_id'), 'concepts', ['id'], unique=False)
    op.create_index(op.f('ix_concepts_name'), 'concepts', ['name'], unique=False)


def downgrade() -> None:
    op.drop_table('concepts')
    op.drop_table('pages')
    op.drop_table('chapters')
    op.drop_table('student_book')
    op.drop_table('books')