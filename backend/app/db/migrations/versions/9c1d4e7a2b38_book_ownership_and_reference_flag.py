"""book ownership and reference flag

Development reset note: private teacher-owned books are intentionally removed from
this schema. After this change the database must be reset/re-seeded because the old
ownership model is no longer compatible.
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
    op.add_column('books', sa.Column('owner_student_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_books_owner_student', 'books', 'users', ['owner_student_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_books_is_reference'), 'books', ['is_reference'], unique=False)
    op.create_index(op.f('ix_books_owner_student_id'), 'books', ['owner_student_id'], unique=False)

    # Fresh/reference corpus only. Any old private test books are discarded by design.
    op.execute("DELETE FROM books WHERE is_reference = false")
    op.execute("UPDATE books SET is_reference = true WHERE owner_student_id IS NULL")

    op.execute("""
        ALTER TABLE books ADD CONSTRAINT ck_book_reference_xor_owner
        CHECK ((is_reference AND owner_student_id IS NULL) OR (NOT is_reference AND owner_student_id IS NOT NULL))
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_book_reference_xor_owner")
    op.drop_index(op.f('ix_books_owner_student_id'), table_name='books')
    op.drop_index(op.f('ix_books_is_reference'), table_name='books')
    op.drop_constraint('fk_books_owner_student', 'books', type_='foreignkey')
    op.drop_column('books', 'owner_student_id')
    op.drop_column('books', 'is_reference')
