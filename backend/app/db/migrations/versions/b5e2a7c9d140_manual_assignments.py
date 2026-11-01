"""manual assignments (school homework) and their submissions

Revision ID: b5e2a7c9d140
Revises: a1f4c8e2d7b6
Create Date: 2026-10-31

A `manual` assignment points at no book: a free-text subject (the existing `subject` column), a title and a new
`description`. It is verified by a photo or spoken answer from the student plus the teacher's verdict, stored in
`manual_submissions`. The assignments table never held a book_id (an assignment is curriculum metadata), so there is
nothing to make nullable here; the create request's `book_id` becomes optional in the API instead.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b5e2a7c9d140"
down_revision: Union[str, None] = "a1f4c8e2d7b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("assignments", sa.Column("description", sa.Text(), nullable=True))
    with op.batch_alter_table("assignments") as batch:
        batch.drop_constraint("ck_assignment_level", type_="check")
        batch.create_check_constraint("ck_assignment_level", "level IN ('subject','chapter','concept','exercise','items','manual')")
        batch.create_check_constraint("ck_assignment_manual_shape", "level <> 'manual' OR (chapter_title IS NULL AND item_label IS NULL)")

    op.create_table(
        "manual_submissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=8), nullable=False),
        sa.Column("photo_path", sa.String(length=300), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("verdict", sa.String(length=10), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("source IN ('photo','voice')", name="ck_submission_source"),
        sa.CheckConstraint("verdict IS NULL OR verdict IN ('good','needs_work','redo')", name="ck_submission_verdict"),
        sa.CheckConstraint(
            "(source = 'photo' AND photo_path IS NOT NULL) OR (source = 'voice' AND text IS NOT NULL AND text <> '')",
            name="ck_submission_has_work"),
        sa.CheckConstraint("(verdict IS NULL) = (reviewed_at IS NULL)", name="ck_submission_reviewed_together"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_manual_submissions_assignment_id"), "manual_submissions", ["assignment_id"])
    op.create_index(op.f("ix_manual_submissions_student_id"), "manual_submissions", ["student_id"])


def downgrade() -> None:
    # A manual task has no meaning in the old schema (its level is not allowed), so those rows go first; their submissions
    # follow through the foreign key. Stored photos are content-addressed and may be shared, so the files are left alone.
    op.drop_index(op.f("ix_manual_submissions_student_id"), table_name="manual_submissions")
    op.drop_index(op.f("ix_manual_submissions_assignment_id"), table_name="manual_submissions")
    op.drop_table("manual_submissions")
    op.execute("DELETE FROM assignments WHERE level = 'manual'")
    with op.batch_alter_table("assignments") as batch:
        batch.drop_constraint("ck_assignment_manual_shape", type_="check")
        batch.drop_constraint("ck_assignment_level", type_="check")
        batch.create_check_constraint("ck_assignment_level", "level IN ('subject','chapter','concept','exercise','items')")
    op.drop_column("assignments", "description")
