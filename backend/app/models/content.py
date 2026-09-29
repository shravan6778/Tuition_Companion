from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Text, Table, Uuid
from sqlalchemy.orm import relationship
from app.models.base import Base

# Association table for Student to Book linkage [source: 2]
student_book = Table(
    'student_book',
    Base.metadata,
    Column('student_id', Uuid, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('book_id', Integer, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)
)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    board = Column(String, index=True)  # e.g., CBSE, State Board [source: 2]
    class_name = Column(String, index=True)  # e.g., Class 9 [source: 2]
    subject = Column(String, index=True)  # e.g., Science [source: 2]
    publisher = Column(String, index=True)  # e.g., NCERT [source: 2]
    edition = Column(String, nullable=True)
    is_customized = Column(Boolean, default=False)  # [source: 2]
    school = Column(String, nullable=True)  # [source: 2]
    variant_of_id = Column(Integer, ForeignKey("books.id"), nullable=True)  # [source: 2]

    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    variants = relationship("Book", backref="base_book", remote_side=[id])
    students = relationship("User", secondary=student_book, back_populates="books")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, index=True)
    sequence_num = Column(Integer)

    book = relationship("Book", back_populates="chapters")
    pages = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer)
    content_text = Column(Text, nullable=False)
    layout_data = Column(JSON, nullable=True)  # Azure Document Intelligence layout data [source: 2]
    image_url = Column(String, nullable=True)
    verified = Column(Boolean, default=False)  # Teacher = verified, Student = unverified [source: 2]
    uploaded_by_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fingerprint = Column(String, nullable=True)  # MinHash signature [source: 2]

    chapter = relationship("Chapter", back_populates="pages")
    concepts = relationship("Concept", back_populates="page", cascade="all, delete-orphan")

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text)
    learning_objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)

    page = relationship("Page", back_populates="concepts")