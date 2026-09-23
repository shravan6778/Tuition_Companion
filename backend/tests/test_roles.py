import pytest

from app.models import Role, User

#update fixtures for username field
def add_user(session_factory, role: Role):
    with session_factory() as db:
        db.add(User(
            supertokens_user_id=f"st-{role.value}",
            name="Test",
            username=f"{role.value}_user",
            phone="+919000000000",
            role=role,
        ))
        db.commit()


def test_no_session_is_401(client):
    assert client.get("/teacher/ping").status_code == 401


def test_unknown_session_user_is_401(client):
    res = client.get("/teacher/ping", headers={"Authorization": "Bearer st-ghost"})
    assert res.status_code == 401


@pytest.mark.parametrize("role", list(Role))
def test_each_role_only_reaches_its_own_routes(client, session_factory, role):
    add_user(session_factory, role)
    headers = {"Authorization": f"Bearer st-{role.value}"}
    for target in Role:
        res = client.get(f"/{target.value}/ping", headers=headers)
        assert res.status_code == (200 if target == role else 403)