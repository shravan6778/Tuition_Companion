"""Layer 5: teacher decisions about variant suggestions feed back (content_library/feedback.py, match_feedback)."""
import uuid

from sqlalchemy import select

from app.db.match_feedback import summarize
from app.models import Book, Chapter, MatchFeedback, Role
from tests.test_book_access import make_user, new_book
from tests.test_step13 import OFFICIAL, titles_book


def setup(client, session_factory, tag="teachera"):
    """An official book plus a teacher book whose chapter titles follow it (so the structure signal suggests it)."""
    t, th = make_user(session_factory, Role.teacher, tag)
    with session_factory() as db:
        ref = titles_book(db, OFFICIAL)
        ref_id = str(ref.id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:
        for i, title in enumerate(["Exploration: Entering the World of Secondary Science", "The Building Block of Life"], 1):
            db.add(Chapter(book_id=uuid.UUID(book["id"]), title=title, sequence_num=i))
        db.commit()
    return th, book["id"], ref_id


def rows(session_factory):
    with session_factory() as db:
        return list(db.scalars(select(MatchFeedback)))


def sugg(client, th, book_id):
    res = client.get(f"/teacher/books/{book_id}/variant-suggestions", headers=th)
    assert res.status_code == 200, res.text
    return res.json()


def test_confirming_records_what_the_suggestion_showed(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    assert client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th).status_code == 200
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and str(row.base_book_id) == ref_id and str(row.book_id) == book_id
    assert row.evidence["signal"] == "structure" and row.evidence["coverage"] == 1.0 and "book" not in row.evidence


def test_confirming_a_book_nobody_suggested_is_recorded_as_a_miss(client, session_factory):
    th, book_id, _ = setup(client, session_factory)
    with session_factory() as db:
        other = titles_book(db, ["Gravitation", "Work and Energy"])
        other_id = str(other.id)
        db.commit()
    assert client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": other_id}, headers=th).status_code == 200
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and row.evidence is None


def test_dismissing_hides_the_suggestion_and_undo_brings_it_back(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id]
    assert client.post(f"/teacher/books/{book_id}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th).status_code == 204
    assert sugg(client, th, book_id) == []
    [row] = rows(session_factory)
    assert row.decision == "dismissed" and row.evidence["signal"] == "structure"
    assert client.delete(f"/teacher/books/{book_id}/variant-suggestions/dismiss/{ref_id}", headers=th).status_code == 204
    assert client.delete(f"/teacher/books/{book_id}/variant-suggestions/dismiss/{ref_id}", headers=th).status_code == 204  # idempotent
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id] and rows(session_factory) == []


def test_a_dismissed_book_can_still_be_confirmed_by_hand(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th)
    res = client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert res.status_code == 200 and res.json()["variant_of_id"] == ref_id
    [row] = rows(session_factory)
    assert row.decision == "confirmed" and row.evidence["signal"] == "structure"  # evidence from the dismissal is kept


def test_clearing_retracts_but_does_not_hide_the_suggestion(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.delete(f"/teacher/books/{book_id}/variant-of", headers=th).status_code == 204
    [row] = rows(session_factory)
    assert row.decision == "retracted" and row.evidence["signal"] == "structure"
    assert [s["book"]["id"] for s in sugg(client, th, book_id)] == [ref_id]


def test_switching_to_another_base_retracts_the_old_one(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    with session_factory() as db:
        other_id = str(titles_book(db, ["Gravitation", "Work and Energy"]).id)
        db.commit()
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": other_id}, headers=th)
    decisions = {str(r.base_book_id): r.decision for r in rows(session_factory)}
    assert decisions == {ref_id: "retracted", other_id: "confirmed"}


def test_dismiss_guards(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    url = f"/teacher/books/{book_id}/variant-suggestions/dismiss"
    assert client.post(url, json={"base_book_id": book_id}, headers=th).status_code == 400  # itself
    assert client.post(url, json={"base_book_id": str(uuid.uuid4())}, headers=th).status_code == 404
    assert client.post(url, json={"base_book_id": ref_id}, headers=bh).status_code == 404  # not B's book
    assert client.delete(f"{url}/{ref_id}", headers=bh).status_code == 404
    other = new_book(client, bh)  # B's private book is invisible to A
    assert client.post(url, json={"base_book_id": other["id"]}, headers=th).status_code == 404
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.post(url, json={"base_book_id": ref_id}, headers=th).status_code == 409  # confirmed: clear it first
    assert rows(session_factory)[0].decision == "confirmed"


def test_report_counts_decisions_and_front_page_corrections(client, session_factory):
    th, book_id, ref_id = setup(client, session_factory)
    client.post(f"/teacher/books/{book_id}/variant-of", json={"base_book_id": ref_id}, headers=th)
    with session_factory() as db:
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


def test_a_page_based_suggestion_can_be_dismissed_too(client, session_factory):
    t, th = make_user(session_factory, Role.teacher, "teachera")
    with session_factory() as db:
        ref_id = str(titles_book(db, OFFICIAL).id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:  # a finished chapter whose page fingerprints matched the official book (titles differ: no structure signal)
        db.add(Chapter(book_id=uuid.UUID(book["id"]), title="Our own title", sequence_num=1, status="ready", match_report={
            "pages_checked": 2, "suggestions": [{"book_id": ref_id, "chapter_id": None, "chapter_title": "Tissues", "kind": "variant",
                                                 "matched_pages": 2, "pages_checked": 2, "avg_similarity": 0.8}]}))
        db.commit()
    [s] = sugg(client, th, book["id"])
    assert s["book"]["id"] == ref_id and s["signal"] == "pages"
    client.post(f"/teacher/books/{book['id']}/variant-suggestions/dismiss", json={"base_book_id": ref_id}, headers=th)
    assert sugg(client, th, book["id"]) == []
    [row] = rows(session_factory)
    assert row.evidence["signal"] == "pages" and row.evidence["coverage"] == 1.0
