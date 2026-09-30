import uuid
import pytest
from sqlalchemy import select
from app.models.content import Book, Chapter, Page, student_book
from app.models.user import User, Role


def test_book_crud_and_student_link(session_factory):
    with session_factory() as db:
        # 1. Create a Book
        book = Book(board="CBSE", class_name="Class 10", subject="Mathematics", publisher="NCERT")
        db.add(book)
        db.flush()

        # 2. Add Chapter
        chapter = Chapter(book_id=book.id, title="Real Numbers", sequence_num=1)
        db.add(chapter)
        db.flush()

        # 3. Create Student User
        student = User(
            supertokens_user_id=f"stu_{uuid.uuid4()}", 
            name="Test Student", 
            username=f"stu_{uuid.uuid4().hex[:8]}", 
            phone="1234567890", 
            role=Role.student
        )
        db.add(student)
        db.flush()

        # 4. Link Student to Book
        db.execute(student_book.insert().values(student_id=student.id, book_id=book.id))
        db.commit()

        # 5. Verify Linkage
        my_books = db.scalars(select(Book).join(student_book).where(student_book.c.student_id == student.id)).all()
        assert len(my_books) == 1
        assert my_books[0].id == book.id


def test_page_verification_flag(session_factory):
    """Teacher uploads are verified; student uploads are unverified until confirmed."""
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Physics", publisher="NCERT")
        db.add(book)
        db.flush()

        chapter = Chapter(book_id=book.id, title="Motion", sequence_num=1)
        db.add(chapter)
        db.flush()

        teacher = User(supertokens_user_id=f"tch_{uuid.uuid4()}", name="Teacher", username="t1", phone="111", role=Role.teacher)
        student = User(supertokens_user_id=f"stu_{uuid.uuid4()}", name="Student", username="s1", phone="222", role=Role.student)
        db.add_all([teacher, student])
        db.flush()

        teacher_page = Page(chapter_id=chapter.id, page_number=1, content_text="Velocity", verified=True, uploaded_by_id=teacher.id)
        student_page = Page(chapter_id=chapter.id, page_number=2, content_text="Doubt", verified=False, uploaded_by_id=student.id)
        
        db.add_all([teacher_page, student_page])
        db.commit()

        assert teacher_page.verified is True
        assert student_page.verified is False