"""assignment_items table and the `items` assignment level

Revision ID: a1f4c8e2d7b6
Revises: f1c9e7a2b4d6
Create Date: 2026-10-31

Assignments at finer grain: a teacher can pick specific examples, exercise questions and figures. They are stored as
metadata (kind + label key), resolved against each student's own copy, exactly like assignment_concepts.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1f4c8e2d7b6"
down_revision: Union[str, None] = "f1c9e7a2b4d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assignment_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("assignment_id", sa.Uuid(), nullable=False),
        sa.Column("item_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("item_key", sa.String(length=160), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("kind IN ('example','exercise_question','diagram','activity','sidebar')", name="ck_assignment_item_kind"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["page_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assignment_items_assignment_id"), "assignment_items", ["assignment_id"])
    op.create_index(op.f("ix_assignment_items_item_key"), "assignment_items", ["item_key"])

    with op.batch_alter_table("assignments") as batch:
        batch.drop_constraint("ck_assignment_level", type_="check")
        batch.create_check_constraint("ck_assignment_level", "level IN ('subject','chapter','concept','exercise','items')")


def downgrade() -> None:
    # An `items` assignment has no meaning without its items, so those rows are removed before the old rule returns.
    op.execute("DELETE FROM assignments WHERE level = 'items'")
    with op.batch_alter_table("assignments") as batch:
        batch.drop_constraint("ck_assignment_level", type_="check")
        batch.create_check_constraint("ck_assignment_level", "level IN ('subject','chapter','concept','exercise')")
    op.drop_index(op.f("ix_assignment_items_item_key"), table_name="assignment_items")
    op.drop_index(op.f("ix_assignment_items_assignment_id"), table_name="assignment_items")
    op.drop_table("assignment_items")
