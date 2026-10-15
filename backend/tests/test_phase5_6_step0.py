"""Tests for Phase 5 & 6 Step 0:
  * 0.1 `session_logs` table schema, foreign keys, JSON tags, and non-empty notes check constraint.
  * 0.2 3-event weighted rolling-window mastery in `assessment/mastery.py` (50% latest, 30% previous, 20% oldest),
        single off-day smoothing, rolling-window-driven weak propagation, and explainable reasons for both direct
        `weak` and propagated `at_risk` concepts."""
from datetime import date

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.assessment import mastery
from app.models import (
    Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, Role, SessionLog, User,
)


def _seed_graph(db):
    teacher = User(
        supertokens_user_id="st-p5-t1",
        name="Teacher Five",
        username="teacher_five",
        phone="9000000001",
        role=Role.teacher,
    )
    student = User(
        supertokens_user_id="st-p5-s1",
        name="Student Five",
        username="student_five",
        phone="9000000002",
        role=Role.student,
        link_code="P5S1CODE",
    )
    db.add_all([teacher, student])
    db.flush()

    book = Book(
        board="CBSE",
        class_name="Class 9",
        subject="Mathematics",
        publisher="NCERT",
        is_reference=True,
    )
    db.add(book)
    db.flush()

    chapter = Chapter(
        book_id=book.id,
        title="Polynomials",
        sequence_num=2,
        status=ChapterStatus.READY,
    )
    db.add(chapter)
    db.flush()

    page = Page(
        chapter_id=chapter.id,
        page_number=1,
        content_text="Factoring polynomials relies on basic algebraic identities and degree of a polynomial.",
    )
    db.add(page)
    db.flush()

    c_base = Concept(
        page_id=page.id,
        name="Algebraic Identities",
        description="Standard algebraic expansion formulas",
        name_key="algebraic identities",
        position=0,
        is_canonical=True,
    )
    c_dep = Concept(
        page_id=page.id,
        name="Factoring Polynomials",
        description="Decomposing a polynomial into factors",
        name_key="factoring polynomials",
        position=1,
        is_canonical=True,
    )
    db.add_all([c_base, c_dep])
    db.flush()

    # Factoring Polynomials depends on Algebraic Identities
    db.add(
        ConceptEdge(
            chapter_id=chapter.id,
            concept_id=c_dep.id,
            prerequisite_id=c_base.id,
            source="llm",
        )
    )
    db.commit()
    return teacher, student, c_base, c_dep


def test_session_logs_table_and_constraints(session_factory):
    with session_factory() as db:
        teacher, student, _, _ = _seed_graph(db)

        log = SessionLog(
            student_id=student.id,
            teacher_id=teacher.id,
            session_date=date(2026, 10, 15),
            notes="Covered factoring by grouping; needs extra practice on middle-term splitting.",
            tags=["polynomials", "needs-practice"],
        )
        db.add(log)
        db.commit()

        saved = db.scalar(select(SessionLog).where(SessionLog.student_id == student.id))
        assert saved is not None
        assert saved.teacher_id == teacher.id
        assert saved.session_date == date(2026, 10, 15)
        assert saved.tags == ["polynomials", "needs-practice"]
        assert "middle-term splitting" in saved.notes

        # Empty notes must be rejected by ck_session_log_notes_nonempty
        with pytest.raises(IntegrityError):
            with db.begin_nested():
                db.add(
                    SessionLog(
                        student_id=student.id,
                        teacher_id=teacher.id,
                        session_date=date(2026, 10, 15),
                        notes="",
                        tags=[],
                    )
                )
                db.flush()


def test_rolling_window_weights_and_single_off_day_smoothing(session_factory):
    with session_factory() as db:
        _, student, c_base, c_dep = _seed_graph(db)

        # 1. Single event: 100% (2/2) -> rolling score = 1.0 (OK)
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 2)})
        db.commit()
        st1 = mastery.current_state(db, student.id)[c_base.id]
        assert st1.score == 1.0
        assert st1.window_size == 1
        assert st1.status == mastery.OK
        assert st1.reason is None

        # 2. Second event (quiz): 100% (2/2) -> rolling score = (0.5*1.0 + 0.3*1.0)/0.8 = 1.0 (OK)
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 2)}, kind=mastery.QUIZ)
        db.commit()
        st2 = mastery.current_state(db, student.id)[c_base.id]
        assert st2.score == 1.0
        assert st2.window_size == 2
        assert st2.status == mastery.OK

        # 3. Third event (single off day: 1/2 = 0.50, which alone would be weak < 0.60):
        # Rolling score = 0.50*(0.50) + 0.30*(1.0) + 0.20*(1.0) = 0.25 + 0.30 + 0.20 = 0.75 >= 0.60 (OK!)
        # Because rolling score is OK (0.75), c_dep must NOT be flagged at_risk!
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 1)})
        db.commit()
        states_after_off_day = mastery.current_state(db, student.id)
        st3 = states_after_off_day[c_base.id]
        assert st3.score == 0.75
        assert st3.latest_score == 0.5
        assert st3.window_size == 3
        assert st3.status == mastery.OK
        assert c_dep.id not in states_after_off_day  # no false propagation on a single off day

        # 4. Fourth event: another poor score (0/2 = 0.0).
        # Window slides to the last 3 events: [1.0 (oldest), 0.5 (previous), 0.0 (latest)]
        # Rolling score = 0.50*(0.0) + 0.30*(0.5) + 0.20*(1.0) = 0.0 + 0.15 + 0.20 = 0.35 < 0.60 (WEAK!)
        # Now c_base is genuinely weak AND propagates at_risk to c_dep with explainable reasons on both.
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 0)}, kind=mastery.QUIZ)
        db.commit()
        states_after_decline = mastery.current_state(db, student.id)

        base_state = states_after_decline[c_base.id]
        assert base_state.score == 0.35
        assert base_state.latest_score == 0.0
        assert base_state.window_size == 3
        assert base_state.status == mastery.WEAK
        assert base_state.reason is not None
        assert "tested weak directly" in base_state.reason
        assert "35%" in base_state.reason
        assert base_state.flagged_by is None

        dep_state = states_after_decline[c_dep.id]
        assert dep_state.status == mastery.AT_RISK
        assert dep_state.score is None
        assert dep_state.flagged_by == c_base.id
        assert dep_state.reason == "flagged because it depends on Algebraic Identities, which tested weak"


def test_two_event_normalized_weights_and_recovery(session_factory):
    with session_factory() as db:
        _, student, c_base, c_dep = _seed_graph(db)

        # Event 1: 0/2 = 0.0 -> rolling = 0.0 (WEAK), c_dep becomes AT_RISK
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 0)})
        db.commit()
        st1 = mastery.current_state(db, student.id)
        assert st1[c_base.id].status == mastery.WEAK
        assert st1[c_base.id].score == 0.0
        assert st1[c_base.id].reason == "tested weak directly (micro-check: 0%)"
        assert st1[c_dep.id].status == mastery.AT_RISK

        # Event 2: 2/2 = 1.0 -> 2-event normalized rolling score = (0.50*1.0 + 0.30*0.0) / 0.80 = 0.625 >= 0.60 (OK)
        mastery.record_check(db, student.id, None, None, {c_base.id: (2, 2)})
        db.commit()
        st2 = mastery.current_state(db, student.id)
        assert st2[c_base.id].status == mastery.OK
        assert st2[c_base.id].score == 0.625
        assert st2[c_base.id].reason is None
        # Per Phase 3 step 6 rule, a weak concept that later recovers does NOT clear its dependents' at_risk flags;
        # only a direct check/quiz on the dependent itself clears it.
        assert st2[c_dep.id].status == mastery.AT_RISK