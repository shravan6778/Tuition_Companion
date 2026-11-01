"""Phase 3 step 7: standalone "Ask a Doubt": browse Subject -> Book -> Chapter, and a doubt narrowed to one chapter (or none)."""
import uuid

import pytest
from sqlalchemy import select

from app.doubts import service
from app.models import Book, Doubt, Role
from tests.test_book_access import make_user
from tests.test_phase3_settle import TISSUE, add_chapter
from tests.test_phase3_step2 import NOISE_Q, TISSUE_Q, assign, world  # noqa: F401  (world is a fixture)
from tests.test_phase3_step4 import PNG, WHOLE_PAGE, reads, snap  # noqa: F401
from app.models import ChapterStatus, PageKind


def ask_chapter(client, w, text, chapter, headers=None, **extra):
    return client.post("/student/doubts", json={"text": text, "chapter_id": w["ids"][chapter] if chapter in w["ids"] else chapter, **extra},
                       headers=headers or w["sh"])


def rows(session_factory):
    with session_factory() as db:
        return db.scalars(select(Doubt)).all()


# ---- browse ------------------------------------------------------------------------------------------------

def test_browse_lists_subject_book_and_only_the_ready_chapters(client, world):
    body = client.get("/student/doubts/browse", headers=world["sh"]).json()
    assert [s["subject"] for s in body] == ["Science"]
    (book,) = body[0]["books"]
    assert book["id"] == world["ids"]["book"] and "Class 9" in book["label"]
    assert [(c["number"], c["title"]) for c in book["chapters"]] == [(1, "Cells"), (2, "Force")]  # the empty chapter 3 is not offered
    assert {c["id"] for c in book["chapters"]} == {world["ids"]["ch1"], world["ids"]["ch2"]}


def test_browse_is_empty_for_a_student_with_no_books(client, session_factory, world):
    _, other = make_user(session_factory, Role.student, "studentb")
    assert client.get("/student/doubts/browse", headers=other).json() == []


def test_browse_groups_books_by_subject_ignoring_case_and_skips_books_without_a_ready_chapter(client, session_factory, world):
    with session_factory() as db:
        owner = db.get(Book, uuid.UUID(world["ids"]["book"])).owner_student_id
        maths = Book(board="CBSE", class_name="Class 9", subject="science", publisher="Other", is_reference=False, owner_student_id=owner)
        empty = Book(board="CBSE", class_name="Class 9", subject="Maths", publisher="Pub", is_reference=False, owner_student_id=owner)
        db.add_all([maths, empty])
        db.flush()
        add_chapter(db, maths, "Motion", 1, [(1, "Motion is change of place " * 6, PageKind.CONTENT)], [(1, "Motion", "change of place")])
        add_chapter(db, empty, "Algebra", 1, [], status=ChapterStatus.PROCESSING)
        db.commit()
    body = client.get("/student/doubts/browse", headers=world["sh"]).json()
    assert [s["subject"] for s in body] == ["Science"] and len(body[0]["books"]) == 2  # 'science' joined 'Science'; Maths has nothing ready


def test_browse_never_shows_another_students_book(client, session_factory, world):
    other_student, _ = make_user(session_factory, Role.student, "studentb")
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="History", publisher="P", is_reference=False, owner_student_id=other_student.id)
        db.add(book)
        db.flush()
        add_chapter(db, book, "Secret", 1, [(1, "Secret text " * 10, PageKind.CONTENT)], [(1, "Secret", "x")])
        db.commit()
    body = client.get("/student/doubts/browse", headers=world["sh"]).json()
    assert "History" not in [s["subject"] for s in body]


# ---- a doubt narrowed to one chapter -----------------------------------------------------------------------

def test_a_doubt_in_the_chosen_chapter_is_grounded_and_answered_from_it(client, session_factory, world):
    body = ask_chapter(client, world, TISSUE_Q, "ch1").json()
    assert body["status"] == "grounded" and body["chapter_id"] == world["ids"]["ch1"] and body["assignment_id"] is None
    assert {p["chapter_title"] for p in body["pages"]} == {"Cells"}
    (row,) = rows(session_factory)
    assert row.assignment_id is None and row.status == "grounded"


def test_the_same_doubt_in_another_chapter_points_to_where_the_books_do_cover_it(client, world):
    body = ask_chapter(client, world, TISSUE_Q, "ch2").json()
    assert body["status"] == "outside_assignment" and body["pages"] == [] and body["answer_status"] == "none"
    assert "Tissue" in [h["name"] for h in body["elsewhere"]]
    assert body["message"] == service.CHAPTER_OUTSIDE and "assignment" not in body["message"]


def test_without_a_chapter_every_book_of_the_student_is_searched(client, world):
    body = client.post("/student/doubts", json={"text": TISSUE_Q}, headers=world["sh"]).json()
    assert body["status"] == "grounded" and body["chapter_id"] is None


def test_a_doubt_the_books_do_not_cover_asks_the_student_to_upload_the_chapter(client, world):
    body = ask_chapter(client, world, NOISE_Q, "ch1").json()
    assert body["status"] == "not_in_book" and body["request_chapter"] is None and "Upload this chapter" in body["message"]


def test_a_chapter_that_is_not_ready_or_not_the_students_is_404_and_saves_nothing(client, session_factory, world):
    assert ask_chapter(client, world, TISSUE_Q, "ch3").status_code == 404  # empty chapter
    assert ask_chapter(client, world, TISSUE_Q, "00000000-0000-0000-0000-000000000000").status_code == 404
    _, other = make_user(session_factory, Role.student, "studentb")  # not the owner of the book
    assert ask_chapter(client, world, TISSUE_Q, "ch1", headers=other).status_code == 404
    assert rows(session_factory) == []


def test_an_assignment_and_a_chapter_together_are_refused(client, world):
    res = ask_chapter(client, world, TISSUE_Q, "ch1", assignment_id=assign(client, world)["id"])
    assert res.status_code == 422


def test_a_removed_book_stops_its_chapters_being_searched(client, world):
    assert client.delete(f"/student/books/{world['ids']['book']}", headers=world["sh"]).status_code == 204
    assert ask_chapter(client, world, TISSUE_Q, "ch1").status_code == 404
    assert client.get("/student/doubts/browse", headers=world["sh"]).json() == []


# ---- a photo narrowed to a chapter -------------------------------------------------------------------------

def photo_in_chapter(client, w, chapter, **kw):
    return client.post("/student/doubts/photo", files={"file": ("d.png", PNG, "image/png")},
                       data={"chapter_id": w["ids"][chapter]}, headers=kw.get("headers") or w["sh"])


def test_a_photographed_doubt_can_be_narrowed_to_a_chapter(client, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    inside = photo_in_chapter(client, world, "ch1").json()
    assert inside["kind"] == "doubt" and inside["doubt"]["status"] == "grounded" and inside["doubt"]["chapter_id"] == world["ids"]["ch1"]
    outside = photo_in_chapter(client, world, "ch2").json()
    assert outside["doubt"]["status"] == "outside_assignment"


def test_a_whole_page_photo_offers_only_concepts_of_the_chosen_chapter(client, world, monkeypatch):
    reads(monkeypatch, WHOLE_PAGE)
    body = photo_in_chapter(client, world, "ch1").json()
    assert body["kind"] == "page" and body["page"]["chapter_id"] == world["ids"]["ch1"]
    outside = photo_in_chapter(client, world, "ch2").json()
    assert outside["kind"] == "page" and outside["page"] is None and outside["status"] == "outside_assignment"


def test_a_photo_for_an_unready_chapter_is_404_before_any_ocr_call(client, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    from tests.test_phase3_step4 import StubOCR
    assert photo_in_chapter(client, world, "ch3").status_code == 404
    assert StubOCR.calls == 0
