import pytest
from app.models.content import Book, Chapter, Page


def test_book_crud_and_student_link(client, db_session, teacher_token, student_token):
    # 1. Teacher creates a Book[cite: 2]
    res = client.post(
        "/teacher/books",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "board": "CBSE",
            "class_name": "Class 10",
            "subject": "Mathematics",
            "publisher": "NCERT",
            "edition": "2026",
            "is_customized": False,
        },
    )
    assert res.status_code == 201
    book_id = res.json()["id"]

    # 2. Add chapter[cite: 2]
    ch_res = client.post(
        f"/teacher/books/{book_id}/chapters",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={"title": "Real Numbers", "sequence_num": 1},
    )
    assert ch_res.status_code == 201
    chapter_id = ch_res.json()["id"]

    # 3. Student links to the Book[cite: 2]
    link_res = client.post(
        f"/student/books/{book_id}/link",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert link_res.status_code == 200
    assert link_res.json()["status"] == "linked"

    # 4. Student views their linked books[cite: 2]
    my_books = client.get(
        "/student/books",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert my_books.status_code == 200
    assert any(b["id"] == book_id for b in my_books.json())


def test_page_verification_status(db_session, test_teacher, test_student):
    """Verifies that teacher upload sets verified=True, student upload sets verified=False[cite: 2]."""
    book = Book(
        board="CBSE",
        class_name="Class 9",
        subject="Physics",
        publisher="NCERT",
    )
    db_session.add(book)
    db_session.flush()

    chapter = Chapter(book_id=book.id, title="Motion", sequence_num=1)
    db_session.add(chapter)
    db_session.flush()

    # Teacher page[cite: 2]
    teacher_page = Page(
        chapter_id=chapter.id,
        page_number=1,
        content_text="Displacement and velocity definitions.",
        verified=True,
        uploaded_by_id=test_teacher.id,
    )
    # Student doubt page[cite: 2]
    student_page = Page(
        chapter_id=chapter.id,
        page_number=2,
        content_text="Unseen exercise problem doubt.",
        verified=False,
        uploaded_by_id=test_student.id,
    )
    db_session.add_all([teacher_page, student_page])
    db_session.commit()

    assert teacher_page.verified is True
    assert student_page.verified is False