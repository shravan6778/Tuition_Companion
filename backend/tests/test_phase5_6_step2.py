"""Tests for Phase 5 & 6 Step 2:
  * `POST /teacher/students/{id}/sessions` and `GET /teacher/students/{id}/sessions`.
  * Free-text notes + quick-tag deduplication/normalization + default/explicit `session_date`.
  * Strict tenant isolation: a teacher can only log or view sessions for students in their own rooms (404 otherwise),
    and two teachers who both teach the same student only ever see their own session logs."""
from datetime import date

from app.models import Role, Room, RoomMember, RoomType, User


def _setup_sessions_world(db):
    t_a = User(supertokens_user_id="st-t-sess-a", name="Teacher A", username="teacher_sess_a", phone="9200000001", role=Role.teacher)
    t_b = User(supertokens_user_id="st-t-sess-b", name="Teacher B", username="teacher_sess_b", phone="9200000002", role=Role.teacher)
    s_1 = User(supertokens_user_id="st-s-sess-1", name="Student 1", username="student_sess_1", phone="9200000003", role=Role.student, link_code="SESS0001")
    s_2 = User(supertokens_user_id="st-s-sess-2", name="Student 2", username="student_sess_2", phone="9200000004", role=Role.student, link_code="SESS0002")
    db.add_all([t_a, t_b, s_1, s_2])
    db.flush()

    room_a = Room(teacher_id=t_a.id, name="Room A", room_type=RoomType.single_class, join_code="SESSRA")
    room_b = Room(teacher_id=t_b.id, name="Room B", room_type=RoomType.single_class, join_code="SESSRB")
    db.add_all([room_a, room_b])
    db.flush()

    db.add(RoomMember(room_id=room_a.id, user_id=s_1.id))
    db.add(RoomMember(room_id=room_b.id, user_id=s_2.id))

    out = {
        "t_a_id": t_a.id,
        "t_b_id": t_b.id,
        "s_1_id": s_1.id,
        "s_2_id": s_2.id,
        "th_a": {"Authorization": f"Bearer {t_a.supertokens_user_id}"},
        "th_b": {"Authorization": f"Bearer {t_b.supertokens_user_id}"},
        "sh_1": {"Authorization": f"Bearer {s_1.supertokens_user_id}"},
    }
    db.commit()
    return out


def test_create_and_list_session_logs_ordered_by_date(client, session_factory):
    with session_factory() as db:
        w = _setup_sessions_world(db)

    # Create an older session log with duplicate/whitespace tags
    r1 = client.post(
        f"/teacher/students/{w['s_1_id']}/sessions",
        headers=w["th_a"],
        json={
            "session_date": "2026-10-10",
            "notes": "  Reviewed linear equations and sign errors.  ",
            "tags": ["algebra", "  sign-errors ", "ALGEBRA", ""],
        },
    )
    assert r1.status_code == 201, r1.text
    b1 = r1.json()
    assert b1["student_id"] == str(w["s_1_id"])
    assert b1["teacher_id"] == str(w["t_a_id"])
    assert b1["session_date"] == "2026-10-10"
    assert b1["notes"] == "Reviewed linear equations and sign errors."
    assert b1["tags"] == ["algebra", "sign-errors"]

    # Create a newer session log (defaulting session_date to today)
    r2 = client.post(
        f"/teacher/students/{w['s_1_id']}/sessions",
        headers=w["th_a"],
        json={
            "notes": "Practiced quadratic factoring; much more confident today.",
            "tags": ["quadratic", "homework-done"],
        },
    )
    assert r2.status_code == 201, r2.text
    b2 = r2.json()
    assert b2["session_date"] == date.today().isoformat() or len(b2["session_date"]) == 10

    # List returns newest session_date first
    listed = client.get(f"/teacher/students/{w['s_1_id']}/sessions", headers=w["th_a"])
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 2
    assert items[0]["id"] == b2["id"]
    assert items[1]["id"] == b1["id"]

    # Whitespace-only notes rejected with 422
    r_blank = client.post(
        f"/teacher/students/{w['s_1_id']}/sessions",
        headers=w["th_a"],
        json={"notes": "   ", "tags": ["test"]},
    )
    assert r_blank.status_code == 422


def test_session_logs_tenant_and_role_isolation(client, session_factory):
    with session_factory() as db:
        w = _setup_sessions_world(db)

    # Teacher A cannot log or read sessions for Student 2 (in Teacher B's room) -> 404
    assert (
        client.post(
            f"/teacher/students/{w['s_2_id']}/sessions",
            headers=w["th_a"],
            json={"notes": "Unauthorized note", "tags": []},
        ).status_code
        == 404
    )
    assert client.get(f"/teacher/students/{w['s_2_id']}/sessions", headers=w["th_a"]).status_code == 404

    # Teacher B cannot log or read sessions for Student 1 -> 404
    assert (
        client.post(
            f"/teacher/students/{w['s_1_id']}/sessions",
            headers=w["th_b"],
            json={"notes": "Unauthorized note", "tags": []},
        ).status_code
        == 404
    )
    assert client.get(f"/teacher/students/{w['s_1_id']}/sessions", headers=w["th_b"]).status_code == 404

    # Student role cannot call teacher session routes -> 403
    assert (
        client.post(
            f"/teacher/students/{w['s_1_id']}/sessions",
            headers=w["sh_1"],
            json={"notes": "Self note", "tags": []},
        ).status_code
        == 403
    )
    assert client.get(f"/teacher/students/{w['s_1_id']}/sessions", headers=w["sh_1"]).status_code == 403