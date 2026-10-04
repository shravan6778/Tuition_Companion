"""Chapter processing lifecycle: background job, status, retry, upload validation (Rules.md §3)."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.models import Chapter, ChapterStatus, Page, Role
from tests.test_book_access import join_room_of, make_user, new_book, new_chapter
from tests.test_pipeline import CountingLLM, _text_pdf


def upload(client, headers, book_id, chapter_id, data, name="c.pdf"):
    return client.post(
        f"/teacher/books/{book_id}/chapters/{chapter_id}/pages/upload",
        files={"file": (name, data, "application/pdf")}, headers=headers,
    )


def chapter_status(client, headers, book_id, chapter_id) -> dict:
    chapters = client.get(f"/teacher/books/{book_id}/chapters", headers=headers).json()
    return next(c for c in chapters if c["id"] == chapter_id)


def page_count(session_factory, chapter_id) -> int:
    with session_factory() as db:
        return len(db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(str(chapter_id)))).all())


def setup_chapter(client, session_factory, tag="teachera"):
    _, th = make_user(session_factory, Role.teacher, tag)
    book = new_book(client, th)
    return th, book["id"], new_chapter(client, th, book["id"])


class BrokenLLM:
    model_name = "broken"

    def complete_json(self, system, user):
        raise RuntimeError("secret-internal-detail: db password is hunter2")


def use_llm(monkeypatch, llm):
    monkeypatch.setattr("app.pipeline.orchestrator.get_llm_provider", lambda: llm)


# ---- lifecycle ----------------------------------------------------------------

def test_new_chapter_starts_empty_then_becomes_ready(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    assert chapter_status(client, th, book_id, ch)["status"] == "empty"

    res = upload(client, th, book_id, ch, _text_pdf("page one", "page two"))
    assert res.status_code == 202 and res.json()["status"] == "processing"

    done = chapter_status(client, th, book_id, ch)
    assert done["status"] == "ready" and done["error_message"] is None
    assert page_count(session_factory, ch) == 2


def test_failure_marks_chapter_failed_with_safe_message_and_keeps_no_pages(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    use_llm(monkeypatch, BrokenLLM())

    assert upload(client, th, book_id, ch, _text_pdf("page one")).status_code == 202
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed"
    assert "try again" in st["error_message"].lower()
    assert "hunter2" not in st["error_message"] and "secret" not in st["error_message"]  # no internals leak
    assert page_count(session_factory, ch) == 0


def test_retry_after_failure_uses_stored_file_and_succeeds(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    use_llm(monkeypatch, CountingLLM(reply="not json"))
    upload(client, th, book_id, ch, _text_pdf("page one", "page two"))
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed" and "page 1" in st["error_message"]

    use_llm(monkeypatch, CountingLLM())  # the LLM recovers
    res = client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=th)
    assert res.status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"
    assert page_count(session_factory, ch) == 2


def test_retry_is_rejected_when_there_is_nothing_to_retry(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    url = f"/teacher/books/{book_id}/chapters/{ch}/retry"
    assert client.post(url, headers=th).status_code == 409  # empty: no file yet
    upload(client, th, book_id, ch, _text_pdf("page one"))
    assert client.post(url, headers=th).status_code == 409  # already ready


def test_reuploading_identical_file_is_a_noop_and_different_file_replaces_pages(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    llm = CountingLLM()
    use_llm(monkeypatch, llm)
    pdf = _text_pdf("alpha page one", "beta page two")

    assert upload(client, th, book_id, ch, pdf).status_code == 202
    calls = llm.calls
    again = upload(client, th, book_id, ch, pdf)
    assert again.status_code == 200 and again.json()["status"] == "ready"
    assert llm.calls == calls  # nothing reprocessed

    assert upload(client, th, book_id, ch, _text_pdf("only one new page")).status_code == 202
    assert page_count(session_factory, ch) == 1  # replaced, not appended


def test_failed_reupload_leaves_previous_pages_untouched(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("good page one", "good page two"))
    use_llm(monkeypatch, BrokenLLM())
    upload(client, th, book_id, ch, _text_pdf("a bad new upload"))
    assert chapter_status(client, th, book_id, ch)["status"] == "failed"
    assert page_count(session_factory, ch) == 2  # rolled back to the old pages, not half-replaced


# ---- concurrency / stuck jobs -----------------------------------------------------

def set_processing(session_factory, chapter_id, started_ago_min):
    with session_factory() as db:
        ch = db.get(Chapter, uuid.UUID(chapter_id))
        ch.status = ChapterStatus.PROCESSING
        ch.source_file = ch.source_file or "xx/missing.pdf"
        ch.processing_started_at = datetime.now(timezone.utc) - timedelta(minutes=started_ago_min)
        db.commit()


def test_cannot_upload_or_retry_while_actively_processing(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    set_processing(session_factory, ch, started_ago_min=1)
    assert upload(client, th, book_id, ch, _text_pdf("x")).status_code == 409
    assert client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=th).status_code == 409


def test_stuck_processing_chapter_can_be_replaced_after_timeout(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    set_processing(session_factory, ch, started_ago_min=settings.chapter_processing_timeout_min + 5)
    assert upload(client, th, book_id, ch, _text_pdf("fresh start")).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"


# ---- upload validation ------------------------------------------------------------

def test_upload_validation(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)
    assert upload(client, th, book_id, ch, b"").status_code == 400
    assert upload(client, th, book_id, ch, b"just some text, not a pdf", name="fake.pdf").status_code == 415
    assert upload(client, th, book_id, ch, b"%PDF-1.4 x", name="notes.txt").status_code == 202  # content decides, not name
    monkeypatch.setattr(settings, "max_upload_mb", 0)
    th2, b2, c2 = setup_chapter(client, session_factory, tag="teacherb")
    assert upload(client, th2, b2, c2, b"%PDF-1.4 x").status_code == 413
    assert chapter_status(client, th2, b2, c2)["status"] == "empty"  # rejected uploads change nothing


def test_other_teacher_cannot_retry_or_replace_pages(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    assert client.post(f"/teacher/books/{book_id}/chapters/{ch}/retry", headers=other).status_code == 404
    assert upload(client, other, book_id, ch, _text_pdf("x")).status_code == 404


# ---- students only see finished chapters --------------------------------------------

def test_students_only_see_ready_chapters_and_their_pages(client, session_factory, monkeypatch):
    th, book_id, ready_ch = setup_chapter(client, session_factory)
    failed_ch = new_chapter(client, th, book_id)  # second chapter, same sequence is fine for this test
    _, sh = make_user(session_factory, Role.student, "student1")
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)

    upload(client, th, book_id, ready_ch, _text_pdf("good"))
    use_llm(monkeypatch, BrokenLLM())
    upload(client, th, book_id, failed_ch, _text_pdf("bad"))

    book = client.get(f"/student/books/{book_id}", headers=sh).json()
    assert [c["id"] for c in book["chapters"]] == [ready_ch]
    assert client.get(f"/student/books/{book_id}/chapters/{ready_ch}/pages", headers=sh).status_code == 200
    assert client.get(f"/student/books/{book_id}/chapters/{failed_ch}/pages", headers=sh).status_code == 404
    mine = client.get("/student/books", headers=sh).json()
    assert [c["id"] for c in mine[0]["chapters"]] == [ready_ch]
