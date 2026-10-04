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


class ChapterGraphOut(BaseModel):
    chapter_id: uuid.UUID
    status: str
    nodes: list[GraphNodeOut]
    edges: list[GraphEdgeOut]
    report: Optional[dict] = None


class VariantSuggestionOut(BaseModel):
    book: "BookBrief"
    kind: str  # "same" (near-identical pages) or "variant" (an edition/customization of that book)
    coverage: float  # share of your uploaded pages that match it
    avg_similarity: float
    matched_pages: int
    pages_checked: int


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


class PageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chapter_id: uuid.UUID
    page_number: int
    content_text: str
    verified: bool
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
    chapters: list[ChapterOut] = []