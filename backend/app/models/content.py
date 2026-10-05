import uuid
from datetime import datetime, timezone
from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, Integer, LargeBinary, String, Boolean, ForeignKey, JSON, Text, Table, UniqueConstraint, Uuid, true
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
    metadata_source = Column(String(12), nullable=False, default="manual", server_default="manual")  # "front_pages" | "manual"
    extracted_metadata = Column(JSON, nullable=True)  # what the system read from the front pages, before the teacher edited it
    front_pages_file = Column(String, nullable=True)

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
    graph_report = Column(JSON, nullable=True)  # summary of the last concept-linking pass (see pipeline/graph.py)
    match_report = Column(JSON, nullable=True)  # how this chapter matched known pages/books (see pipeline/matching.py)

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
    needs_review = Column(Boolean, nullable=False, default=False, server_default="false")  # pipeline doubts about this page
    review_note = Column(String(200), nullable=True)  # why (shown to the teacher)
    uploaded_by_id = Column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fingerprint = Column(LargeBinary, nullable=True)  # MinHash signature (512 bytes); None for very short pages

    chapter = relationship("Chapter", back_populates="pages")
    concepts = relationship("Concept", back_populates="page", cascade="all, delete-orphan")
    bands = relationship("PageBand", back_populates="page", cascade="all, delete-orphan")


class PageBand(Base):
    """LSH index: a page shares >= 1 band key with every page it is similar to, so matching looks up
    ~32 keys instead of comparing against every page in the database."""
    __tablename__ = "page_bands"

    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), primary_key=True)
    key = Column(BigInteger, primary_key=True, index=True)

    page = relationship("Page", back_populates="bands")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    page_id = Column(Uuid, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True)
    description = Column(Text)
    learning_objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)  # raw prerequisite NAMES as the page-level LLM wrote them
    position = Column(Integer, nullable=False, default=0, server_default="0")  # order within its page
    name_key = Column(String, index=True, nullable=True)  # normalized name; equal keys in a chapter = same concept
    is_canonical = Column(Boolean, nullable=False, default=True, server_default=true())  # first occurrence in chapter

    page = relationship("Page", back_populates="concepts")
    edges_in = relationship("ConceptEdge", foreign_keys="ConceptEdge.concept_id", back_populates="concept", cascade="all, delete-orphan")
    edges_out = relationship("ConceptEdge", foreign_keys="ConceptEdge.prerequisite_id", back_populates="prerequisite", cascade="all, delete-orphan")

    @property
    def prerequisite_ids(self) -> list[uuid.UUID]:
        return [e.prerequisite_id for e in self.edges_in]


class ConceptEdge(Base):
    """'prerequisite_id must be understood before concept_id'. Only canonical concepts of one chapter are
    linked, and the stored graph is always acyclic (pipeline/graph.py enforces that)."""
    __tablename__ = "concept_edges"
    __table_args__ = (
        UniqueConstraint("concept_id", "prerequisite_id", name="uq_concept_edge"),
        CheckConstraint("concept_id <> prerequisite_id", name="ck_concept_edge_not_self"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    prerequisite_id = Column(Uuid, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(8), nullable=False, default="page")  # "page" = name match, "llm" = chapter linking pass

    concept = relationship("Concept", foreign_keys=[concept_id], back_populates="edges_in")
    prerequisite = relationship("Concept", foreign_keys=[prerequisite_id], back_populates="edges_out")


class UploadDraft(Base):
    """A teacher's upload that waits for confirmation: front pages (-> new Book) or a whole-textbook PDF
    (-> chapter split). Nothing heavy runs until the teacher confirms."""
    __tablename__ = "upload_drafts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String(12), nullable=False)  # "front_pages" | "whole_book"
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    source_file = Column(String, nullable=False)
    source_sha256 = Column(String(64), nullable=False)
    page_count = Column(Integer, nullable=False, default=0)
    payload = Column(JSON, nullable=True)  # extracted metadata / proposed chapter split
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class ChapterRequest(Base):
    """A student asking their teacher to add a chapter that isn't in the teacher's uploaded book yet."""
    __tablename__ = "chapter_requests"
    __table_args__ = (
        CheckConstraint("status IN ('open','fulfilled','dismissed','cancelled')", name="ck_chapter_request_status"),
    )

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)  # the book's owner
    book_id = Column(Uuid, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Uuid, ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    chapter_hint = Column(String(200), nullable=False)
    status = Column(String(10), nullable=False, default="open", server_default="open")
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
