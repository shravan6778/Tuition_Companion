import uuid
from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String, Boolean, ForeignKey, JSON, Text, Table, Uuid
from sqlalchemy.orm import relationship
from app.models.base import Base

# Association table for Student to Book linkage
student_book = Table(
    'student_book',
    Base.metadata,
    Column('student_id', Uuid, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('book_id', Uuid, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True)
)

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        # A book is EITHER platform-wide reference content (no owner) OR a private upload owned by one teacher.
        CheckConstraint(
            "(is_reference AND owner_teacher_id IS NULL) OR (NOT is_reference AND owner_teacher_id IS NOT NULL)",
            name="ck_book_reference_xor_owner",
        ),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    board = Column(String, index=True)  # e.g., CBSE, State Board
    class_name = Column(String, index=True)  # e.g., Class 9
    subject = Column(String, index=True)  # e.g., Science
    publisher = Column(String, index=True)  # e.g., NCERT
    edition = Column(String, nullable=True)
    is_customized = Column(Boolean, default=False)
    school = Column(String, nullable=True)
    variant_of_id = Column(Uuid, ForeignKey("books.id"), nullable=True)
    is_reference = Column(Boolean, nullable=False, default=False, server_default="false", index=True)
    owner_teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.sequence_num")
    variants = relationship("Book", backref="base_book", remote_side=[id])
    students = relationship("User", secondary=student_book, back_populates="books")

class ChapterStatus:
    EMPTY = "empty"            # no file uploaded yet
    PROCESSING = "processing"  # OCR + concept extraction running in the background
    READY = "ready"            # pages + concepts saved; visible to students
    FAILED = "failed"          # last attempt failed; error_message says why; retry is possible
    ALL = (EMPTY, PROCESSING, READY, FAILED)


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
        CheckConstraint("status IN ('empty','processing','ready','failed')", name="ck_chapter_status"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, index=True)
    sequence_num = Column(Integer)
    status = Column(String(16), nullable=False, default=ChapterStatus.EMPTY, server_default=ChapterStatus.EMPTY)
    error_message = Column(Text, nullable=True)  # teacher-safe text, set when status == failed
    source_file = Column(String, nullable=True)  # stored upload (path relative to storage root); used for retry
    source_sha256 = Column(String(64), nullable=True)  # identical re-upload of a ready chapter is a no-op
    processing_started_at = Column(DateTime(timezone=True), nullable=True)

    book = relationship("Book", back_populates="chapters")
    pages = relationship("Page", back_populates="chapter", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer)
    content_text = Column(Text, nullable=False)
    layout_data = Column(JSON, nullable=True)  # Azure Document Intelligence layout data
    image_url = Column(String, nullable=True)
    verified = Column(Boolean, default=False)  # Teacher = verified, Student = unverified
    uploaded_by_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fingerprint = Column(String, nullable=True)  # MinHash signature

    chapter = relationship("Chapter", back_populates="pages")
    concepts = relationship("Concept", back_populates="page", cascade="all, delete-orphan")

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text)
    learning_objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)

    page = relationship("Page", back_populates="concepts")