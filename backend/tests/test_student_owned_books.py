"""Private student-owned books, step 1: the column, the XOR constraint and the owner-only access rule.

Upload routes, removal and the pipeline still work with teacher-owned books at this point; these tests only
cover what the new column and the new access rules guarantee."""
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.content_library import access
from app.models import Book, Role
from tests.test_book_access import join_room_of, make_user, new_book, reference_book


def student_book_row(session_factory, student, **overrides) -> str:
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Maths", publisher="Mine", is_reference=False,
                    owner_student_id=student.id, **overrides)
        db.add(book)
        db.commit()
        return str(book.id)


# ---- the XOR constraint ------------------------------------------------------

def test_a_book_may_be_reference_or_student_owned_or_still_teacher_owned(session_factory):
    _, _ = make_user(session_factory, Role.student, "student1")
    teacher, _ = make_user(session_factory, Role.teacher, "teachera")
    student, _ = make_user(session_factory, Role.student, "student2")
    with session_factory() as db:
        db.add_all([
            Book(subject="ref", is_reference=True),
            Book(subject="mine", is_reference=False, owner_student_id=student.id),
            Book(subject="legacy", is_reference=False, owner_teacher_id=teacher.id),  # transitional branch
        ])
        db.commit()


@pytest.mark.parametrize("owners", ["none", "both", "reference_with_student", "reference_with_teacher"])
def test_the_constraint_rejects_every_other_combination(session_factory, owners):
    teacher, _ = make_user(session_factory, Role.teacher, "teachera")
    student, _ = make_user(session_factory, Role.student, "student1")
    book = {
        "none": Book(subject="x", is_reference=False),
        "both": Book(subject="x", is_reference=False, owner_student_id=student.id, owner_teacher_id=teacher.id),
        "reference_with_student": Book(subject="x", is_reference=True, owner_student_id=student.id),
        "reference_with_teacher": Book(subject="x", is_reference=True, owner_teacher_id=teacher.id),
    }[owners]
    with session_factory() as db:
        db.add(book)
        with pytest.raises(IntegrityError):
            db.commit()


# ---- who sees a student's book -------------------------------------------------

def test_a_student_sees_reference_books_and_their_own_and_nobody_elses(session_factory):
    s1, _ = make_user(session_factory, Role.student, "student1")
    s2, _ = make_user(session_factory, Role.student, "student2")
    ref = reference_book(session_factory)
    mine, theirs = student_book_row(session_factory, s1), student_book_row(session_factory, s2)
    with session_factory() as db:
        assert {str(b.id) for b in db.scalars(access.student_visible_books(s1))} == {ref, mine}
        assert {str(b.id) for b in db.scalars(access.student_visible_books(s2))} == {ref, theirs}
        assert access.get_book_visible_to_student(db, s1, uuid.UUID(mine)).id == uuid.UUID(mine)
        with pytest.raises(HTTPException) as err:
            access.get_book_visible_to_student(db, s1, uuid.UUID(theirs))
        assert err.value.status_code == 404


def test_a_classmate_in_the_same_room_still_cannot_see_a_students_book(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    s1, h1 = make_user(session_factory, Role.student, "student1")
    s2, h2 = make_user(session_factory, Role.student, "student2")
    join_room_of(client, session_factory, th, h1)
    join_room_of(client, session_factory, th, h2)
    mine = student_book_row(session_factory, s1)

    assert mine in {b["id"] for b in client.get("/student/library", headers=h1).json()}
    assert mine not in {b["id"] for b in client.get("/student/library", headers=h2).json()}
    assert client.get(f"/student/books/{mine}", headers=h1).status_code == 200
    assert client.get(f"/student/books/{mine}", headers=h2).status_code == 404
    assert client.post(f"/student/books/{mine}/link", headers=h2).status_code == 404


def test_the_owner_can_link_their_own_book_and_nobody_else_can(client, session_factory):
    s1, h1 = make_user(session_factory, Role.student, "student1")
    _, h2 = make_user(session_factory, Role.student, "student2")
    mine = student_book_row(session_factory, s1)
    assert client.post(f"/student/books/{mine}/link", headers=h2).status_code == 404
    assert client.post(f"/student/books/{mine}/link", headers=h1).json()["status"] == "linked"
    assert mine in {b["id"] for b in client.get("/student/books", headers=h1).json()}
    assert client.get("/student/books", headers=h2).json() == []


def test_teachers_never_see_a_students_book_even_with_the_student_in_their_room(client, session_factory):
    teacher, th = make_user(session_factory, Role.teacher, "teachera")
    s1, h1 = make_user(session_factory, Role.student, "student1")
    join_room_of(client, session_factory, th, h1)
    mine = student_book_row(session_factory, s1)
    own = new_book(client, th)  # the teacher's own book is still there, as before

    listed = {b["id"] for b in client.get("/teacher/books", headers=th).json()}
    assert own["id"] in listed and mine not in listed
    assert client.get(f"/teacher/books/{mine}", headers=th).status_code == 404
    assert client.get(f"/teacher/books/{mine}/chapters", headers=th).status_code == 404
    with session_factory() as db:
        assert db.scalar(access.teacher_visible_books(teacher).where(Book.id == uuid.UUID(mine))) is None
        with pytest.raises(HTTPException) as err:
            access.get_book_visible_to_teacher(db, teacher, uuid.UUID(mine))
        assert err.value.status_code == 404


# ---- changing a student's book -------------------------------------------------

def test_only_the_owner_may_change_a_student_book(session_factory):
    s1, _ = make_user(session_factory, Role.student, "student1")
    s2, _ = make_user(session_factory, Role.student, "student2")
    ref = reference_book(session_factory)
    mine = student_book_row(session_factory, s1)
    with session_factory() as db:
        assert access.get_student_owned_book(db, s1, uuid.UUID(mine)).id == uuid.UUID(mine)
        for who, book_id, code in [(s2, mine, 404), (s1, ref, 403), (s1, uuid.uuid4(), 404)]:
            with pytest.raises(HTTPException) as err:
                access.get_student_owned_book(db, who, uuid.UUID(str(book_id)))
            assert err.value.status_code == code
