"""the append-only mastery log, with the doubts already asked back-filled (Phase 3 step 6)

Revision ID: d6a9b2e4f158
Revises: c5f8a1d3e947
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d6a9b2e4f158"
down_revision: Union[str, None] = "c5f8a1d3e947"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mastery_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("concept_name", sa.String(length=300), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("asked", sa.Integer(), nullable=True),
        sa.Column("correct", sa.Integer(), nullable=True),
        sa.Column("assignment_id", sa.Uuid(), nullable=True),
        sa.Column("check_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("source_concept_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("kind IN ('check','doubt','propagated')", name="ck_mastery_kind"),
        sa.CheckConstraint("kind <> 'propagated' OR (reason IS NOT NULL AND reason <> '')", name="ck_mastery_propagated_reason"),
        sa.CheckConstraint("kind <> 'check' OR (score IS NOT NULL AND asked IS NOT NULL AND correct IS NOT NULL)", name="ck_mastery_check_scored"),
        sa.CheckConstraint("kind = 'check' OR score IS NULL", name="ck_mastery_only_checks_score"),
        sa.CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_mastery_score_range"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["check_id"], ["assignment_checks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mastery_events_student_id"), "mastery_events", ["student_id"])
    op.create_index(op.f("ix_mastery_events_concept_id"), "mastery_events", ["concept_id"])
    op.create_index(op.f("ix_mastery_events_check_id"), "mastery_events", ["check_id"])
    # Step 3 kept the doubt row itself as the log; from now on a `doubt` event is written with it, so the doubts already asked
    # (answered against a concept) are carried over once, oldest first.
    op.execute(
        "INSERT INTO mastery_events (student_id, concept_id, concept_name, kind, assignment_id, created_at) "
        "SELECT d.student_id, d.concept_id, LEFT(c.name, 300), 'doubt', d.assignment_id, d.created_at "
        "FROM doubts d JOIN concepts c ON c.id = d.concept_id WHERE d.concept_id IS NOT NULL ORDER BY d.created_at, d.id"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_mastery_events_check_id"), table_name="mastery_events")
    op.drop_index(op.f("ix_mastery_events_concept_id"), table_name="mastery_events")
    op.drop_index(op.f("ix_mastery_events_student_id"), table_name="mastery_events")
    op.drop_table("mastery_events")
