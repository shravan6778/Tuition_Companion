"""Admin, security and monitoring: account status, usage events, audit log, app settings, teacher invites.

Existing users stay 'active' (the column's default), so nobody is locked out by this migration.

Revision ID: a7f3c9d1e5b8
Revises: d3a7b1c9e582
Create Date: 2026-11-02
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7f3c9d1e5b8"
down_revision: Union[str, Sequence[str], None] = "d3a7b1c9e582"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("status", sa.String(length=12), server_default="active", nullable=False))
        batch.add_column(sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("quota_overrides", sa.JSON(), nullable=True))
        batch.create_check_constraint("ck_user_status", "status IN ('active','pending','disabled')")

    op.create_table(
        "usage_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("operation", sa.String(length=60), nullable=False),
        sa.Column("quota", sa.String(length=20), nullable=False),
        sa.Column("units", sa.Integer(), nullable=False),
        sa.Column("unit_type", sa.String(length=10), nullable=False),
        sa.Column("estimated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("status", sa.String(length=10), server_default="ok", nullable=False),
        sa.Column("request_id", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usage_events_created_at"), "usage_events", ["created_at"])
    op.create_index(op.f("ix_usage_events_user_id"), "usage_events", ["user_id"])
    op.create_index("ix_usage_events_user_quota_created", "usage_events", ["user_id", "quota", "created_at"])
    op.create_index("ix_usage_events_quota_created", "usage_events", ["quota", "created_at"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("actor_username", sa.String(length=30), nullable=True),
        sa.Column("actor_role", sa.String(length=12), nullable=True),
        sa.Column("action", sa.String(length=60), nullable=False),
        sa.Column("target_type", sa.String(length=30), nullable=True),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("target_label", sa.String(length=160), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        sa.Column("request_id", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_log_created_at"), "audit_log", ["created_at"])
    op.create_index(op.f("ix_audit_log_actor_user_id"), "audit_log", ["actor_user_id"])
    op.create_index("ix_audit_log_action_created", "audit_log", ["action", "created_at"])

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=60), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.String(length=30), nullable=True),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "teacher_invites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("note", sa.String(length=120), nullable=True),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_by_id", sa.Uuid(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["used_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teacher_invites_code_hash"), "teacher_invites", ["code_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_teacher_invites_code_hash"), table_name="teacher_invites")
    op.drop_table("teacher_invites")
    op.drop_table("app_settings")
    op.drop_index("ix_audit_log_action_created", table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_actor_user_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_created_at"), table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_usage_events_quota_created", table_name="usage_events")
    op.drop_index("ix_usage_events_user_quota_created", table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_user_id"), table_name="usage_events")
    op.drop_index(op.f("ix_usage_events_created_at"), table_name="usage_events")
    op.drop_table("usage_events")
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("ck_user_status", type_="check")
        batch.drop_column("quota_overrides")
        batch.drop_column("status_changed_at")
        batch.drop_column("status")
