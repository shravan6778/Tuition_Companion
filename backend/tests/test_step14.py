"""Layer 5: decisions about variant suggestions are remembered (content_library/feedback.py, table match_feedback) and summarised
(app.db.match_feedback).

The teacher endpoints that used to record these decisions (variant-of, dismiss, report) no longer exist, so nothing in the
app writes this table today; the recorder and the report are tested directly so they keep working if a student-side flow
starts using them."""
import uuid

from sqlalchemy import select

from app.content_library import feedback
from app.db.match_feedback import summarize
from app.models import Book, MatchFeedback, Role
from tests.test_book_access import make_user
from tests.test_step13 import OFFICIAL, titles_book


def world(session_factory):
    """An official book and a student's private book that follows its chapter titles."""
    s, _ = make_user(session_factory, Role.student, "studenta")
    with session_factory() as db:
        ref = titles_book(db, OFFICIAL)
        mine = titles_book(db, OFFICIAL[:2], owner_id=s.id)
        db.commit()
        return str(mine.id), str(ref.id)


def rows(session_factory):
    with session_factory() as db:
        return list(db.scalars(select(MatchFeedback)))


EVIDENCE = {"signal": "structure", "coverage": 1.0, "avg_similarity": 0.9, "matched_chapters": 2}


def test_recording_keeps_what_the_suggestion_showed(session_factory):
    book_id, ref_id = world(session_factory)
    with session_factory() as db:
        feedback.record(db, uuid.UUID(book_id), uuid.UUID(ref_id), "confirmed", EVIDENCE)
        db.commit()
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and str(row.base_book_id) == ref_id and str(row.book_id) == book_id
    assert row.evidence["signal"] == "structure" and "book" not in row.evidence


def test_a_later_decision_replaces_the_earlier_one_but_keeps_the_evidence(session_factory):
    book_id, ref_id = world(session_factory)
    b, r = uuid.UUID(book_id), uuid.UUID(ref_id)
    with session_factory() as db:
        feedback.record(db, b, r, "confirmed", EVIDENCE)
        feedback.record(db, b, r, "retracted")  # cleared later: the evidence from the confirmation stays
        db.commit()
    [row] = rows(session_factory)  # one row per (book, base)
    assert row.decision == "retracted" and row.evidence == EVIDENCE


def test_only_dismissed_suggestions_are_hidden(session_factory):
    book_id, ref_id = world(session_factory)
    b, r = uuid.UUID(book_id), uuid.UUID(ref_id)
    with session_factory() as db:
        assert feedback.dismissed_ids(db, b) == set()
        feedback.record(db, b, r, "dismissed", EVIDENCE)
        assert feedback.dismissed_ids(db, b) == {r}
        feedback.record(db, b, r, "retracted")  # a retraction does not hide the suggestion
        assert feedback.dismissed_ids(db, b) == set()
        feedback.record(db, b, r, "dismissed")
        feedback.record(db, b, r, "confirmed")  # a dismissed book can still be confirmed by hand
        assert feedback.dismissed_ids(db, b) == set()


def test_a_book_cannot_give_feedback_about_itself(session_factory):
    import pytest
    from sqlalchemy.exc import IntegrityError

    book_id, _ = world(session_factory)
    with session_factory() as db:
        with pytest.raises(IntegrityError):
            feedback.record(db, uuid.UUID(book_id), uuid.UUID(book_id), "confirmed")


def test_feedback_rows_are_declared_to_vanish_with_either_book():
    """The test database does not enforce foreign keys, so check the declared cascade (Postgres enforces it)."""
    for column in ("book_id", "base_book_id"):
        [fk] = MatchFeedback.__table__.c[column].foreign_keys
        assert fk.ondelete == "CASCADE"


def test_report_counts_decisions_and_front_page_corrections(session_factory):
    book_id, ref_id = world(session_factory)
    with session_factory() as db:
        feedback.record(db, uuid.UUID(book_id), uuid.UUID(ref_id), "confirmed", EVIDENCE)
        book = db.get(Book, uuid.UUID(book_id))
        book.extracted_metadata = {"board": "CBSE", "class_name": "Class " + book.class_name, "publisher": "N C E R T", "subject": book.subject}
        db.commit()
        text = "\n".join(summarize(db))
        shown = "\n".join(summarize(db, show_changes=True))
    assert "1 teacher decisions" in text and "signal structure:" in text and "confirmed: 1" in text
    assert "confirmed without a suggestion (the system missed it): 0" in text
    assert "publisher: teacher changed 1 of 1" in text and "subject: teacher changed 0 of 1" in text
    assert "class_name: teacher changed 0 of 1" in text  # 'Class 9' read, '9' confirmed: the same class
    assert ref_id not in text and book_id not in text  # counts only, never ids
    assert "N C E R T" not in text and "'N C E R T' ->" in shown  # values only when asked for
