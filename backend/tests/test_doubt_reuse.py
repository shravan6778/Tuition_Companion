import uuid

from sqlalchemy import select

from app.models import Doubt, Role
from tests.test_phase3_step2 import TISSUE_Q, ask, assign, world  # noqa: F401
from tests.test_phase3_step3 import GOOD, Scripted, use_model


def test_same_normalized_doubt_reuses_saved_answer_without_another_llm_call(client, session_factory, world, monkeypatch):
    llm = use_model(monkeypatch, Scripted(GOOD))
    assignment = assign(client, world)

    first = ask(client, world, TISSUE_Q, assignment)
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["answer_status"] == "answered"

    second = ask(client, world, "  WHAT is a tissue???  ", assignment)
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["reused"] is True
    assert "You asked this on" in second_body["message"]
    assert second_body["answer"] == first_body["answer"]
    assert len(llm.prompts) == 1

    with session_factory() as db:
        assert len(db.scalars(select(Doubt)).all()) == 1


def test_explain_differently_creates_a_thread_and_calls_llm_again(client, session_factory, world, monkeypatch):
    llm = use_model(monkeypatch, Scripted(GOOD, GOOD))
    assignment = assign(client, world)

    first = ask(client, world, TISSUE_Q, assignment)
    assert first.status_code == 200
    first_id = first.json()["id"]

    followup = client.post(
        "/student/doubts",
        json={
            "text": "Explain this more simply.",
            "assignment_id": assignment["id"],
            "parent_doubt_id": first_id,
        },
        headers=world["sh"],
    )
    assert followup.status_code == 200, followup.text
    body = followup.json()
    assert body["reused"] is False
    assert body["parent_doubt_id"] == first_id
    assert body["answer_status"] == "answered"
    assert len(llm.prompts) == 2

    with session_factory() as db:
        rows = db.scalars(select(Doubt).order_by(Doubt.created_at)).all()
        assert len(rows) == 2
        assert rows[1].parent_doubt_id == uuid.UUID(first_id)


def test_cannot_create_a_followup_from_another_students_doubt(client, world, make_user, as_user):
    other = make_user(Role.student)
    first = ask(client, world, TISSUE_Q, assign(client, world))
    first_id = first.json()["id"]

    # world student is still authenticated; parent_doubt_id must belong to that student.
    as_user(other)
    res = client.post(
        "/student/doubts",
        json={"text": "Explain simpler.", "parent_doubt_id": first_id},
    )
    assert res.status_code == 404
