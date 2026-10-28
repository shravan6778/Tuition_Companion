from app.models import Role, RoomMember, RoomJoinRequest


def make_user(session_factory, role, phone, name="Test User"):
    with session_factory() as db:
        user = __import__("app.models", fromlist=["User"]).User(
            supertokens_user_id=f"st-{phone}", name=name, username=f"user{phone[-6:]}",
            phone=phone, role=role, link_code=f"LINK{phone[-4:]}" if role == Role.student else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
    return user, {"Authorization": f"Bearer st-{phone}"}


def test_student_can_cancel_pending_request_and_leave_after_approval(client, session_factory):
    _, teacher_headers = make_user(session_factory, Role.teacher, "+919000000101", "Teacher")
    student, student_headers = make_user(session_factory, Role.student, "+919000000102", "Student")
    room = client.post("/teacher/rooms", json={"name": "Algebra", "room_type": "single_class"},
                       headers=teacher_headers).json()

    joined = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=student_headers)
    assert joined.status_code == 202
    assert client.get("/student/rooms", headers=student_headers).json() == []
    pending = client.get("/student/rooms/requests", headers=student_headers).json()
    assert len(pending) == 1 and pending[0]["room_name"] == "Algebra"
    assert client.delete(f"/student/rooms/{room['id']}/join-request", headers=student_headers).status_code == 204
    assert client.get("/student/rooms/requests", headers=student_headers).json() == []

    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]},
                       headers=student_headers).status_code == 202
    request_row = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=teacher_headers).json()[0]
    assert client.post(f"/teacher/rooms/{room['id']}/join-requests/{request_row['id']}/approve",
                       headers=teacher_headers).status_code == 200
    assert len(client.get("/student/rooms", headers=student_headers).json()) == 1

    assert client.delete(f"/student/rooms/{room['id']}/leave", headers=student_headers).status_code == 204
    assert client.get("/student/rooms", headers=student_headers).json() == []


def test_reject_remove_member_regenerate_code_and_typed_delete(client, session_factory):
    _, teacher_headers = make_user(session_factory, Role.teacher, "+919000000111", "Teacher")
    student, student_headers = make_user(session_factory, Role.student, "+919000000112", "Student")
    room = client.post("/teacher/rooms", json={"name": "Geometry", "room_type": "mixed_class"},
                       headers=teacher_headers).json()
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]},
                       headers=student_headers).status_code == 202
    request_row = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=teacher_headers).json()[0]
    assert client.post(f"/teacher/rooms/{room['id']}/join-requests/{request_row['id']}/reject",
                       headers=teacher_headers).status_code == 204
    assert client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=teacher_headers).json() == []

    # Rejected requests can be submitted again and then approved.
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]},
                       headers=student_headers).status_code == 202
    request_row = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=teacher_headers).json()[0]
    assert client.post(f"/teacher/rooms/{room['id']}/join-requests/{request_row['id']}/approve",
                       headers=teacher_headers).status_code == 200
    assert client.delete(f"/teacher/rooms/{room['id']}/members/{student.id}",
                         headers=teacher_headers).status_code == 204
    assert client.get(f"/teacher/rooms/{room['id']}/members", headers=teacher_headers).json() == []

    regenerated = client.post(f"/teacher/rooms/{room['id']}/regenerate-join-code", headers=teacher_headers)
    assert regenerated.status_code == 200
    assert regenerated.json()["join_code"] != room["join_code"]
    assert client.request("DELETE", f"/teacher/rooms/{room['id']}", json={"confirm_name": "wrong"},
                         headers=teacher_headers).status_code == 400
    deleted = client.request("DELETE", f"/teacher/rooms/{room['id']}", json={"confirm_name": "Geometry"},
                            headers=teacher_headers)
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": True, "assignments_deleted": 0}
