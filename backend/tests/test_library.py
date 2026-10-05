import uuid
import pytest
from sqlalchemy import select
from app.models.content import Book, Chapter, Page, student_book
from app.models.user import User, Role


def test_book_crud_and_student_link(session_factory):
    with session_factory() as db:
        # 1. Create a Book
        book = Book(board="CBSE", class_name="Class 10", subject="Mathematics", publisher="NCERT", is_reference=True)
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
