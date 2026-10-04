"""Content tenancy: who can see/change/link which Book (Rules.md §2 + §4)."""
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
    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "Private Pub", **overrides}
    res = client.post("/teacher/books", json=body, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def new_chapter(client, headers, book_id) -> str:
    res = client.post(f"/teacher/books/{book_id}/chapters", json={"title": "Ch 1", "sequence_num": 1}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def join_room_of(client, session_factory, teacher_headers, student_headers):
    room = client.post("/teacher/rooms", json={"name": "Room A", "room_type": "single_class"}, headers=teacher_headers).json()
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=student_headers).status_code == 200


# ---- teacher side -----------------------------------------------------------

def test_created_book_is_owned_by_creator_and_never_reference(client, session_factory):
    a, ah = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, ah, publisher="NCERT")  # even labelled "NCERT", a teacher's book is private
    assert book["is_reference"] is False
    with session_factory() as db:
        assert db.get(Book, uuid.UUID(book["id"])).owner_teacher_id == a.id


def test_teacher_cannot_see_or_modify_another_teachers_book(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    book = new_book(client, ah)
    ch = new_chapter(client, ah, book["id"])

    assert book["id"] not in [b["id"] for b in client.get("/teacher/books", headers=bh).json()]
    assert client.get(f"/teacher/books/{book['id']}", headers=bh).status_code == 404
    assert client.get(f"/teacher/books/{book['id']}/chapters", headers=bh).status_code == 404
    assert client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=bh).status_code == 404
    assert client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "X", "sequence_num": 2}, headers=bh).status_code == 404
    res = client.post(f"/teacher/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=bh)
    assert res.status_code == 404
    # owner still works
    assert client.get(f"/teacher/books/{book['id']}", headers=ah).status_code == 200


def test_reference_books_are_visible_to_teachers_but_read_only(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    ref_id = reference_book(session_factory)

    assert ref_id in [b["id"] for b in client.get("/teacher/books", headers=ah).json()]
    assert client.get(f"/teacher/books/{ref_id}", headers=ah).json()["is_reference"] is True
    assert client.post(f"/teacher/books/{ref_id}/chapters", json={"title": "X", "sequence_num": 1}, headers=ah).status_code == 403
    res = client.post(f"/teacher/books/{ref_id}/chapters/{uuid.uuid4()}/pages/upload", files={"file": FAKE_PDF}, headers=ah)
    assert res.status_code == 403


def test_list_scope_filter(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    ref_id = reference_book(session_factory)
    mine = new_book(client, ah)
    new_book(client, bh)

    assert {b["id"] for b in client.get("/teacher/books?scope=mine", headers=ah).json()} == {mine["id"]}
    assert {b["id"] for b in client.get("/teacher/books?scope=reference", headers=ah).json()} == {ref_id}
    assert {b["id"] for b in client.get("/teacher/books", headers=ah).json()} == {mine["id"], ref_id}


def test_variant_of_must_point_at_a_visible_book(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    ref_id = reference_book(session_factory)
    a_book = new_book(client, ah)

    body = {"board": "CBSE", "class_name": "Class 10", "subject": "Maths", "publisher": "P", "is_customized": True}
    assert client.post("/teacher/books", json={**body, "variant_of_id": a_book["id"]}, headers=bh).status_code == 404
    assert client.post("/teacher/books", json={**body, "variant_of_id": ref_id}, headers=bh).status_code == 201
    assert client.post("/teacher/books", json={**body, "variant_of_id": a_book["id"]}, headers=ah).status_code == 201


# ---- student side -----------------------------------------------------------

def test_student_can_only_link_reference_or_own_teachers_books(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    ref_id = reference_book(session_factory)
    a_book, b_book = new_book(client, ah), new_book(client, bh)

    # not in any room yet: reference only
    assert {b["id"] for b in client.get("/student/library", headers=sh).json()} == {ref_id}
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).status_code == 404
    assert client.get(f"/student/books/{a_book['id']}", headers=sh).status_code == 404

    join_room_of(client, session_factory, ah, sh)

    assert {b["id"] for b in client.get("/student/library", headers=sh).json()} == {ref_id, a_book["id"]}
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).json()["status"] == "linked"
    assert client.post(f"/student/books/{a_book['id']}/link", headers=sh).json()["status"] == "already_linked"
    assert client.post(f"/student/books/{ref_id}/link", headers=sh).status_code == 200
    assert client.post(f"/student/books/{b_book['id']}/link", headers=sh).status_code == 404  # other teacher's book

    assert client.get("/student/library", headers=sh).json() == []  # everything visible is now linked
    assert {b["id"] for b in client.get("/student/books", headers=sh).json()} == {a_book["id"], ref_id}


def test_student_reads_pages_only_of_linked_books_and_never_sees_fingerprints(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    book = new_book(client, ah)
    ch = new_chapter(client, ah, book["id"])
    up = client.post(f"/teacher/books/{book['id']}/chapters/{ch}/pages/upload", files={"file": FAKE_PDF}, headers=ah)
    assert up.status_code == 202, up.text
    teacher_pages = client.get(f"/teacher/books/{book['id']}/chapters/{ch}/pages", headers=ah).json()
    assert teacher_pages and "fingerprint" not in teacher_pages[0]

    join_room_of(client, session_factory, ah, sh)
    url = f"/student/books/{book['id']}/chapters/{ch}/pages"
    assert client.get(url, headers=sh).status_code == 404  # in the room, but hasn't linked the book

    client.post(f"/student/books/{book['id']}/link", headers=sh)
    res = client.get(url, headers=sh)
    assert res.status_code == 200 and len(res.json()) == 1
    assert "fingerprint" not in res.json()[0]

    client.delete(f"/student/books/{book['id']}/link", headers=sh)
    assert client.get(url, headers=sh).status_code == 404  # unlink revokes access


def test_student_cannot_use_teacher_book_endpoints_and_parent_cannot_use_either(client, session_factory):
    _, sh = make_user(session_factory, Role.student, "student1")
    _, ph = make_user(session_factory, Role.parent, "parent1")
    assert client.get("/teacher/books", headers=sh).status_code == 403
    assert client.post("/teacher/books", json={"board": "b", "class_name": "c", "subject": "s", "publisher": "p"}, headers=sh).status_code == 403
    assert client.get("/student/library", headers=ph).status_code == 403
    assert client.post(f"/student/books/{uuid.uuid4()}/link", headers=ph).status_code == 403


def test_student_upload_and_verification_endpoints_are_gone(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    assert client.post(f"/student/books/{uuid.uuid4()}/chapters/{uuid.uuid4()}/doubt-upload", files={"file": FAKE_PDF}, headers=sh).status_code == 404
    assert client.get("/teacher/pages/unverified", headers=th).status_code == 404
    assert client.post(f"/teacher/pages/{uuid.uuid4()}/verify", headers=th).status_code == 404
