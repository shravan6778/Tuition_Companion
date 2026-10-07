"""What a graph store must offer, plus the plain-data shapes it exchanges with the pipeline.

Rules every store follows:
  * PostgreSQL is the source of truth. A store only holds a rebuildable COPY, written per chapter and replaced
    as a whole (`replace_chapter`), so writing the same chapter twice gives the same result.
  * No page text goes into a store: only ids, page numbers, concept names/descriptions and vectors.
  * Every search takes `book_ids` and returns only nodes of those books. An empty list returns nothing, never
    "everything". The caller (the Tutor, in Phase 3) passes the books the student is linked to.
"""
from dataclasses import dataclass, field
from typing import Optional, Protocol, Sequence


class GraphStoreError(Exception):
    """The graph store failed or is unreachable. The message is for logs and the sync report, not for users."""


@dataclass
class PageNode:
    id: str
    page_number: int
    embedding: Optional[list[float]] = None


@dataclass
class ConceptNode:
    id: str
    name: str
    description: str
    position: int
    embedding: Optional[list[float]] = None


@dataclass
class EdgeRow:
    concept_id: str       # the concept that needs...
    prerequisite_id: str  # ...this one first
    source: str           # "page" | "llm"


@dataclass
class ChapterGraph:
    book_id: str
    chapter_id: str
    title: str
    sequence_num: int
    is_reference: bool
    owner_teacher_id: Optional[str]
    embedding_model: Optional[str]
    pages: list[PageNode] = field(default_factory=list)
    concepts: list[ConceptNode] = field(default_factory=list)  # canonical concepts only
    edges: list[EdgeRow] = field(default_factory=list)
    concept_pages: list[tuple[str, str]] = field(default_factory=list)  # (concept id, page id) it is explained on


@dataclass
class ConceptHit:
    concept_id: str
    name: str
    description: str
    chapter_id: str
    book_id: str
    similarity: float


@dataclass
class PageHit:
    page_id: str
    page_number: int
    chapter_id: str
    book_id: str
    similarity: float


@dataclass
class PrerequisiteRow:
    concept_id: str
    name: str
    depth: int  # 1 = direct prerequisite


class GraphStore(Protocol):
    def ensure_schema(self) -> None:
        """Create indexes (idempotent). Raises GraphStoreError if a vector index has a different dimension."""

    def replace_chapter(self, graph: ChapterGraph) -> None:
        """Delete everything stored for the chapter and write `graph`, atomically."""

    def delete_chapter(self, chapter_id: str) -> None: ...

    def list_chapter_ids(self) -> set[str]: ...

    def clear(self) -> None:
        """Remove everything this app wrote (used by a full rebuild)."""

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]: ...

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]: ...

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        """Everything the concept needs, nearest first (breadth of the prerequisite graph)."""

    def stats(self) -> dict: ...

    def close(self) -> None: ...
