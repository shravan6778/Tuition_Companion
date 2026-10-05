"""upload drafts and chapter requests

Revision ID: e6c4f9a3b027
Revises: d5b3e8f2a916
Create Date: 2026-10-04

books: how the metadata was obtained (front pages vs manual), what the system extracted, the stored front pages.
upload_drafts: front pages / whole-textbook uploads waiting for the teacher's confirmation.
chapter_requests: student -> teacher "please add this chapter".
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e6c4f9a3b027'
down_revision: Union[str, None] = 'd5b3e8f2a916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('books', sa.Column('metadata_source', sa.String(length=12), server_default='manual', nullable=False))
    op.add_column('books', sa.Column('extracted_metadata', sa.JSON(), nullable=True))
    op.add_column('books', sa.Column('front_pages_file', sa.String(), nullable=True))

    op.create_table(
        'upload_drafts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('teacher_id', sa.Uuid(), nullable=False),
        sa.Column('kind', sa.String(length=12), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=True),
        sa.Column('source_file', sa.String(), nullable=False),
        sa.Column('source_sha256', sa.String(length=64), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_upload_drafts_teacher_id'), 'upload_drafts', ['teacher_id'], unique=False)

    op.create_table(
        'chapter_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('teacher_id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('chapter_id', sa.Uuid(), nullable=True),
        sa.Column('chapter_hint', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=10), server_default='open', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('open','fulfilled','dismissed','cancelled')", name='ck_chapter_request_status'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chapter_requests_student_id'), 'chapter_requests', ['student_id'], unique=False)
    op.create_index(op.f('ix_chapter_requests_teacher_id'), 'chapter_requests', ['teacher_id'], unique=False)
    op.create_index(op.f('ix_chapter_requests_book_id'), 'chapter_requests', ['book_id'], unique=False)


def downgrade() -> None:
    op.drop_table('chapter_requests')
    op.drop_table('upload_drafts')
    op.drop_column('books', 'front_pages_file')
    op.drop_column('books', 'extracted_metadata')
    op.drop_column('books', 'metadata_source')
