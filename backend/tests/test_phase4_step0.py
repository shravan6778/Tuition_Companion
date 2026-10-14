"""Phase 4 Step 0 tests: `quiz` in mastery_events, unified mastery state, and `quizzes` / `quiz_questions` / `quiz_responses`."""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.assessment import mastery
from app.models import (
    AnswerFormat, Book, Chapter, ChapterStatus, Concept, ConceptEdge, MasteryEvent, Page, QuestionType, Quiz, QuizKind,
    QuizQuestion, QuizResponse, Role, User,
)


def _seed_graph(db):
    teacher = User(supertokens_user_id="st-t-p4s0", name="Teacher", username="tp4s0", phone="9000000001", role=Role.teacher)
    student = User(supertokens_user_id="st-s-p4s0", name="Student", username="sp4s0", phone="9000000002", role=Role.student, link_code="P4S0CODE")
    db.add_all([teacher, student])
    db.flush()

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()

    chapter = Chapter(book_id=book.id, title="Motion", sequence_num=1, status=ChapterStatus.READY)
    db.add(chapter)
    db.flush()

    page = Page(chapter_id=chapter.id, page_number=1, content_text="Distance, displacement, velocity and acceleration.")
    db.add(page)
    db.flush()

    c1 = Concept(page_id=page.id, name="Displacement", description="Shortest path", name_key="displacement", is_canonical=True, position=0)
    c2 = Concept(page_id=page.id, name="Velocity", description="Rate of change of displacement", name_key="velocity", is_canonical=True, position=1)
    db.add_all([c1, c2])
    db.flush()

    # Velocity depends on Displacement
    db.add(ConceptEdge(chapter_id=chapter.id, concept_id=c2.id, prerequisite_id=c1.id, source="llm"))
    db.commit()
    return teacher, student, book, chapter, c1, c2


def test_mastery_events_accepts_quiz_and_enforces_constraints(session_factory):
    with session_factory() as db_session:
        _, student, book, chapter, c1, _ = _seed_graph(db_session)
        quiz = Quiz(kind=QuizKind.PRACTICE, student_id=student.id, book_id=book.id, chapter_id=chapter.id, title="Practice Quiz", question_count=10)
        db_session.add(quiz)
        db_session.flush()

        ev = MasteryEvent(
            student_id=student.id, concept_id=c1.id, concept_name=c1.name,
            kind="quiz", score=0.8, asked=5, correct=4, quiz_id=quiz.id,
        )
        db_session.add(ev)
        db_session.commit()
        assert ev.id is not None

        # A 'quiz' event without score/asked/correct is rejected by ck_mastery_check_scored
        with pytest.raises(IntegrityError):
            with db_session.begin_nested():
                db_session.add(MasteryEvent(student_id=student.id, concept_id=c1.id, concept_name=c1.name, kind="quiz", score=None))
                db_session.flush()

        # An unknown kind is rejected by ck_mastery_kind
        with pytest.raises(IntegrityError):
            with db_session.begin_nested():
                db_session.add(MasteryEvent(student_id=student.id, concept_id=c1.id, concept_name=c1.name, kind="exam", score=0.5, asked=2, correct=1))
                db_session.flush()


def test_record_quiz_propagates_weak_and_clears_at_risk_in_unified_state(session_factory):
    with session_factory() as db_session:
        _, student, book, chapter, c1, c2 = _seed_graph(db_session)
        q1 = Quiz(kind=QuizKind.PRACTICE, student_id=student.id, book_id=book.id, chapter_id=chapter.id, title="Quiz 1", question_count=10)
        db_session.add(q1)
        db_session.flush()

        # Student fails c1 (Displacement) on Quiz 1 -> c1 is weak, c2 (Velocity) is propagated at_risk
        mastery.record_quiz(db_session, student.id, q1.id, None, {c1.id: (2, 0)})
        db_session.commit()

        state = mastery.current_state(db_session, student.id)
        assert state[c1.id].status == mastery.WEAK
        assert state[c1.id].score == 0.0
        assert state[c2.id].status == mastery.AT_RISK
        assert state[c2.id].score is None
        assert "Displacement" in state[c2.id].reason

        # Student later passes c2 (Velocity) on Quiz 2 -> c2's at_risk flag is cleared by the quiz measurement
        q2 = Quiz(kind=QuizKind.PRACTICE, student_id=student.id, book_id=book.id, chapter_id=chapter.id, title="Quiz 2", question_count=10)
        db_session.add(q2)
        db_session.flush()
        mastery.record_quiz(db_session, student.id, q2.id, None, {c2.id: (2, 2)})
        db_session.commit()

        state_after = mastery.current_state(db_session, student.id)
        assert state_after[c2.id].status == mastery.OK
        assert state_after[c2.id].score == 1.0
        assert state_after[c2.id].reason is None
        assert state_after[c1.id].status == mastery.WEAK  # c1 stays weak until tested again


def test_quiz_questions_and_short_answer_responses_persist(session_factory):
    with session_factory() as db_session:
        teacher, student, book, chapter, c1, c2 = _seed_graph(db_session)
        quiz = Quiz(kind=QuizKind.TEACHER, teacher_id=teacher.id, book_id=book.id, chapter_id=chapter.id, title="Motion Full Test", question_count=10)
        quiz.questions = [
            QuizQuestion(
                position=0, concept_id=c1.id, question_type=QuestionType.RECALL, answer_format=AnswerFormat.MCQ,
                status="ready", question="What is displacement?", options=["Shortest path", "Total path", "Speed", "Time"],
                correct_index=0, explanation="Displacement is the shortest distance from initial to final position.",
            ),
            QuizQuestion(
                position=1, concept_id=c2.id, related_concept_id=c1.id,
                question_type=QuestionType.CROSS_CONCEPT, answer_format=AnswerFormat.SHORT_ANSWER,
                status="ready", question="How does velocity relate to displacement when an object returns to its starting point?",
                expected_answer="Displacement is zero, so average velocity is also zero.",
                explanation="Average velocity is displacement divided by time.",
            ),
        ]
        db_session.add(quiz)
        db_session.commit()

        short_q = quiz.questions[1]
        resp = QuizResponse(
            quiz_id=quiz.id, question_id=short_q.id, student_id=student.id,
            answer_text="Because displacement is zero, the average velocity becomes zero.",
            score=0.95, correct=True, feedback="Accurately links zero net displacement to zero average velocity.",
        )
        db_session.add(resp)
        db_session.commit()

        saved = db_session.scalar(select(QuizResponse).where(QuizResponse.quiz_id == quiz.id))
        assert saved.answer_text.startswith("Because displacement")
        assert saved.score == 0.95
        assert saved.correct is True

        # Out-of-range response score is rejected by ck_quiz_response_score_range
        with pytest.raises(IntegrityError):
            with db_session.begin_nested():
                db_session.add(QuizResponse(quiz_id=quiz.id, question_id=short_q.id, student_id=student.id, score=1.5))
                db_session.flush()