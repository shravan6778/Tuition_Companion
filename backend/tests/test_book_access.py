"""Content tenancy: reference books are shared and read-only; every other book is private to the student who uploaded it."""
import uuid

from app.models import Book, Role, User

FAKE_PDF = ("p.pdf", b"%PDF-1.4 fake", "application/pdf")


def make_user(session_factory, role: Role, tag: str):
    with session_factory() as db:
        user = User(
            supertokens_user_id=f"st-{tag}", name=tag, username=tag, phone="9" + tag[-3:], role=role,
            link_code=f"LNK{tag[-3:]}".upper()[:12] if role == Role.student else None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
    return user, {"Authorization": f"Bearer st-{tag}"}


def reference_book(session_factory) -> str:
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
        db.add(book)
        db.commit()
        return str(book.id)


def new_book(client, headers, **overrides) -> dict:
    """A student creates a private book (teachers can no longer create books)."""
    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "Private Pub", **overrides}
    res = client.post("/student/books", json=body, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def new_chapter(client, headers, book_id) -> str:
    res = client.post(f"/student/books/{book_id}/chapters", json={"title": "Ch 1", "sequence_num": 1}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def join_room_of(client, session_factory, teacher_headers, student_headers):
    """Create an approved membership for tests unrelated to the approval workflow."""
    room = client.post("/teacher/rooms", json={"name": "Room A", "room_type": "single_class"}, headers=teacher_headers).json()
    joined = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=student_headers)
    assert joined.status_code == 202, joined.text
    requests = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=teacher_headers)
    assert requests.status_code == 200, requests.text
    pending = requests.json()
    assert len(pending) == 1
    approved = client.post(
        f"/teacher/rooms/{room['id']}/join-requests/{pending[0]['id']}/approve",
        headers=teacher_headers,
    )
    assert approved.status_code == 200, approved.text
    return room


# ---- the owner -----------------------------------------------------------------

def test_created_book_is_owned_by_the_student_and_never_reference(client, session_factory):
    a, ah = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, ah, publisher="NCERT")  # even labelled "NCERT", a student's book is private
    assert book["is_reference"] is False
    with session_factory() as db:
        row = db.get(Book, uuid.UUID(book["id"]))
        assert row.owner_student_id == a.id and row.is_reference is False


def test_the_database_refuses_a_book_that_is_both_or_neither(session_factory):
    """The XOR constraint: reference (no owner) or student-owned, nothing else."""
    import pytest
    from sqlalchemy.exc import IntegrityError

    s, _ = make_user(session_factory, Role.student, "studenta")
    base = dict(board="CBSE", class_name="Class 9", subject="Science", publisher="P")
    for bad in (dict(is_reference=True, owner_student_id=s.id), dict(is_reference=False, owner_student_id=None)):
        with session_factory() as db:
            db.add(Book(**base, **bad))
            with pytest.raises(IntegrityError):
                db.commit()


def test_student_cannot_see_or_modify_another_students_book(client, session_factory):
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
    book = new_book(client, ah)
    ch = new_chapter(client, ah, book["id"])

    assert client.get(f"/student/books/{book['id']}", headers=bh).status_code == 404
    assert client.get(f"/student/books/{book['id']}/chapters", headers=bh).status_code == 404
    assert client.get(f"/student/books/{book['id']}/chapters/{ch}/pages", headers=bh).status_code == 404
    assert client.post(f"/student/books/{book['id']}/chapters", json={"title": "X", "sequence_num": 2}, headers=bh).status_code == 404
    res = client.post(f"/student/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=bh)
    assert res.status_code == 404
    assert client.delete(f"/student/books/{book['id']}", headers=bh).status_code == 404
    assert client.post(f"/student/books/{book['id']}/link", headers=bh).status_code == 404
    assert book["id"] not in [b["id"] for b in client.get("/student/books", headers=bh).json()]
    assert book["id"] not in [b["id"] for b in client.get("/student/library", headers=bh).json()]
    # the owner still works
    assert client.get(f"/student/books/{book['id']}", headers=ah).status_code == 200


def test_reference_books_are_visible_to_students_but_read_only(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "studenta")
    ref_id = reference_book(session_factory)

    assert ref_id in [b["id"] for b in client.get("/student/library", headers=sh).json()]
    assert client.get(f"/student/books/{ref_id}", headers=sh).json()["is_reference"] is True
    assert client.post(f"/student/books/{ref_id}/chapters", json={"title": "X", "sequence_num": 1}, headers=sh).status_code == 403
    res = client.post(f"/student/books/{ref_id}/chapters/{uuid.uuid4()}/pages/upload", files={"file": FAKE_PDF}, headers=sh)
    assert res.status_code == 403
    assert client.delete(f"/student/books/{ref_id}", headers=sh).status_code == 403  # "remove book" never touches NCERT


def test_a_reference_book_is_linked_but_an_own_book_needs_no_link(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "studenta")
    ref_id = reference_book(session_factory)
    mine = new_book(client, sh)

    assert client.post(f"/student/books/{ref_id}/link", headers=sh).json()["status"] == "linked"
    assert client.post(f"/student/books/{ref_id}/link", headers=sh).json()["status"] == "already_linked"
    assert client.post(f"/student/books/{mine['id']}/link", headers=sh).status_code == 409  # already yours
    assert {b["id"] for b in client.get("/student/books", headers=sh).json()} == {ref_id, mine["id"]}
    assert ref_id not in [b["id"] for b in client.get("/student/library", headers=sh).json()]  # linked: no longer on offer
    client.delete(f"/student/books/{ref_id}/link", headers=sh)
    assert {b["id"] for b in client.get("/student/books", headers=sh).json()} == {mine["id"]}


def test_variant_of_can_only_be_a_reference_book(client, session_factory):
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
    ref_id = reference_book(session_factory)
    a_book = new_book(client, ah)

    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "P", "is_customized": True}
    assert client.post("/student/books", json={**body, "variant_of_id": a_book["id"]}, headers=bh).status_code == 404  # someone else's
    assert client.post("/student/books", json={**body, "variant_of_id": a_book["id"]}, headers=ah).status_code == 404  # even one's own
    assert client.post("/student/books", json={**body, "variant_of_id": ref_id}, headers=bh).status_code == 201


def test_removing_a_book_deletes_its_pages_and_stored_pdf(client, session_factory):
    import os
    from sqlalchemy import select

    from app.core.config import settings
    from app.models import Chapter, Page
    from tests.test_pipeline import _text_pdf

    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    ch = new_chapter(client, sh, book["id"])
    up = client.post(f"/student/books/{book['id']}/chapters/{ch}/pages/upload",
                     files={"file": ("c.pdf", _text_pdf("page one", "page two"), "application/pdf")}, headers=sh)
    assert up.status_code == 202, up.text
    with session_factory() as db:
        stored = db.get(Chapter, uuid.UUID(ch)).source_file
        assert db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(ch))).all()
    assert os.path.exists(os.path.join(settings.storage_dir, stored))

    assert client.delete(f"/student/books/{book['id']}", headers=sh).status_code == 204
    with session_factory() as db:
        assert db.get(Book, uuid.UUID(book["id"])) is None
        assert db.get(Chapter, uuid.UUID(ch)) is None
        assert db.scalars(select(Page)).all() == []
    assert not os.path.exists(os.path.join(settings.storage_dir, stored))
    assert client.get("/student/books", headers=sh).json() == []


# ---- teachers ----------------------------------------------------------------------

def test_teachers_can_no_longer_create_or_upload_books(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "P"}
    assert client.post("/teacher/books", json=body, headers=th).status_code == 405
    assert client.post("/teacher/book-drafts/front-pages", files={"file": FAKE_PDF}, headers=th).status_code in (404, 405)
    ids = f"{uuid.uuid4()}/chapters/{uuid.uuid4()}"
    assert client.post(f"/teacher/books/{ids}/pages/upload", files={"file": FAKE_PDF}, headers=th).status_code in (404, 405)
    assert client.post(f"/teacher/rooms/{uuid.uuid4()}/books/{uuid.uuid4()}/link", headers=th).status_code in (404, 405)  # bulk link is gone
    assert client.post("/student/book-drafts/front-pages", files={"file": FAKE_PDF}, headers=th).status_code == 403


def test_teachers_only_ever_see_reference_books_through_the_book_api(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "studenta")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    ref_id = reference_book(session_factory)
    private = new_book(client, sh)

    assert {b["id"] for b in client.get("/teacher/books", headers=th).json()} == {ref_id}
    assert {b["id"] for b in client.get("/teacher/books?scope=all", headers=th).json()} == {ref_id}
    assert client.get(f"/teacher/books/{ref_id}", headers=th).json()["is_reference"] is True
    assert client.get(f"/teacher/books/{private['id']}", headers=th).status_code == 404  # not even a student in my room
    join_room_of(client, session_factory, th, sh)
    assert client.get(f"/teacher/books/{private['id']}", headers=th).status_code == 404  # still no content access
    assert client.get(f"/teacher/books/{private['id']}/chapters", headers=th).status_code in (404, 405)


def test_teacher_sees_only_titles_and_labels_of_a_room_students_books(client, session_factory):
    from tests.test_chapter_jobs import upload
    from tests.test_pipeline import _text_pdf

    s, sh = make_user(session_factory, Role.student, "studenta")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, sh, subject="Science")
    ch = new_chapter(client, sh, book["id"])
    assert upload(client, sh, book["id"], ch, _text_pdf("the secret private page text")).status_code == 202

    # not my student yet: indistinguishable from "no such student"
    assert client.get(f"/teacher/students/{s.id}/books", headers=th).status_code == 404
    join_room_of(client, session_factory, th, sh)
    res = client.get(f"/teacher/students/{s.id}/books", headers=th)
    assert res.status_code == 200, res.text
    [b] = res.json()
    assert b["id"] == book["id"] and b["subject"] == "Science"
    assert [c["title"] for c in b["chapters"]] == ["Ch 1"]
    assert {"concept_names", "item_labels"} <= set(b["chapters"][0])
    # Titles, concept names and item labels only. (The fake model names a concept after the page text, so the
    # concept list is allowed to mention it; what must never appear is a page, an image or a stored file.)
    assert set(b["chapters"][0]) == {"id", "title", "sequence_num", "status", "concept_names", "item_labels"}
    for forbidden in ("pages", "content_text", "image_url", "layout_data", "source_file", "front_pages_file", "fingerprint"):
        assert forbidden not in res.text

    # another teacher (no room with this student) sees nothing
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    assert client.get(f"/teacher/students/{s.id}/books", headers=other).status_code == 404
    # and a student cannot use the teacher view at all
    assert client.get(f"/teacher/students/{s.id}/books", headers=sh).status_code == 403


# ---- pages ---------------------------------------------------------------------------

def test_owner_reads_pages_without_linking_and_never_sees_fingerprints(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    ch = new_chapter(client, sh, book["id"])
    up = client.post(f"/student/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=sh)
    assert up.status_code == 202, up.text
    res = client.get(f"/student/books/{book['id']}/chapters/{ch}/pages", headers=sh)
    assert res.status_code == 200 and len(res.json()) == 1
    assert "fingerprint" not in res.json()[0]


def test_roles_are_separated_on_the_book_endpoints(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "student1")
    _, ph = make_user(session_factory, Role.parent, "parent1")
    assert client.get("/teacher/books", headers=sh).status_code == 403
    assert client.get("/student/library", headers=ph).status_code == 403
    assert client.post("/student/books", json={"board": "b", "class_name": "c", "subject": "s", "publisher": "p"}, headers=ph).status_code == 403
    assert client.delete(f"/student/books/{uuid.uuid4()}", headers=ph).status_code == 403
    assert client.post(f"/student/books/{uuid.uuid4()}/link", headers=ph).status_code == 403


def test_old_doubt_upload_and_verification_endpoints_stay_gone(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    assert client.post(f"/student/books/{uuid.uuid4()}/chapters/{uuid.uuid4()}/doubt-upload", files={"file": FAKE_PDF}, headers=sh).status_code == 404
    assert client.get("/teacher/pages/unverified", headers=th).status_code == 404
    assert client.post(f"/teacher/pages/{uuid.uuid4()}/verify", headers=th).status_code == 404
