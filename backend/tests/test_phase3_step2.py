"""Phase 3 step 2: POST /student/doubts, the retrieval step (no explanation yet)."""
import uuid

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models import Assignment, Book, Chapter, Doubt, PageKind, Role
from app.pipeline.indexing import index_chapter
from tests.test_book_access import make_user
from tests.test_phase3_step1 import create, make_world, room_with_student
from tests.test_phase3_settle import TISSUE, add_chapter

TISSUE_Q = "what is a tissue group of similar cells"
NOISE_Q = "zebra quantum jukebox harmonica"


@pytest.fixture()
def world(client, session_factory, indexing_on, monkeypatch):
    """A teacher's book (Cells, Force) indexed into the fake store, one student who linked it and sits in the room."""
    monkeypatch.setattr(settings, "retrieval_min_similarity", 0.5)
    teacher, th, ids, concepts = make_world(session_factory)
    for chapter in (ids["ch1"], ids["ch2"]):
        index_chapter(session_factory, uuid.UUID(chapter))
    student, sh, room = room_with_student(client, session_factory, th, link_book=ids["book"])
    return dict(th=th, sh=sh, student=student, room=room, ids=ids, concepts=concepts)


def assign(client, w, level="chapter", chapter="ch1", **extra):
    body = dict(level=level, book_id=w["ids"]["book"], room_id=w["room"]["id"], **extra)
    if chapter:
        body["chapter_id"] = w["ids"][chapter]
    res = create(client, w["th"], **body)
    assert res.status_code == 201, res.text
    return res.json()


def ask(client, w, text, assignment=None, headers=None):
    body = {"text": text}
    if assignment:
        body["assignment_id"] = assignment["id"]
    return client.post("/student/doubts", json=body, headers=headers or w["sh"])


def test_doubt_inside_the_assignment_is_grounded_with_page_text_and_stored(client, session_factory, world):
    a = assign(client, world)
    res = ask(client, world, TISSUE_Q, a)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "grounded" and body["request_chapter"] is None
    assert body["pages"][0]["excerpt"].startswith("A tissue is a group") and body["pages"][0]["chapter_title"] == "Cells"
    assert body["concepts"][0]["name"] == "Tissue"
    assert body["prerequisites"] == []  # this fixture has no prerequisite edges
    with session_factory() as db:
        row = db.scalars(select(Doubt)).one()
        assert row.student_id == world["student"].id and str(row.assignment_id) == a["id"]
        assert row.status == "grounded" and str(row.concept_id) == world["concepts"]["Tissue"] and row.confidence >= 0.5


def test_a_narrower_assignment_sends_the_doubt_to_ask_a_doubt(client, world):
    cell_only = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Cell"]])
    body = ask(client, world, TISSUE_Q, cell_only).json()
    assert body["status"] == "outside_assignment" and body["pages"] == []
    assert "Tissue" in [h["name"] for h in body["elsewhere"]] and "Ask a Doubt" in body["message"]


def test_a_doubt_the_books_do_not_cover_points_to_the_chapter_request_flow(client, session_factory, world):
    a = assign(client, world)
    body = ask(client, world, NOISE_Q, a).json()
    assert body["status"] == "not_in_book" and body["pages"] == [] and body["concepts"] == []
    assert body["request_chapter"] == {"book_id": world["ids"]["book"], "path": f"/student/books/{world['ids']['book']}/chapter-requests"}
    # the path it names is the real, existing route
    assert client.post(body["request_chapter"]["path"], json={"chapter_hint": "Photosynthesis"}, headers=world["sh"]).status_code in (200, 201)


def test_when_the_search_services_are_down_it_says_so_and_never_guesses(client, session_factory, world, monkeypatch):
    from app.graph_store import FAKE_STORE
    a = assign(client, world)
    FAKE_STORE.fail_with = RuntimeError("down")
    body = ask(client, world, TISSUE_Q, a).json()
    assert body["status"] == "unavailable" and body["pages"] == [] and body["concepts"] == []
    monkeypatch.setattr(settings, "embedding_provider", "none")  # switched off entirely
    FAKE_STORE.fail_with = None
    assert ask(client, world, TISSUE_Q, a).json()["status"] == "unavailable"
    with session_factory() as db:
        assert [d.status for d in db.scalars(select(Doubt).order_by(Doubt.created_at))] == ["unavailable", "unavailable"]


def test_a_standalone_doubt_searches_all_linked_books_and_has_no_assignment(client, session_factory, world):
    body = ask(client, world, TISSUE_Q).json()
    assert body["status"] == "grounded" and body["assignment_id"] is None and body["request_chapter"] is None
    assert ask(client, world, NOISE_Q).json()["request_chapter"] is None  # no assignment, so no particular book to ask about


def test_a_student_with_no_linked_book_gets_not_in_book_not_everything(client, session_factory, world):
    _, bare = make_user(session_factory, Role.student, "studentz")
    assert ask(client, world, TISSUE_Q, headers=bare).json()["status"] == "not_in_book"


def test_another_teachers_private_book_is_never_searched(client, session_factory, world):
    secret_owner, _ = make_user(session_factory, Role.teacher, "teacherc")
    with session_factory() as db:
        secret = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="X", owner_teacher_id=secret_owner.id)
        db.add(secret)
        db.flush()
        ch = add_chapter(db, secret, "Secret", 1, [(1, "photosynthesis converts sunlight water and carbon dioxide into glucose and oxygen in the chloroplast of green leaves", PageKind.CONTENT)],
                         [(1, "Photosynthesis", "Plants make glucose from sunlight water and carbon dioxide")])
        db.commit()
        chapter_id = ch.id
    index_chapter(session_factory, chapter_id)
    q = "photosynthesis sunlight water carbon dioxide glucose chloroplast"
    body = ask(client, world, q, assign(client, world)).json()
    assert body["status"] != "grounded" and all(p["chapter_title"] != "Secret" for p in body["pages"])
    assert ask(client, world, q).json()["status"] == "not_in_book"


def test_an_assignment_that_is_not_mine_is_404(client, session_factory, world):
    a = assign(client, world)
    _, other = make_user(session_factory, Role.student, "studentb")
    assert ask(client, world, TISSUE_Q, a, headers=other).status_code == 404
    assert ask(client, world, TISSUE_Q, {"id": str(uuid.uuid4())}).status_code == 404
    with session_factory() as db:
        assert db.scalars(select(Doubt)).all() == []  # a refused doubt leaves no trace


def test_unlinking_the_book_hides_the_assignment_and_its_doubt_button(client, world):
    a = assign(client, world)
    client.delete(f"/student/books/{world['ids']['book']}/link", headers=world["sh"])
    assert ask(client, world, TISSUE_Q, a).status_code == 404


def test_blank_or_huge_text_is_refused(client, world):
    assert ask(client, world, "   ").status_code == 422
    assert ask(client, world, "x " * 600).status_code == 422


def test_each_student_is_rate_limited(client, session_factory, world, monkeypatch):
    monkeypatch.setattr(settings, "rate_doubts_per_hour", 2)
    a = assign(client, world)
    assert [ask(client, world, TISSUE_Q, a).status_code for _ in range(3)] == [200, 200, 429]
    _, other = make_user(session_factory, Role.student, "studentb")
    assert ask(client, world, TISSUE_Q, headers=other).status_code == 200  # someone else is unaffected


def test_history_is_only_my_own_and_can_be_filtered_by_assignment(client, session_factory, world):
    a, b = assign(client, world), assign(client, world, chapter="ch2")
    ask(client, world, TISSUE_Q, a)
    ask(client, world, NOISE_Q, b)
    _, other = make_user(session_factory, Role.student, "studentb")
    ask(client, world, TISSUE_Q, headers=other)
    mine = client.get("/student/doubts", headers=world["sh"]).json()
    assert [d["text"] for d in mine] == [NOISE_Q, TISSUE_Q]
    assert [d["text"] for d in client.get(f"/student/doubts?assignment_id={a['id']}", headers=world["sh"]).json()] == [TISSUE_Q]
    assert len(client.get("/student/doubts", headers=other).json()) == 1


def test_deleting_the_assignment_keeps_the_doubt_history(client, session_factory, world):
    a = assign(client, world)
    ask(client, world, TISSUE_Q, a)
    assert client.delete(f"/teacher/assignments/{a['id']}", headers=world["th"]).status_code == 204
    with session_factory() as db:
        row = db.scalars(select(Doubt)).one()
        assert row.assignment_id is None and row.text == TISSUE_Q


def test_only_students_may_ask(client, world):
    assert client.post("/student/doubts", json={"text": TISSUE_Q}, headers=world["th"]).status_code == 403
    assert client.post("/student/doubts", json={"text": TISSUE_Q}).status_code == 401
