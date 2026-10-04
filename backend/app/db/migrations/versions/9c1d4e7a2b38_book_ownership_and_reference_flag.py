"""book ownership and reference flag

Revision ID: 9c1d4e7a2b38
Revises: 0aa84017b2de
Create Date: 2026-10-03

Books become either platform-wide reference content (is_reference, no owner) or a private upload
owned by one teacher (owner_teacher_id). Existing rows are backfilled:
  1. a book whose pages were uploaded by a teacher -> owned by that teacher
  2. remaining ownerless NCERT books (the seeded corpus) -> reference
  3. anything left is an orphan: it stays as-is (nobody can see it) and should be deleted by hand.
The CHECK constraint is added NOT VALID so these legacy orphans don't block the migration;
it is enforced for every new/updated row.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9c1d4e7a2b38'
down_revision: Union[str, None] = '0aa84017b2de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('books', sa.Column('is_reference', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('books', sa.Column('owner_teacher_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_books_owner_teacher', 'books', 'users', ['owner_teacher_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_books_is_reference'), 'books', ['is_reference'], unique=False)
    op.create_index(op.f('ix_books_owner_teacher_id'), 'books', ['owner_teacher_id'], unique=False)

    op.execute("""
        UPDATE books b SET owner_teacher_id = sub.teacher_id
        FROM (
            SELECT c.book_id, (array_agg(p.uploaded_by_id ORDER BY p.page_number))[1] AS teacher_id
            FROM pages p
            JOIN chapters c ON c.id = p.chapter_id
            JOIN users u ON u.id = p.uploaded_by_id AND u.role = 'teacher'
            GROUP BY c.book_id
        ) sub
        WHERE b.id = sub.book_id
    """)
    op.execute("UPDATE books SET is_reference = true WHERE owner_teacher_id IS NULL AND lower(publisher) = 'ncert'")

    op.execute("""
        ALTER TABLE books ADD CONSTRAINT ck_book_reference_xor_owner
        CHECK ((is_reference AND owner_teacher_id IS NULL) OR (NOT is_reference AND owner_teacher_id IS NOT NULL))
        NOT VALID
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_book_reference_xor_owner")
    op.drop_index(op.f('ix_books_owner_teacher_id'), table_name='books')
    op.drop_index(op.f('ix_books_is_reference'), table_name='books')
    op.drop_constraint('fk_books_owner_teacher', 'books', type_='foreignkey')
    op.drop_column('books', 'owner_teacher_id')
    op.drop_column('books', 'is_reference')
