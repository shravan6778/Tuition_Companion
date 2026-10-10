import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.room import RoomType


# --- Auth & User Schemas ---
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    supertokens_user_id: str
    name: str
    username: str
    phone: str
    role: str
    link_code: Optional[str] = None
    created_at: datetime
    is_admin: bool = False  # may delete official books/chapters (see ADMIN_USERNAMES); only /auth/me fills it in


# --- Room Schemas ---
class RoomCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    room_type: RoomType = RoomType.single_class


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    teacher_id: uuid.UUID
    name: str
    room_type: RoomType
    join_code: str
    created_at: datetime
    member_count: int = 0


class JoinRoomIn(BaseModel):
    join_code: str = Field(min_length=6, max_length=12)


# Replace the current MemberOut schema with this:
class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID        # This is the User ID
    name: str            # This is the User name
    joined_at: datetime  # When they joined the room
    


class RoomBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str


# --- Parent Schemas ---
class LinkStudentIn(BaseModel):
    link_code: str = Field(min_length=4, max_length=12)


class ChildOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    rooms: list[RoomBrief] = []


# --- Book, Chapter, Page, Concept Schemas ---
class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    learning_objectives: Optional[list[str]] = None
    prerequisites: Optional[list[str]] = None  # raw names from the page-level extraction
    is_canonical: bool = True
    prerequisite_ids: list[uuid.UUID] = []  # resolved links (only canonical concepts have any)


class GraphNodeOut(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    pages: list[int]  # every page where this concept appears


class GraphEdgeOut(BaseModel):
    prerequisite_id: uuid.UUID  # learn this first...
    concept_id: uuid.UUID  # ...before this
    source: str  # "page" (name match) or "llm" (chapter linking pass)


class CrossChapterEdgeOut(BaseModel):
    concept_id: uuid.UUID  # in THIS chapter
    prerequisite_id: uuid.UUID  # in an earlier chapter of the same book
    prerequisite_name: str
    prerequisite_chapter_id: uuid.UUID
    prerequisite_chapter_title: Optional[str] = None
    similarity: Optional[float] = None


class ChapterGraphOut(BaseModel):
    chapter_id: uuid.UUID
    status: str
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]
    cross_chapter: list[CrossChapterEdgeOut] = []
    report: Optional[dict] = None


class ChapterMatchOut(BaseModel):
    """One of YOUR chapters matching a chapter of a book you can see."""
    book: "BookBrief"
    chapter_id: Optional[uuid.UUID] = None  # the matching chapter of that book
    chapter_title: Optional[str] = None
    kind: str  # "same" (near-identical pages) or "variant" (same content with edits)
    matched_pages: int
    pages_checked: int
    avg_similarity: float
    signal: str = "fingerprint"  # "fingerprint" (text overlap) or "embedding" (similar meaning; weaker evidence)


class ChapterMatchesOut(BaseModel):
    chapter_id: uuid.UUID
    chapter_title: str
    matches: list[ChapterMatchOut]


class VariantSuggestionOut(BaseModel):
    book: "BookBrief"
    kind: str  # "same" or "variant"
    coverage: float  # share of YOUR chapters that match a chapter of this book
    matched_chapters: int
    chapters_checked: int
    candidate_chapters_loaded: int  # how many finished chapters the suggested book has (official books fill up over time)
    avg_similarity: float
    matched_pages: int
    pages_checked: int
    signal: str = "pages"  # "pages" (text/meaning of the pages) or "structure" (same chapter titles in the same order; weaker evidence)


class BookBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_reference: bool = False


class VariantOfIn(BaseModel):
    base_book_id: uuid.UUID


class BookMetadataOut(BaseModel):
    board: Optional[str] = None
    class_name: Optional[str] = None
    subject: Optional[str] = None
    publisher: Optional[str] = None
    edition: Optional[str] = None
    is_customized: bool = False
    school: Optional[str] = None


class FrontPagesDraftOut(BaseModel):
    draft_id: uuid.UUID
    page_count: int
    metadata: BookMetadataOut  # what the system read; the teacher edits/confirms it
    matches: list["BookBrief"]  # known books (official first) that already match this metadata
    warning: Optional[str] = None  # set when nothing could be read from the pages, so the UI can say so


class ChapterRange(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    start_page: int = Field(ge=1)
    end_page: int = Field(ge=1)


class WholeBookPlanOut(BaseModel):
    draft_id: uuid.UUID
    page_count: int
    proposed_chapters: list[ChapterRange]  # from the PDF's bookmarks; empty if it has none


class WholeBookConfirmIn(BaseModel):
    draft_id: uuid.UUID
    chapters: list[ChapterRange]


class BulkLinkOut(BaseModel):
    linked: int
    already_linked: int
    total_students: int


class ChapterRequestCreate(BaseModel):
    chapter_hint: str = Field(min_length=3, max_length=200)
    chapter_id: Optional[uuid.UUID] = None


class ChapterRequestOut(BaseModel):
    id: uuid.UUID
    book: "BookBrief"
    chapter_hint: str
    chapter_id: Optional[uuid.UUID] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    student_name: Optional[str] = None  # only filled in for the teacher's view


class FulfillRequestIn(BaseModel):
    chapter_id: Optional[uuid.UUID] = None


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chapter_id: uuid.UUID
    page_number: int
    content_text: str
    needs_review: bool = False
    review_note: Optional[str] = None
    concepts: list[ConceptOut] = []


class ChapterCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    sequence_num: int = 1


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    book_id: uuid.UUID
    title: str
    sequence_num: int
    status: str = "empty"
    error_message: Optional[str] = None


class BookCreate(BaseModel):
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool = False
    school: Optional[str] = None
    variant_of_id: Optional[uuid.UUID] = None
    draft_id: Optional[uuid.UUID] = None  # front-pages draft this Book is created from (see /teacher/book-drafts)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    board: str
    class_name: str
    subject: str
    publisher: str
    edition: Optional[str] = None
    is_customized: bool
    school: Optional[str] = None
    variant_of_id: Optional[uuid.UUID] = None
    is_reference: bool = False
    metadata_source: str = "manual"
    chapters: list[ChapterOut] = []