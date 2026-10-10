"""Delete books/chapters (teacher + admin), front-page reading that survives odd answers, drop_book, relaxed unresolved rule."""
import json
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.content_library import deletion
from app.core.config import settings
from app.db import drop_book, phase2_check as pc, try_front_pages
from app.models import Book, Chapter, ChapterStatus, Page, Role
from app.pipeline.front_matter import BookMetadata, extract_book_metadata, is_empty, parse_reply
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_step6 import front_pdf, post_front, ref_book
from tests.test_step15 import GOOD, TEXT, official_book


class FakeStore:
    def __init__(self, fail=False):
        self.deleted, self.fail = [], fail

    def delete_chapter(self, cid):
        if self.fail:
            raise RuntimeError("graph store down")
        self.deleted.append(cid)


@pytest.fixture
def store(monkeypatch):
    s = FakeStore()
    monkeypatch.setattr(deletion, "get_graph_store", lambda: s)
    return s


def add_chapter_row(session_factory, book_id, title="Ch", seq=1, status=ChapterStatus.READY, started=None):
    with session_factory() as db:
        ch = Chapter(book_id=uuid.UUID(book_id), title=title, sequence_num=seq, status=status, processing_started_at=started)
        db.add(ch)
        db.flush()
        db.add(Page(chapter_id=ch.id, page_number=1, content_text=TEXT))
        db.commit()
        return str(ch.id)


def count(session_factory, model):
    with session_factory() as db:
        return db.scalar(select(func.count()).select_from(model))


# ---------------- teachers delete their own books and chapters ----------------

def test_teacher_deletes_own_book_with_its_chapters_and_graph_copy(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch_id = add_chapter_row(session_factory, book["id"])
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 204
    assert count(session_factory, Book) == 0 and count(session_factory, Chapter) == 0 and count(session_factory, Page) == 0
    assert store.deleted == [uuid.UUID(ch_id)] or store.deleted == [ch_id]
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 404


def test_nobody_else_can_delete_my_book_and_official_books_are_not_deletable_here(client, session_factory, store):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    book = new_book(client, ah)
    assert client.delete(f"/teacher/books/{book['id']}", headers=bh).status_code == 404
    ref = ref_book(session_factory)
    assert client.delete(f"/teacher/books/{ref}", headers=ah).status_code == 403
    assert count(session_factory, Book) == 2


def test_deleting_a_book_unmarks_books_that_were_variants_of_it(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    base, variant = new_book(client, th), new_book(client, th, subject="Other")
    assert client.post(f"/teacher/books/{variant['id']}/variant-of", json={"base_book_id": base["id"]}, headers=th).status_code == 200
    assert client.delete(f"/teacher/books/{base['id']}", headers=th).status_code == 204
    with session_factory() as db:
        assert db.get(Book, uuid.UUID(variant["id"])).variant_of_id is None


def test_a_chapter_being_processed_cannot_be_deleted_but_a_stuck_one_can(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    busy = add_chapter_row(session_factory, book["id"], "Busy", 1, ChapterStatus.PROCESSING, datetime.now(timezone.utc))
    assert client.delete(f"/teacher/books/{book['id']}/chapters/{busy}", headers=th).status_code == 409
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 409
    stuck = add_chapter_row(session_factory, book["id"], "Stuck", 2, ChapterStatus.PROCESSING, datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert client.delete(f"/teacher/books/{book['id']}/chapters/{stuck}", headers=th).status_code == 204


def test_delete_chapter_checks_it_belongs_to_that_book_and_book_survives(client, session_factory, store):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    a, b = new_book(client, th), new_book(client, th, subject="Other")
    ch = add_chapter_row(session_factory, a["id"])
    assert client.delete(f"/teacher/books/{b['id']}/chapters/{ch}", headers=th).status_code == 404
    assert client.delete(f"/teacher/books/{a['id']}/chapters/{ch}", headers=th).status_code == 204
    assert count(session_factory, Book) == 2 and count(session_factory, Chapter) == 0


def test_graph_store_trouble_never_blocks_a_delete(client, session_factory, monkeypatch):
    monkeypatch.setattr(deletion, "get_graph_store", lambda: FakeStore(fail=True))
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    add_chapter_row(session_factory, book["id"])
    assert client.delete(f"/teacher/books/{book['id']}", headers=th).status_code == 204
    assert count(session_factory, Chapter) == 0


# ---------------- administrators delete official books ----------------

def test_only_listed_administrators_can_delete_official_books_and_chapters(client, session_factory, store, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "adminuser")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    ref = ref_book(session_factory)
    ch = add_chapter_row(session_factory, ref)
    mine = new_book(client, th)
    assert client.delete(f"/admin/books/{ref}", headers=ah).status_code == 403  # nobody is an administrator by default
    monkeypatch.setattr(settings, "admin_usernames", " AdminUser , someone ")
    assert client.delete(f"/admin/books/{ref}", headers=th).status_code == 403
    assert client.delete(f"/admin/books/{mine['id']}", headers=ah).status_code == 404  # not official: not an admin matter
    assert client.delete(f"/admin/books/{ref}/chapters/{uuid.uuid4()}", headers=ah).status_code == 404
    assert client.delete(f"/admin/books/{ref}/chapters/{ch}", headers=ah).status_code == 204
    assert client.delete(f"/admin/books/{ref}", headers=ah).status_code == 204
    assert count(session_factory, Book) == 1


def test_me_tells_the_ui_whether_the_user_is_an_administrator(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "adminuser")
    assert client.get("/auth/me", headers=ah).json()["is_admin"] is False
    monkeypatch.setattr(settings, "admin_usernames", "adminuser")
    assert client.get("/auth/me", headers=ah).json()["is_admin"] is True


def test_drop_book_tool(session_factory, store):
    with session_factory() as db:
        official = official_book(db)
        teacher_book_id = None
        db.commit()
        book_id = official.id
    out = drop_book.run(session_factory, book_id, confirm=False)
    assert "would delete" in out[0] and "3 chapters" in out[0] and count(session_factory, Book) == 1
    assert drop_book.run(session_factory, uuid.uuid4(), True) == ["Book not found."]
    assert drop_book.run(session_factory, book_id, True)[0].startswith("deleted") and count(session_factory, Book) == 0
    assert len(store.deleted) == 3


# ---------------- front pages ----------------

def test_reply_parsing_accepts_odd_but_clear_answers():
    assert parse_reply('{"Board": "CBSE", "Class": "Class 9", "Subject": "Science", "Publisher": "NCERT"}').publisher == "NCERT"
    nested = parse_reply('{"metadata": {"board": "CBSE", "grade": "Class 9", "publisher": "NCERT"}}')
    assert nested.class_name == "Class 9" and nested.board == "CBSE"
    assert parse_reply('```json\n{"board": "ICSE"}\n```').board == "ICSE"
    assert is_empty(parse_reply('{"unrelated": 1}'))


class Scripted:
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), 0

    def complete_json(self, system, user):
        self.calls += 1
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


def test_an_all_empty_answer_gets_a_second_look_and_never_crashes():
    good = '{"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "NCERT"}'
    llm = Scripted('{"board": null, "class_name": null}', good)
    assert extract_book_metadata(llm, "Curiosity Grade 9 Science NCERT").publisher == "NCERT" and llm.calls == 2
    nothing = Scripted('{"board": null, "class_name": null, "subject": null, "publisher": null}')
    assert is_empty(extract_book_metadata(nothing, "some text")) and nothing.calls == 3  # asked three times, then the form stays empty
    junk_then_good = Scripted("not json at all", good)
    assert extract_book_metadata(junk_then_good, "text").board == "CBSE"


def test_the_draft_says_so_when_nothing_could_be_read(client, session_factory, monkeypatch):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    with monkeypatch.context() as m:
        m.setattr("app.content_library.upload.extract_book_metadata", lambda provider, text: BookMetadata())
        body = post_front(client, th).json()
    assert body["warning"] and "characters" in body["warning"] and body["metadata"]["publisher"] is None
    assert post_front(client, th).json()["warning"] is None  # the normal fake-provider read fills the form


def test_try_front_pages_shows_what_the_reader_gets(tmp_path):
    pdf = tmp_path / "front.pdf"
    pdf.write_bytes(front_pdf())

    class Ocr:
        def extract_layout(self, data, ext):
            return {"pages": [{"text": "CURIOSITY Textbook of Science Grade 9 NCERT"}]}

    class Llm:
        def complete_json(self, system, user):
            return json.dumps({"board": None, "class_name": "Class 9", "subject": "Science", "publisher": "NCERT"})
    text = "\n".join(try_front_pages.run(str(pdf), Ocr(), Llm()))
    assert "43 characters" in text and "CURIOSITY" in text and "'publisher': 'NCERT'" in text and "would be filled" in text
    class Blank:
        def extract_layout(self, data, ext):
            return {"pages": [{"text": "   "}]}
    assert "No readable text" in "\n".join(try_front_pages.run(str(pdf), Blank(), Llm()))
    assert "Unsupported" in try_front_pages.run(str(tmp_path / "x.txt"))[0]


# ---------------- phase2_check: the two rules that were too blunt ----------------

def test_a_stray_unresolved_prerequisite_is_shown_for_review_not_failed(session_factory):
    with session_factory() as db:
        official_book(db, report={**GOOD, "concepts": 98, "unresolved_prerequisites": [{"concept": "A", "prerequisite": "Z"}]})
        res = pc.check_official_books(db)
        assert not [r for r in res if r[0] == "FAIL"]
        assert any(r[0] == "REVIEW" and "'A' needs 'Z'" in r[2] for r in res)
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        official_book(db, report={**GOOD, "concepts": 20, "unresolved_prerequisites": [{"concept": "A", "prerequisite": "Z"}] * 6})
        assert any(r[0] == "FAIL" and "unresolved" in r[2] for r in pc.check_official_books(db))


def test_an_empty_official_book_is_named_and_the_fix_is_given(session_factory):
    with session_factory() as db:
        official_book(db)
        empty = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", edition="2026", is_reference=True)
        db.add(empty)
        db.flush()
        fails = [r[2] for r in pc.check_official_books(db) if r[0] == "FAIL"]
        assert len(fails) == 1 and "no chapters at all" in fails[0] and f"drop_book --book {empty.id}" in fails[0] and "edition 2026" in fails[0]
