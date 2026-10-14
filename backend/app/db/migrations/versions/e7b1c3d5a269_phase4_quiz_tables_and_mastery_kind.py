"""phase 4 step 0: add quiz to mastery_events.kind and create quizzes, quiz_questions, quiz_responses

Revision ID: e7b1c3d5a269
Revises: d6a9b2e4f158
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7b1c3d5a269"
down_revision: Union[str, None] = "d6a9b2e4f158"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=10), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=True),
        sa.Column("student_id", sa.Uuid(), nullable=True),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("chapter_id", sa.Uuid(), nullable=True),
        sa.Column("assignment_id", sa.Uuid(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("question_count", sa.Integer(), server_default="10", nullable=False),
        sa.Column("status", sa.String(length=10), server_default="open", nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("kind IN ('teacher','practice')", name="ck_quiz_kind"),
        sa.CheckConstraint("status IN ('open','submitted')", name="ck_quiz_status"),
        sa.CheckConstraint("question_count >= 1 AND question_count <= 30", name="ck_quiz_question_count"),
        sa.CheckConstraint(
            "(kind = 'teacher' AND teacher_id IS NOT NULL) OR (kind = 'practice' AND student_id IS NOT NULL)",
            name="ck_quiz_owner",
        ),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quizzes_teacher_id"), "quizzes", ["teacher_id"])
    op.create_index(op.f("ix_quizzes_student_id"), "quizzes", ["student_id"])
    op.create_index(op.f("ix_quizzes_book_id"), "quizzes", ["book_id"])
    op.create_index(op.f("ix_quizzes_chapter_id"), "quizzes", ["chapter_id"])
    op.create_index(op.f("ix_quizzes_assignment_id"), "quizzes", ["assignment_id"])

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=True),
        sa.Column("related_concept_id", sa.Uuid(), nullable=True),
        sa.Column("question_type", sa.String(length=16), server_default="recall", nullable=False),
        sa.Column("answer_format", sa.String(length=16), server_default="mcq", nullable=False),
        sa.Column("status", sa.String(length=8), server_default="pending", nullable=False),
        sa.Column("question", sa.Text(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("correct_index", sa.Integer(), nullable=True),
        sa.Column("expected_answer", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), server_default="", nullable=False),
        sa.CheckConstraint("status IN ('pending','ready','failed')", name="ck_quiz_question_status"),
        sa.CheckConstraint("question_type IN ('recall','application','cross_concept')", name="ck_quiz_question_type"),
        sa.CheckConstraint("answer_format IN ('mcq','short_answer')", name="ck_quiz_answer_format"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["related_concept_id"], ["concepts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_questions_quiz_id"), "quiz_questions", ["quiz_id"])
    op.create_index(op.f("ix_quiz_questions_concept_id"), "quiz_questions", ["concept_id"])

    op.create_table(
        "quiz_responses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quiz_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=False),
        sa.Column("chosen_index", sa.Integer(), nullable=True),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("correct", sa.Boolean(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("score IS NULL OR (score >= 0 AND score <= 1)", name="ck_quiz_response_score_range"),
        sa.ForeignKeyConstraint(["question_id"], ["quiz_questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_responses_quiz_id"), "quiz_responses", ["quiz_id"])
    op.create_index(op.f("ix_quiz_responses_question_id"), "quiz_responses", ["question_id"])
    op.create_index(op.f("ix_quiz_responses_student_id"), "quiz_responses", ["student_id"])

    with op.batch_alter_table("mastery_events") as batch:
        batch.add_column(sa.Column("quiz_id", sa.Uuid(), nullable=True))
        batch.create_index(op.f("ix_mastery_events_quiz_id"), ["quiz_id"])
        batch.create_foreign_key("fk_mastery_events_quiz_id", "quizzes", ["quiz_id"], ["id"], ondelete="SET NULL")
        batch.drop_constraint("ck_mastery_kind", type_="check")
        batch.drop_constraint("ck_mastery_check_scored", type_="check")
        batch.drop_constraint("ck_mastery_only_checks_score", type_="check")
        batch.create_check_constraint("ck_mastery_kind", "kind IN ('check','quiz','doubt','propagated')")
        batch.create_check_constraint(
            "ck_mastery_check_scored",
            "kind NOT IN ('check','quiz') OR (score IS NOT NULL AND asked IS NOT NULL AND correct IS NOT NULL)",
        )
        batch.create_check_constraint("ck_mastery_only_checks_score", "kind IN ('check','quiz') OR score IS NULL")


def downgrade() -> None:
    op.execute("DELETE FROM mastery_events WHERE kind = 'quiz'")
    with op.batch_alter_table("mastery_events") as batch:
        batch.drop_constraint("ck_mastery_only_checks_score", type_="check")
        batch.drop_constraint("ck_mastery_check_scored", type_="check")
        batch.drop_constraint("ck_mastery_kind", type_="check")
        batch.create_check_constraint("ck_mastery_kind", "kind IN ('check','doubt','propagated')")
        batch.create_check_constraint(
            "ck_mastery_check_scored",
            "kind <> 'check' OR (score IS NOT NULL AND asked IS NOT NULL AND correct IS NOT NULL)",
        )
        batch.create_check_constraint("ck_mastery_only_checks_score", "kind = 'check' OR score IS NULL")
        batch.drop_constraint("fk_mastery_events_quiz_id", type_="foreignkey")
        batch.drop_index(op.f("ix_mastery_events_quiz_id"))
        batch.drop_column("quiz_id")

    op.drop_index(op.f("ix_quiz_responses_student_id"), table_name="quiz_responses")
    op.drop_index(op.f("ix_quiz_responses_question_id"), table_name="quiz_responses")
    op.drop_index(op.f("ix_quiz_responses_quiz_id"), table_name="quiz_responses")
    op.drop_table("quiz_responses")

    op.drop_index(op.f("ix_quiz_questions_concept_id"), table_name="quiz_questions")
    op.drop_index(op.f("ix_quiz_questions_quiz_id"), table_name="quiz_questions")
    op.drop_table("quiz_questions")

    op.drop_index(op.f("ix_quizzes_assignment_id"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_chapter_id"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_book_id"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_student_id"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_teacher_id"), table_name="quizzes")
    op.drop_table("quizzes")