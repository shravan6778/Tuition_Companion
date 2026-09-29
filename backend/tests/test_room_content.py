import uuid

from sqlalchemy import update

from app.models import Role
from app.teacher import processing
from tests.test_chapters import PDF, PDF_2, make_subject, upload
from tests.test_library import add_user


def make_room(client, headers, name="Class 10") -> dict:
    return client.post("/teacher/rooms", json={"name": name, "room_type": "single_class"}, headers=headers).json()



def test_attach_list_and_detach_keeps_library_content(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    room, sid = make_room(client, t), make_subject(client, t)
    upload(client, t, sid)

    res = client.post(f"/teacher/rooms/{room['id']}/subjects", json={"subject_id": sid}, headers=t)
    assert res.status_code == 201 and res.json()[0]["name"] == "Maths"

    assert client.delete(f"/teacher/rooms/{room['id']}/subjects/{sid}", headers=t).status_code == 204
    assert client.get(f"/teacher/rooms/{room['id']}/subjects", headers=t).json() == []
    # content is a reusable library: detaching never deletes it
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=t).json()[0]["title"] == "Ch 1"


def test_same_subject_in_two_rooms(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    r1, r2, sid = make_room(client, t, "Class A"), make_room(client, t, "Class B"), make_subject(client, t)
    for r in (r1, r2):
        assert client.post(f"/teacher/rooms/{r['id']}/subjects", json={"subject_id": sid}, headers=t).status_code == 201


def test_attach_twice_is_409(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    room, sid = make_room(client, t), make_subject(client, t)
    url = f"/teacher/rooms/{room['id']}/subjects"
    assert client.post(url, json={"subject_id": sid}, headers=t).status_code == 201
    assert client.post(url, json={"subject_id": sid}, headers=t).status_code == 409


def test_teacher_cannot_attach_someone_elses_subject_or_room(client, session_factory):
    a = add_user(session_factory, Role.teacher, "a")
    b = add_user(session_factory, Role.teacher, "b")
    room_a, sid_a = make_room(client, a), make_subject(client, a)
    room_b = make_room(client, b)
    assert client.post(f"/teacher/rooms/{room_b['id']}/subjects", json={"subject_id": sid_a}, headers=b).status_code == 404
    assert client.post(f"/teacher/rooms/{room_a['id']}/subjects", json={"subject_id": sid_a}, headers=b).status_code == 404


def test_student_sees_only_ready_chapters_without_internals(client, session_factory, monkeypatch):
    class BoomProvider:
        def extract(self, data, ext):
            raise RuntimeError("provider unavailable")

    t = add_user(session_factory, Role.teacher)
    s = add_user(session_factory, Role.student)
    room, sid = make_room(client, t), make_subject(client, t)
    upload(client, t, sid, "Ch 1", PDF)  # succeeds -> ready

    monkeypatch.setattr(processing, "get_ocr_provider", lambda: BoomProvider())
    upload(client, t, sid, "Ch 2", PDF_2)  # fails -> not shown to students

    client.post(f"/teacher/rooms/{room['id']}/subjects", json={"subject_id": sid}, headers=t)
    client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=s)

    subjects = client.get(f"/student/rooms/{room['id']}/subjects", headers=s).json()
    assert subjects[0]["chapter_count"] == 1  # only the ready chapter counts
    chapters = client.get(f"/student/rooms/{room['id']}/subjects/{sid}/chapters", headers=s).json()
    assert [c["title"] for c in chapters] == ["Ch 1"]
    assert set(chapters[0]) == {"id", "title", "position"}

def test_student_outside_the_room_gets_404(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    outsider = add_user(session_factory, Role.student, "out")
    room, sid = make_room(client, t), make_subject(client, t)
    client.post(f"/teacher/rooms/{room['id']}/subjects", json={"subject_id": sid}, headers=t)
    assert client.get(f"/student/rooms/{room['id']}/subjects", headers=outsider).status_code == 404
    assert client.get(f"/student/rooms/{room['id']}/subjects/{sid}/chapters", headers=outsider).status_code == 404


def test_student_cannot_read_subject_not_attached_to_their_room(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    s = add_user(session_factory, Role.student)
    room, attached, other = make_room(client, t), make_subject(client, t, "Maths"), make_subject(client, t, "Physics")
    client.post(f"/teacher/rooms/{room['id']}/subjects", json={"subject_id": attached}, headers=t)
    client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=s)
    assert client.get(f"/student/rooms/{room['id']}/subjects/{other}/chapters", headers=s).status_code == 404


def test_roles_are_enforced_on_room_content(client, session_factory):
    t = add_user(session_factory, Role.teacher)
    room = make_room(client, t)
    for role in (Role.student, Role.parent):
        h = add_user(session_factory, role, "x")
        assert client.get(f"/teacher/rooms/{room['id']}/subjects", headers=h).status_code == 403
    parent = add_user(session_factory, Role.parent, "p")
    assert client.get(f"/student/rooms/{room['id']}/subjects", headers=parent).status_code == 403