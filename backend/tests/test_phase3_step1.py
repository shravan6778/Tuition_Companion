"""Phase 3 step 1: assignments at four levels, teacher tenancy, and the student's Today's Work."""
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.models import Assignment, Book, ChapterStatus, Concept, PageKind, Role, User, student_book
from app.pipeline.indexing import embed_chapter
from tests.test_book_access import join_room_of, make_user
from tests.test_phase3_settle import CELL, EXERCISE, TISSUE, add_chapter


EXERCISE_LABELLED = EXERCISE + " Exercise 1.1 is about cells. Exercise 1.2 is about tissue."


def make_world(session_factory, with_exercise_vectors=False):
    """A teacher, and "studenta" who owns a private Science book: ch1 (ready, 2 concepts + an exercise page), ch2 (ready),
    ch3 (empty). Teachers no longer own books; they assign from a book of a student in their room, and each student's
    own copy is found by subject + chapter title. `room_with_student` puts studenta in the teacher's room."""
    teacher, th = make_user(session_factory, Role.teacher, "teachera")
    owner, _ = make_user(session_factory, Role.student, "studenta")
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="Pub", is_reference=False, owner_student_id=owner.id)
        db.add(book)
        db.flush()
        ch1 = add_chapter(db, book, "Cells", 1,
                          [(1, CELL, PageKind.CONTENT), (2, TISSUE, PageKind.CONTENT), (3, EXERCISE_LABELLED, PageKind.EXERCISE)],
                          [(1, "Cell", "basic unit"), (2, "Tissue", "group of cells")])
        ch2 = add_chapter(db, book, "Force", 2, [(1, "Force is a push or a pull " * 6, PageKind.CONTENT)], [(1, "Force", "push or pull")])
        ch3 = add_chapter(db, book, "Empty", 3, [], status=ChapterStatus.EMPTY)
        db.commit()
        if with_exercise_vectors:
            for ch in (ch1, ch2):
                embed_chapter(db, ch, FakeEmbeddingProvider(settings.embedding_dim))
            db.commit()
        concepts = {c.name: str(c.id) for c in db.scalars(select(Concept))}
        ids = dict(book=str(book.id), ch1=str(ch1.id), ch2=str(ch2.id), ch3=str(ch3.id))
    return teacher, th, ids, concepts


def room_with_student(client, session_factory, th, tag="studenta", link_book=None):
    sh = {"Authorization": f"Bearer st-{tag}"}
    with session_factory() as db:  # "studenta" already exists: make_world created the owner of the book
        student = db.scalar(select(User).where(User.username == tag))
        if student is not None:
            db.expunge(student)
    if student is None:
        student, sh = make_user(session_factory, Role.student, tag)
    room = client.post("/teacher/rooms", json={"name": "Room One", "room_type": "single_class"}, headers=th).json()
    joined = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sh)
    assert joined.status_code == 202, joined.text
    pending = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=th)
    assert pending.status_code == 200, pending.text
    request_id = pending.json()[0]["id"]
    approved = client.post(f"/teacher/rooms/{room['id']}/join-requests/{request_id}/approve", headers=th)
    assert approved.status_code == 200, approved.text
    if link_book:  # only a reference book needs linking; a student's own book is theirs already
        assert client.post(f"/student/books/{link_book}/link", headers=sh).status_code == 200
    return student, sh, room


def join_existing(client, session_factory, th, room, tag):
    """Another student asks to join `room` and the teacher approves."""
    student, sh = make_user(session_factory, Role.student, tag)
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sh).status_code == 202
    pending = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=th).json()
    request_id = next(r["id"] for r in pending if r["student_id"] == str(student.id))
    assert client.post(f"/teacher/rooms/{room['id']}/join-requests/{request_id}/approve", headers=th).status_code == 200
    return student, sh


def create(client, th, **body):
    return client.post("/teacher/assignments", json=body, headers=th)


# ---- the four levels --------------------------------------------------------

def test_chapter_level_stores_the_chapters_concepts(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    res = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"])
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["title"] == "Cells" and body["concept_count"] == 2
    assert [c["name"] for c in body["concepts"]] == ["Cell", "Tissue"]


def test_subject_level_covers_every_ready_chapter_of_the_book(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    body = create(client, th, level="subject", book_id=ids["book"], room_id=room["id"]).json()
    assert sorted(c["name"] for c in body["concepts"]) == ["Cell", "Force", "Tissue"]  # the empty chapter adds nothing


def test_concept_level_keeps_the_picked_order_and_drops_duplicates(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    picked = [concepts["Tissue"], concepts["Cell"], concepts["Tissue"]]  # a concept assignment sits inside one chapter
    body = create(client, th, level="concept", book_id=ids["book"], chapter_id=ids["ch1"], concept_ids=picked, room_id=room["id"]).json()
    assert [c["name"] for c in body["concepts"]] == ["Tissue", "Cell"]


def test_exercise_level_stores_the_label_and_the_confirmed_concepts(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    res = create(client, th, level="exercise", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"],
                 item_label="Exercise 1.1", concept_ids=[concepts["Cell"]])
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["item_label"] == "Exercise 1.1" and [c["name"] for c in body["concepts"]] == ["Cell"]
    assert body["chapter_title"] == "Cells" and body["subject"] == "Science"


def test_exercise_level_needs_a_label(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    assert create(client, th, level="exercise", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).status_code == 422


def test_exercise_concepts_must_come_from_that_chapter(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    res = create(client, th, level="exercise", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"],
                 item_label="Exercise 1.1", concept_ids=[concepts["Force"]])  # Force lives in chapter 2
    assert res.status_code == 404


def test_exercise_label_that_does_not_exist_is_404(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    res = create(client, th, level="exercise", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"],
                 item_label="Exercise 99.9", concept_ids=[concepts["Cell"]])
    assert res.status_code == 404


def test_unready_chapter_cannot_be_assigned(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    assert create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch3"], room_id=room["id"]).status_code == 409


def test_unknown_concept_is_404_not_silently_dropped(client, session_factory):
    _, th, ids, concepts = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    res = create(client, th, level="concept", book_id=ids["book"], room_id=room["id"],
                 concept_ids=[concepts["Cell"], str(uuid.uuid4())])
    assert res.status_code == 404


def test_target_must_be_exactly_one_of_room_or_student(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    student, _, room = room_with_student(client, session_factory, th)
    base = dict(level="chapter", book_id=ids["book"], chapter_id=ids["ch1"])
    assert create(client, th, **base).status_code == 422
    assert create(client, th, **base, room_id=room["id"], student_id=str(student.id)).status_code == 422
    assert create(client, th, **base, student_id=str(student.id)).status_code == 201


# ---- exercise proposal ------------------------------------------------------

def test_exercise_proposal_returns_candidates_and_writes_nothing(client, session_factory):
    _, th, ids, _ = make_world(session_factory, with_exercise_vectors=True)
    room_with_student(client, session_factory, th)  # the book is the student's: the teacher sees its metadata through the room
    res = client.post("/teacher/assignments/exercise-proposal",
                      json={"book_id": ids["book"], "chapter_id": ids["ch1"], "page_numbers": [3]}, headers=th)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["chapter_title"] == "Cells" and body["exercise_pages"] == [3]
    assert body["status"] in ("ok", "no_vectors")
    with session_factory() as db:
        assert db.scalars(select(Assignment)).all() == []


def test_exercise_proposal_without_exercise_pages_says_so(client, session_factory):
    _, th, ids, _ = make_world(session_factory, with_exercise_vectors=True)
    room_with_student(client, session_factory, th)
    res = client.post("/teacher/assignments/exercise-proposal", json={"book_id": ids["book"], "chapter_id": ids["ch2"]}, headers=th)
    assert res.json()["status"] == "no_exercise_pages"


# ---- teacher tenancy --------------------------------------------------------

def test_other_teacher_cannot_assign_from_my_book_or_to_my_room(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    other_room = client.post("/teacher/rooms", json={"name": "Room Bee", "room_type": "single_class"}, headers=bh).json()
    # my book, their room -> the book is invisible to them
    assert create(client, bh, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=other_room["id"]).status_code == 404
    # their own book would be fine, but my room is not theirs
    mine = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    assert create(client, bh, level="subject", book_id=ids["book"], room_id=room["id"]).status_code == 404
    assert client.get(f"/teacher/assignments/{mine['id']}", headers=bh).status_code == 404
    assert client.delete(f"/teacher/assignments/{mine['id']}", headers=bh).status_code == 404
    assert client.get("/teacher/assignments", headers=bh).json() == []


def test_cannot_assign_to_a_student_outside_my_rooms(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    room_with_student(client, session_factory, th)  # the book is visible to this teacher, so the 404 below is about the student
    stranger, _ = make_user(session_factory, Role.student, "strangers")
    res = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], student_id=str(stranger.id))
    assert res.status_code == 404


def test_roles_are_enforced(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, sh, _ = room_with_student(client, session_factory, th)
    assert client.get("/teacher/assignments", headers=sh).status_code == 403
    assert client.get("/student/assignments", headers=th).status_code == 403


def test_teacher_can_list_filter_and_delete(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    student, _, room = room_with_student(client, session_factory, th)
    a = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    b = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch2"], student_id=str(student.id)).json()
    assert {x["id"] for x in client.get("/teacher/assignments", headers=th).json()} == {a["id"], b["id"]}
    assert [x["id"] for x in client.get(f"/teacher/assignments?room_id={room['id']}", headers=th).json()] == [a["id"]]
    assert {x["id"] for x in client.get(f"/teacher/assignments?student_id={student.id}", headers=th).json()} == {a["id"], b["id"]}
    assert client.delete(f"/teacher/assignments/{a['id']}", headers=th).status_code == 204
    assert client.get(f"/teacher/assignments/{a['id']}", headers=th).status_code == 404
    with session_factory() as db:  # the concept list went with it, the concepts themselves stay
        assert len(db.scalars(select(Concept)).all()) == 3


# ---- the student's Today's Work --------------------------------------------

def test_student_sees_room_and_personal_work_resolved_against_their_own_copy(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    student, sh, room = room_with_student(client, session_factory, th)
    a = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    b = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch2"], student_id=str(student.id)).json()
    mine = client.get("/student/assignments", headers=sh).json()
    assert {x["id"] for x in mine} == {a["id"], b["id"]} and all(x["available"] for x in mine)
    detail = client.get(f"/student/assignments/{a['id']}", headers=sh).json()
    assert detail["concept_count"] == 2 and detail["chapter_title"] == "Cells"
    assert detail["resolved_book_id"] == ids["book"] and detail["resolved_chapter_id"] == ids["ch1"]


def test_a_student_without_that_chapter_is_asked_to_upload_it(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, _, room = room_with_student(client, session_factory, th)
    _, bh = join_existing(client, session_factory, th, room, "studentb")  # studentb has no book at all
    a = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    [seen] = client.get("/student/assignments", headers=bh).json()
    assert seen["id"] == a["id"] and seen["available"] is False
    assert seen["availability_message"] == "Upload this chapter to see this task."
    assert seen["resolved_book_id"] is None and seen["resolved_chapter_id"] is None
    # and the owner's private book is never what studentb resolves to
    assert client.get(f"/student/books/{ids['book']}", headers=bh).status_code == 404


def test_student_never_sees_work_meant_for_someone_else(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    s1, h1, room = room_with_student(client, session_factory, th, "studenta")
    s2, h2 = make_user(session_factory, Role.student, "studentb")
    other_room = client.post("/teacher/rooms", json={"name": "Room Two", "room_type": "single_class"}, headers=th).json()
    client.post("/student/rooms/join", json={"join_code": other_room["join_code"]}, headers=h2)  # pending, not approved
    mine = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], student_id=str(s1.id)).json()
    in_room = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch2"], room_id=room["id"]).json()
    assert {x["id"] for x in client.get("/student/assignments", headers=h2).json()} == set()
    assert client.get(f"/student/assignments/{mine['id']}", headers=h2).status_code == 404
    assert client.get(f"/student/assignments/{in_room['id']}", headers=h2).status_code == 404
    # a student of ANOTHER teacher sees nothing either
    _, oh = make_user(session_factory, Role.teacher, "teacherb")
    _, h3, _ = room_with_student(client, session_factory, oh, "studentc")
    assert client.get("/student/assignments", headers=h3).json() == []


def test_todays_work_orders_by_due_date_then_undated_last(client, session_factory):
    _, th, ids, _ = make_world(session_factory)
    _, sh, room = room_with_student(client, session_factory, th)
    soon, later = date.today() + timedelta(days=1), date.today() + timedelta(days=5)
    undated = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    far = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch2"], room_id=room["id"], due_date=str(later)).json()
    near = create(client, th, level="subject", book_id=ids["book"], room_id=room["id"], due_date=str(soon)).json()
    order = [x["id"] for x in client.get("/student/assignments", headers=sh).json()]
    assert order == [near["id"], far["id"], undated["id"]]


def test_assignment_keeps_its_concepts_when_a_chapter_is_reprocessed(client, session_factory):
    """The stored list is what was assigned; a chapter going back to `processing` must not empty it."""
    _, th, ids, _ = make_world(session_factory)
    _, sh, room = room_with_student(client, session_factory, th)
    a = create(client, th, level="chapter", book_id=ids["book"], chapter_id=ids["ch1"], room_id=room["id"]).json()
    with session_factory() as db:
        from app.models import Chapter
        db.get(Chapter, uuid.UUID(ids["ch1"])).status = ChapterStatus.PROCESSING
        db.commit()
    assert client.get(f"/student/assignments/{a['id']}", headers=sh).json()["concept_count"] == 2
