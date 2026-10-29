"""Private student-owned books: books.owner_student_id.

Revision ID: a1c5e7b9d302
Revises: f3a8c1d9e620
Create Date: 2026-10-29

A book is now reference content OR owned by one student. The teacher-owned branch is still accepted
(transitional, see models/content.py) so existing rows and the teacher upload routes keep working until the
uploads move to the student side. The constraint is swapped with NOT VALID, like the one it replaces, so legacy
rows never block the migration; it is enforced for every new or updated row.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1c5e7b9d302"
down_revision: Union[str, Sequence[str], None] = "f3a8c1d9e620"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_OLD = "(is_reference AND owner_teacher_id IS NULL) OR (NOT is_reference AND owner_teacher_id IS NOT NULL)"
_NEW = (
    "(is_reference AND owner_teacher_id IS NULL AND owner_student_id IS NULL)"
    " OR (NOT is_reference AND owner_student_id IS NOT NULL AND owner_teacher_id IS NULL)"
    " OR (NOT is_reference AND owner_teacher_id IS NOT NULL AND owner_student_id IS NULL)"
)


def upgrade() -> None:
    op.add_column("books", sa.Column("owner_student_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_books_owner_student", "books", "users", ["owner_student_id"], ["id"], ondelete="CASCADE")
    op.create_index(op.f("ix_books_owner_student_id"), "books", ["owner_student_id"], unique=False)
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_book_reference_xor_owner")
    op.execute(f"ALTER TABLE books ADD CONSTRAINT ck_book_reference_xor_owner CHECK ({_NEW}) NOT VALID")


def downgrade() -> None:
    # Student-owned books cannot satisfy the old constraint, so they go first (their chapters, pages,
    # embeddings and links cascade). Stored PDFs and Memgraph nodes are not touched by this.
    op.execute("DELETE FROM books WHERE owner_student_id IS NOT NULL")
    op.execute("ALTER TABLE books DROP CONSTRAINT IF EXISTS ck_book_reference_xor_owner")
    op.execute(f"ALTER TABLE books ADD CONSTRAINT ck_book_reference_xor_owner CHECK ({_OLD}) NOT VALID")
    op.drop_index(op.f("ix_books_owner_student_id"), table_name="books")
    op.drop_constraint("fk_books_owner_student", "books", type_="foreignkey")
    op.drop_column("books", "owner_student_id")
