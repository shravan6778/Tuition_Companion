from app.models import Role, User


def add_user(session_factory, role: Role, tag: str = "a") -> dict:
    with session_factory() as db:
        db.add(User(
            supertokens_user_id=f"st-{role.value}-{tag}",
            name="Test",
            username=f"{role.value}_{tag}",
            phone="+919000000000",
            role=role,
        ))
        db.commit()
    return {"Authorization": f"Bearer st-{role.value}-{tag}"}


def test_teacher_creates_and_lists_subjects(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    res = client.post("/teacher/subjects", json={"name": "Maths", "grade": "10"}, headers=h)
    assert res.status_code == 201
    assert res.json()["chapter_count"] == 0

    listed = client.get("/teacher/subjects", headers=h).json()
    assert [s["name"] for s in listed] == ["Maths"]


def test_duplicate_subject_name_is_409(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    assert client.post("/teacher/subjects", json={"name": "Maths"}, headers=h).status_code == 201
    assert client.post("/teacher/subjects", json={"name": "Maths"}, headers=h).status_code == 409


def test_subjects_are_private_to_their_teacher(client, session_factory):
    a = add_user(session_factory, Role.teacher, "a")
    b = add_user(session_factory, Role.teacher, "b")
    client.post("/teacher/subjects", json={"name": "Maths"}, headers=a)
    assert client.get("/teacher/subjects", headers=b).json() == []


def test_non_teachers_cannot_use_library(client, session_factory):
    for role in (Role.student, Role.parent):
        h = add_user(session_factory, role)
        assert client.get("/teacher/subjects", headers=h).status_code == 403
        assert client.post("/teacher/subjects", json={"name": "Maths"}, headers=h).status_code == 403