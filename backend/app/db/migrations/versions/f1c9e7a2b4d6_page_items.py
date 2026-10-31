"""page items and item embeddings

Revision ID: f1c9e7a2b4d6
Revises: e7b1c3d5a269
Create Date: 2026-10-31
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "f1c9e7a2b4d6"
down_revision: Union[str, None] = "f3a8c1d9e620"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "page_items",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("page_id", UUID(as_uuid=True), sa.ForeignKey("pages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(length=24), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("solution_text", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "kind IN ('concept','example','exercise_question','diagram','activity','sidebar')",
            name="ck_page_item_kind",
        ),
    )
    op.create_index("ix_page_items_page_id", "page_items", ["page_id"])

    op.create_table(
        "page_item_concepts",
        sa.Column("item_id", UUID(as_uuid=True), sa.ForeignKey("page_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("concept_id", UUID(as_uuid=True), sa.ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True),
    )

    op.add_column("content_embeddings", sa.Column("item_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_content_embeddings_item_id", "content_embeddings", "page_items", ["item_id"], ["id"], ondelete="CASCADE")
    op.create_unique_constraint("uq_embedding_item", "content_embeddings", ["item_id"])
    op.drop_constraint("ck_embedding_page_xor_concept", "content_embeddings", type_="check")
    op.create_check_constraint(
        "ck_embedding_page_xor_concept_item",
        "content_embeddings",
        "(page_id IS NOT NULL AND concept_id IS NULL AND item_id IS NULL) OR "
        "(page_id IS NULL AND concept_id IS NOT NULL AND item_id IS NULL) OR "
        "(page_id IS NULL AND concept_id IS NULL AND item_id IS NOT NULL)",
    )

def downgrade() -> None:
    op.drop_constraint("ck_embedding_page_xor_concept_item", "content_embeddings", type_="check")
    op.create_check_constraint(
        "ck_embedding_page_xor_concept",
        "content_embeddings",
        "(page_id IS NOT NULL AND concept_id IS NULL) OR (page_id IS NULL AND concept_id IS NOT NULL)",
    )
    op.drop_constraint("uq_embedding_item", "content_embeddings", type_="unique")
    op.drop_constraint("fk_content_embeddings_item_id", "content_embeddings", type_="foreignkey")
    op.drop_column("content_embeddings", "item_id")
    op.drop_table("page_item_concepts")
    op.drop_index("ix_page_items_page_id", table_name="page_items")
    op.drop_table("page_items")
