"""written and spoken answers: long_answer format, key points, input_method, score_source, mastery corrections

Revision ID: d3a7b1c9e582
Revises: b5e2a7c9d140
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d3a7b1c9e582"
down_revision: Union[str, None] = "b5e2a7c9d140"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# columns every written / spoken answer row has (models/answers.py WrittenAnswerMixin)
def _answer_columns() -> list[sa.Column]:
    return [
        sa.Column("input_method", sa.String(length=8), server_default="typed", nullable=False),
        sa.Column("transcript_language", sa.String(length=8), nullable=True),
        sa.Column("points_hit", sa.JSON(), nullable=True),
        sa.Column("points_missed", sa.JSON(), nullable=True),
        sa.Column("score_source", sa.String(length=8), nullable=True),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("needs_confirm", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("teacher_feedback", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    # tests
    op.drop_constraint("ck_quiz_answer_format", "quiz_questions", type_="check")
    op.create_check_constraint("ck_quiz_answer_format", "quiz_questions", "answer_format IN ('mcq','short_answer','long_answer')")
    op.add_column("quiz_questions", sa.Column("key_points", sa.JSON(), nullable=True))
    for col in _answer_columns():
        op.add_column("quiz_responses", col)
    op.create_check_constraint("ck_quiz_response_input_method", "quiz_responses", "input_method IN ('typed','voice')")
    op.create_check_constraint("ck_quiz_response_score_source", "quiz_responses", "score_source IS NULL OR score_source IN ('ai','teacher')")
    # assignment checks
    op.add_column("assignment_checks", sa.Column("subject", sa.String(length=120), nullable=True))
    op.add_column("check_questions", sa.Column("answer_format", sa.String(length=16), server_default="mcq", nullable=False))
    op.add_column("check_questions", sa.Column("expected_answer", sa.Text(), nullable=True))
    op.add_column("check_questions", sa.Column("key_points", sa.JSON(), nullable=True))
    op.add_column("check_questions", sa.Column("answer_text", sa.Text(), nullable=True))
    op.add_column("check_questions", sa.Column("score", sa.Float(), nullable=True))
    op.add_column("check_questions", sa.Column("feedback", sa.Text(), nullable=True))
    for col in _answer_columns():
        op.add_column("check_questions", col)
    op.create_check_constraint("ck_check_question_format", "check_questions", "answer_format IN ('mcq','short_answer','long_answer')")
    op.create_check_constraint("ck_check_question_input_method", "check_questions", "input_method IN ('typed','voice')")
    op.create_check_constraint("ck_check_question_score_source", "check_questions", "score_source IS NULL OR score_source IN ('ai','teacher')")
    op.create_check_constraint("ck_check_question_score_range", "check_questions", "score IS NULL OR (score >= 0 AND score <= 1)")
    # mastery: a teacher's re-mark replaces an earlier event when the state is read
    op.add_column("mastery_events", sa.Column("corrects_event_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("fk_mastery_corrects_event", "mastery_events", "mastery_events", ["corrects_event_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_mastery_corrects_event", "mastery_events", type_="foreignkey")
    op.drop_column("mastery_events", "corrects_event_id")
    for name in ("ck_check_question_score_range", "ck_check_question_score_source", "ck_check_question_input_method", "ck_check_question_format"):
        op.drop_constraint(name, "check_questions", type_="check")
    for c in ("reviewed_at", "reviewed_by", "teacher_feedback", "needs_confirm", "ai_score", "score_source", "points_missed", "points_hit",
              "transcript_language", "input_method", "feedback", "score", "answer_text", "key_points", "expected_answer", "answer_format"):
        op.drop_column("check_questions", c)
    op.drop_column("assignment_checks", "subject")
    op.drop_constraint("ck_quiz_response_score_source", "quiz_responses", type_="check")
    op.drop_constraint("ck_quiz_response_input_method", "quiz_responses", type_="check")
    for c in ("reviewed_at", "reviewed_by", "teacher_feedback", "needs_confirm", "ai_score", "score_source", "points_missed", "points_hit",
              "transcript_language", "input_method"):
        op.drop_column("quiz_responses", c)
    op.drop_column("quiz_questions", "key_points")
    op.drop_constraint("ck_quiz_answer_format", "quiz_questions", type_="check")
    op.create_check_constraint("ck_quiz_answer_format", "quiz_questions", "answer_format IN ('mcq','short_answer')")
