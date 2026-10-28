"""Room join approval requests.

Revision ID: f3a8c1d9e620
Revises: e1b4c7d9a203
Create Date: 2026-10-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f3a8c1d9e620"
down_revision: Union[str, Sequence[str], None] = ("a3d9e2c6f581", "c1d4e6f8a2b0")
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "room_join_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=12), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", "user_id", name="uq_room_join_request"),
    )
    op.create_index(op.f("ix_room_join_requests_room_id"), "room_join_requests", ["room_id"], unique=False)
    op.create_index(op.f("ix_room_join_requests_user_id"), "room_join_requests", ["user_id"], unique=False)
    op.create_index(op.f("ix_room_join_requests_status"), "room_join_requests", ["status"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_room_join_requests_status"), table_name="room_join_requests")
    op.drop_index(op.f("ix_room_join_requests_user_id"), table_name="room_join_requests")
    op.drop_index(op.f("ix_room_join_requests_room_id"), table_name="room_join_requests")
    op.drop_table("room_join_requests")
