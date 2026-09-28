from pathlib import Path

from app.core.config import settings
from app.models import Role
from tests.test_library import add_user

PDF = b"%PDF-1.4\n%fake pdf body one\n"
PDF_2 = b"%PDF-1.4\n%fake pdf body two\n"


def make_subject(client, headers, name="Maths") -> str:
    return client.post("/teacher/subjects", json={"name": name}, headers=headers).json()["id"]


def upload(client, headers, subject_id, title="Ch 1", data=PDF, filename="ch1.pdf"):
    return client.post(
        f"/teacher/subjects/{subject_id}/chapters",
        data={"title": title},
        files={"file": (filename, data, "application/octet-stream")},
        headers=headers,
    )


def test_upload_stores_file_and_starts_as_uploaded(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    res = upload(client, h, sid)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "uploaded" and body["position"] == 1

    files = list(Path(settings.storage_dir).rglob("*.pdf"))
    assert len(files) == 1 and files[0].read_bytes() == PDF


def test_positions_increase_and_subject_counts_chapters(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    upload(client, h, sid, "Ch 1", PDF)
    upload(client, h, sid, "Ch 2", PDF_2)
    assert [c["position"] for c in client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()] == [1, 2]
    assert client.get("/teacher/subjects", headers=h).json()[0]["chapter_count"] == 2


def test_same_file_twice_in_a_subject_is_409(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    assert upload(client, h, sid, "Ch 1").status_code == 201
    dup = upload(client, h, sid, "Ch 1 again")
    assert dup.status_code == 409 and "Ch 1" in dup.json()["detail"]


def test_same_file_in_two_subjects_is_stored_once(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    a, b = make_subject(client, h, "Maths"), make_subject(client, h, "Physics")
    assert upload(client, h, a).status_code == 201
    assert upload(client, h, b).status_code == 201
    assert len(list(Path(settings.storage_dir).rglob("*.pdf"))) == 1


def test_rejects_non_pdf_or_image_even_if_named_pdf(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    res = upload(client, h, sid, data=b"MZ\x90\x00 not a pdf", filename="evil.pdf")
    assert res.status_code == 400


def test_rejects_empty_and_oversized(client, session_factory, monkeypatch):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    assert upload(client, h, sid, data=b"").status_code == 400
    monkeypatch.setattr(settings, "max_upload_mb", 1)
    assert upload(client, h, sid, data=b"%PDF-" + b"x" * (1024 * 1024)).status_code == 413


def test_cannot_upload_to_another_teachers_subject(client, session_factory):
    a = add_user(session_factory, Role.teacher, "a")
    b = add_user(session_factory, Role.teacher, "b")
    sid = make_subject(client, a)
    assert upload(client, b, sid).status_code == 404
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=b).status_code == 404


def test_students_cannot_upload(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    sid = make_subject(client, t)
    s = add_user(session_factory, Role.student)
    assert upload(client, s, sid).status_code == 403