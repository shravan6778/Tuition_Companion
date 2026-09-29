from app.models import Role
from app.teacher import processing
from tests.test_chapters import PDF, make_subject, upload
from tests.test_library import add_user


def test_upload_triggers_processing_to_ready(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    upload(client, h, sid)

    chapter = client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]
    assert chapter["status"] == "ready"
    assert chapter["error_message"] is None


def test_ocr_runs_once_per_file_hash(client, session_factory, monkeypatch):
    calls = []
    real_provider = processing.get_ocr_provider()

    class CountingProvider:
        def extract(self, data, ext):
            calls.append(1)
            return real_provider.extract(data, ext)

    monkeypatch.setattr(processing, "get_ocr_provider", lambda: CountingProvider())

    h = add_user(session_factory, Role.teacher)
    a, b = make_subject(client, h, "Maths"), make_subject(client, h, "Physics")
    upload(client, h, a)  # same PDF bytes as b
    upload(client, h, b)

    assert len(calls) == 1  # second chapter reused the cached extraction, per Rules.md


def test_ocr_failure_marks_chapter_failed_with_message(client, session_factory, monkeypatch):
    class BoomProvider:
        def extract(self, data, ext):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr(processing, "get_ocr_provider", lambda: BoomProvider())

    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    upload(client, h, sid)

    chapter = client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]
    assert chapter["status"] == "failed"
    assert chapter["error_message"]


def test_retry_reprocesses_a_failed_chapter(client, session_factory, monkeypatch):
    from app.ocr import get_ocr_provider as real_get_ocr_provider

    class BoomProvider:
        def extract(self, data, ext):
            raise RuntimeError("provider unavailable")

    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)

    monkeypatch.setattr(processing, "get_ocr_provider", lambda: BoomProvider())
    cid = upload(client, h, sid).json()["id"]
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]["status"] == "failed"

    # Re-patch (rather than monkeypatch.undo(), which would also revert the
    # autouse tmp_storage fixture sharing this same monkeypatch instance).
    monkeypatch.setattr(processing, "get_ocr_provider", real_get_ocr_provider)
    res = client.post(f"/teacher/subjects/{sid}/chapters/{cid}/retry", headers=h)
    assert res.status_code == 202
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]["status"] == "ready"


def test_retry_only_allowed_on_failed_chapters(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    cid = upload(client, h, sid).json()["id"]  # succeeds -> ready
    assert client.post(f"/teacher/subjects/{sid}/chapters/{cid}/retry", headers=h).status_code == 409


def test_retry_is_owner_only(client, session_factory):
    a = add_user(session_factory, Role.teacher, "a")
    b = add_user(session_factory, Role.teacher, "b")
    sid = make_subject(client, a)
    cid = upload(client, a, sid).json()["id"]
    assert client.post(f"/teacher/subjects/{sid}/chapters/{cid}/retry", headers=b).status_code == 404


def test_deleting_last_chapter_for_a_hash_clears_the_extraction_cache(client, session_factory):
    from app.models import ChapterExtraction

    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    cid = upload(client, h, sid).json()["id"]

    with session_factory() as db:
        assert db.get(ChapterExtraction, db.query(ChapterExtraction).first().file_hash) is not None

    client.delete(f"/teacher/subjects/{sid}/chapters/{cid}", headers=h)
    with session_factory() as db:
        assert db.query(ChapterExtraction).count() == 0