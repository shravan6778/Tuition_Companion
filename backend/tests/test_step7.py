"""Rate limits, needs_review flags, draft cleanup, and the reference-corpus ingest script."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core import ratelimit
from app.core.config import settings
from app.core.storage import read_file, save_by_hash, sha256_hex
from app.db.cleanup_drafts import cleanup
from app.db.ingest_reference import ingest, parse_ranges
from app.models import Book, Chapter, Role, UploadDraft, User
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_book_access import make_user, new_book, new_chapter
from tests.test_chapter_jobs import BrokenLLM, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf
from tests.test_step6 import TEXTS, make_room, pdf_with_outline, plan, post_front


# ---- rate limits --------------------------------------------------------------------------------

def test_limiter_blocks_after_limit_resets_after_window_and_separates_users(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(ratelimit.time, "monotonic", lambda: clock[0])
    lim = ratelimit.RateLimiter()
    for _ in range(3):
        lim.check("b", "u1", 3, 60)
    with pytest.raises(Exception) as err:
        lim.check("b", "u1", 3, 60)
    assert err.value.status_code == 429 and int(err.value.headers["Retry-After"]) >= 1
    lim.check("b", "u2", 3, 60)  # other user unaffected
    lim.check("other-bucket", "u1", 3, 60)  # other action unaffected
    clock[0] += 61
    lim.check("b", "u1", 3, 60)  # window passed


def test_join_room_is_rate_limited_per_student(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_join_per_min", 3)
    _, s1 = make_user(session_factory, Role.student, "student1")
    _, s2 = make_user(session_factory, Role.student, "student2")
    for _ in range(3):
        assert client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s1).status_code == 404
    blocked = client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s1)
    assert blocked.status_code == 429 and "Retry-After" in blocked.headers
    assert client.post("/student/rooms/join", json={"join_code": "WRONG1"}, headers=s2).status_code == 404


def test_parent_link_is_rate_limited(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_parent_link_per_min", 2)
    _, ph = make_user(session_factory, Role.parent, "parent1")
    for _ in range(2):
        assert client.post("/parent/link", json={"link_code": "NOPE0000"}, headers=ph).status_code == 404
    assert client.post("/parent/link", json={"link_code": "NOPE0000"}, headers=ph).status_code == 429


def test_costly_upload_steps_are_rate_limited(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "rate_front_pages_per_hour", 2)
    monkeypatch.setattr(settings, "rate_whole_book_plan_per_hour", 1)
    _, th = make_user(session_factory, Role.teacher, "teachera")
    assert post_front(client, th).status_code == 201 and post_front(client, th).status_code == 201
    assert post_front(client, th).status_code == 429
    book = new_book(client, th)
    assert plan(client, th, book["id"], _text_pdf(*TEXTS)).status_code == 201
    assert plan(client, th, book["id"], _text_pdf(*TEXTS)).status_code == 429


# ---- needs_review ------------------------------------------------------------------------------------

LONG = " ".join(f"word{i}" for i in range(60))


def test_long_page_without_concepts_is_flagged_for_review_and_reported(client, session_factory, monkeypatch):
    class OnlyEmptyForBlankPage(CountingLLM):
        def complete_json(self, system, user):
            self.calls += 1
            if "word0" in user:  # the long scan: the model found nothing
                return '{"concepts": []}'
            return '{"concepts":[{"name":"Matter","description":"d","learning_objectives":[],"prerequisites":[]}]}'

    use_llm(monkeypatch, OnlyEmptyForBlankPage())
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    ch = new_chapter(client, th, book["id"])
    assert upload(client, th, book["id"], ch, _text_pdf(LONG, "a short page about matter and nothing else here")).status_code == 202

    pages = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=th).json()
    long_page, short_page = pages
    assert long_page["needs_review"] is True and "no concepts" in long_page["review_note"].lower()
    assert short_page["needs_review"] is False and short_page["review_note"] is None and short_page["concepts"]
    report = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/graph", headers=th).json()["report"]
    assert [r["page"] for r in report["review_pages"]] == [1] and report["concepts"] == 1  # graph facts survive


def test_short_page_with_no_concepts_is_not_flagged(session_factory):
    class Empty(CountingLLM):
        def complete_json(self, system, user):
            return '{"concepts": []}'

    with session_factory() as db:
        book = Book(board="B", class_name="9", subject="S", publisher="P", is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="C", sequence_num=1)
        db.add(ch)
        db.flush()
        pages = PipelineOrchestrator(db, llm_provider=Empty()).process_chapter_file(ch, _text_pdf("Contents page"), "pdf", None)
        assert pages[0].needs_review is False and ch.graph_report["review_pages"] == []


# ---- draft cleanup -----------------------------------------------------------------------------------

def stored(data: bytes) -> str:
    return save_by_hash(data, sha256_hex(data), "pdf")


def test_cleanup_removes_only_old_drafts_and_unreferenced_files(session_factory):
    old_time = datetime.now(timezone.utc) - timedelta(days=10)
    with session_factory() as db:
        teacher = User(supertokens_user_id="st-t", name="T", username="tt", phone="1", role=Role.teacher)
        db.add(teacher)
        db.flush()
        book = Book(board="B", class_name="9", subject="S", publisher="P", owner_teacher_id=teacher.id)
        db.add(book)
        db.flush()
        chapter = Chapter(book_id=book.id, title="C", sequence_num=1)
        db.add(chapter)

        orphan_file, shared_file, fresh_file = stored(b"%PDF-1.4 orphan"), stored(b"%PDF-1.4 shared"), stored(b"%PDF-1.4 fresh")
        chapter.source_file = shared_file  # a chapter still uses this file
        mk = lambda path, when: UploadDraft(teacher_id=teacher.id, kind="front_pages", source_file=path,
                                            source_sha256="0" * 64, page_count=1, created_at=when)
        db.add_all([mk(orphan_file, old_time), mk(shared_file, old_time), mk(fresh_file, datetime.now(timezone.utc))])
        db.commit()

        assert cleanup(db, older_than_days=7) == (2, 1)
        assert [d.source_file for d in db.scalars(select(UploadDraft))] == [fresh_file]
        with pytest.raises(FileNotFoundError):
            read_file(orphan_file)
        assert read_file(shared_file) and read_file(fresh_file)  # still there
        assert cleanup(db, older_than_days=7) == (0, 0)


# ---- reference corpus ingest ----------------------------------------------------------------------------

META = dict(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", edition="2025")


def test_parse_ranges():
    r = parse_ranges("Matter in Our Surroundings: A:1-12, Atoms:13-30,Single:31")
    assert [(x.title, x.start_page, x.end_page) for x in r] == [
        ("Matter in Our Surroundings: A", 1, 12), ("Atoms", 13, 30), ("Single", 31, 31)]


def test_ingest_builds_a_public_read_only_reference_book_from_bookmarks(client, session_factory):
    pdf = pdf_with_outline(TEXTS, [("Matter", 0), ("Atoms", 3)])
    book_id, results = ingest(session_factory, pdf, **META)
    assert results == ["ok     Matter", "ok     Atoms"]

    with session_factory() as db:
        book = db.get(Book, uuid.UUID(book_id))
        assert book.is_reference and book.owner_teacher_id is None and book.edition == "2025"
        chapters = db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)).all()
        assert [(c.title, c.status) for c in chapters] == [("Matter", "ready"), ("Atoms", "ready")]
        assert [len(c.pages) for c in chapters] == [3, 3]
        assert all(c.graph_report and c.match_report for c in chapters)

    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    assert book_id in [b["id"] for b in client.get("/teacher/books?scope=reference", headers=th).json()]
    assert client.post(f"/teacher/books/{book_id}/chapters", json={"title": "x", "sequence_num": 9}, headers=th).status_code == 403
    assert client.post(f"/student/books/{book_id}/link", headers=sh).status_code == 200
    first_chapter = client.get(f"/student/books/{book_id}", headers=sh).json()["chapters"][0]["id"]
    assert client.get(f"/student/books/{book_id}/chapters/{first_chapter}/graph", headers=sh).status_code == 200


def test_ingest_with_explicit_ranges_refuses_duplicates_and_reports_failures(session_factory, monkeypatch):
    pdf = _text_pdf(*TEXTS)
    book_id, results = ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META)
    assert results == ["ok     All"]
    with pytest.raises(SystemExit, match="already exists"):
        ingest(session_factory, pdf, ranges=parse_ranges("All:1-6"), **META)

    use_llm(monkeypatch, BrokenLLM())
    _, results = ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("Bad:1-2"), **{**META, "edition": "other"})
    assert results[0].startswith("FAILED Bad: ") and "secret" not in results[0]


def test_ingest_rejects_a_pdf_without_chapters_or_with_bad_ranges(session_factory):
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        ingest(session_factory, _text_pdf(*TEXTS), **META)  # no bookmarks and no --chapters
    with pytest.raises(HTTPException):
        ingest(session_factory, _text_pdf(*TEXTS), ranges=parse_ranges("X:1-99"), **META)
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []  # nothing created on rejection
