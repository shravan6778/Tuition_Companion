from app.models import Role, User


def make_user(session_factory, role: Role, phone: str, name="Test User"):
    with session_factory() as db:
        user = User(
            supertokens_user_id=f"st-{phone}",
            name=name,
            phone=phone,
            role=role,
            link_code=f"LINK{phone[-4:]}" if role == Role.student else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
    return user, {"Authorization": f"Bearer st-{phone}"}


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code == 401


def test_student_cannot_create_room(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "+919000000002")
    res = client.post("/teacher/rooms", json={"name": "Maths 10", "room_type": "single_class"}, headers=sh)
    assert res.status_code == 403


def test_full_room_and_parent_flow(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "+919000000001")
    student, sh = make_user(session_factory, Role.student, "+919000000002")
    _, ph = make_user(session_factory, Role.parent, "+919000000003")
    _, other_th = make_user(session_factory, Role.teacher, "+919000000004")

    room = client.post("/teacher/rooms", json={"name": "Maths 10", "room_type": "mixed_class"}, headers=th).json()
    assert len(room["join_code"]) == 6

    res = client.post("/student/rooms/join", json={"join_code": room["join_code"].lower()}, headers=sh)
    assert res.status_code == 200
    res = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sh)
    assert res.status_code == 409
    assert client.post("/student/rooms/join", json={"join_code": "ZZZZZZ"}, headers=sh).status_code == 404

    members = client.get(f"/teacher/rooms/{room['id']}/members", headers=th).json()
    assert [m["name"] for m in members] == ["Test User"]
    assert client.get("/teacher/rooms", headers=th).json()[0]["member_count"] == 1
    assert client.get(f"/teacher/rooms/{room['id']}/members", headers=other_th).status_code == 404

    res = client.post("/parent/link", json={"link_code": student.link_code}, headers=ph)
    assert res.status_code == 200
    kids = client.get("/parent/children", headers=ph).json()
    assert kids[0]["rooms"][0]["name"] == "Maths 10"
    assert "join_code" not in kids[0]["rooms"][0]

    assert client.post("/teacher/rooms", json={"name": "X1", "room_type": "single_class"}, headers=ph).status_code == 403
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=ph).status_code == 403