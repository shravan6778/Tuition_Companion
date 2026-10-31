"""Retrieval for a doubt: the part of Phase 3 that decides WHAT the Tutor may answer from. It never writes an answer.

    doubt text -> vector -> graph-store search restricted to the student's linked books (never "everything")
               -> optional narrowing to the assignment's chapters / concepts
               -> the best pages (their text is read from PostgreSQL, the source of truth) and concepts
               -> prerequisites of the best concepts by walking the graph (the refresher)

`status` says what the caller may do:
  grounded            enough evidence inside the scope: the Tutor may answer from `pages` / `concepts`
  outside_assignment  nothing good inside the assignment, but the student's books do cover it: offer standalone "Ask a Doubt"
  not_in_book         nothing good anywhere in the linked books: "upload this chapter" (Rules.md §4: no ungrounded answer)
  unavailable         the embedding service or graph store failed: say "couldn't do this right now", never guess

Tenancy: the books are re-checked in PostgreSQL after the search (a page is returned only if its chapter is ready and
belongs to one of `book_ids`), so a wrong answer from the store can never leak another teacher's text."""
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings import EmbeddingError
from app.graph_store.base import ConceptHit, GraphStoreError, ItemHit, PageHit, PrerequisiteRow
from app.models.content import Chapter, ChapterStatus, Concept, Page

logger = logging.getLogger(__name__)

GROUNDED, OUTSIDE, NOT_IN_BOOK, UNAVAILABLE = "grounded", "outside_assignment", "not_in_book", "unavailable"


@dataclass
class Scope:
    """What an assignment covers. Chapter / subject level: `chapter_ids` only (a hit is inside if its chapter is). Concept
    or exercise level: also `concept_ids` and `page_ids` (the pages those concepts are explained on), which narrow it
    below the chapter, so a doubt about ANOTHER concept of the same chapter is `outside_assignment` too.
    Empty scope = nothing is inside it. Build one from concepts with `scope_for_concepts`."""
    chapter_ids: set[str] = field(default_factory=set)
    concept_ids: set[str] = field(default_factory=set)
    page_ids: set[str] = field(default_factory=set)

    def has_concept(self, concept_id: str, chapter_id: str) -> bool:
        return concept_id in self.concept_ids or (not self.concept_ids and chapter_id in self.chapter_ids)

    def has_page(self, page_id: str, chapter_id: str) -> bool:
        return page_id in self.page_ids if self.page_ids else chapter_id in self.chapter_ids


def scope_for_concepts(db: Session, concepts: Sequence[Concept]) -> Scope:
    """The scope of a concept- or exercise-level assignment: those concepts, the pages they are explained on (the page
    that holds them and any page of the same chapter where the same idea recurs), and their chapters."""
    scope = Scope()
    wanted: dict[uuid.UUID, set[str]] = {}
    for c in concepts:
        page = db.get(Page, c.page_id)
        scope.concept_ids.add(str(c.id))
        scope.chapter_ids.add(str(page.chapter_id))
        scope.page_ids.add(str(page.id))
        if c.name_key:
            wanted.setdefault(page.chapter_id, set()).add(c.name_key)
    for chapter_id, keys in wanted.items():  # the same idea repeated on a later page is explained there too
        rows = db.execute(select(Concept.page_id).join(Page, Page.id == Concept.page_id)
                          .where(Page.chapter_id == chapter_id, Concept.name_key.in_(keys))).all()
        scope.page_ids.update(str(r[0]) for r in rows)
    return scope


@dataclass
class RetrievedItem:
    item_id: str
    kind: str
    label: str | None
    text: str
    solution_text: str | None
    page_id: str
    page_number: int
    chapter_id: str
    chapter_title: str
    book_id: str
    similarity: float


class RetrievedPage:
    page_id: str
    page_number: int
    chapter_id: str
    chapter_title: str
    book_id: str
    similarity: float
    text: str


@dataclass
class RetrievalResult:
    status: str
    confidence: float = 0.0              # best similarity inside the scope (the whole books when there is no scope)
    elsewhere_confidence: float = 0.0    # best similarity anywhere in the linked books (what "outside_assignment" is judged on)
    threshold: float = 0.0
    pages: list[RetrievedPage] = field(default_factory=list)
    items: list[RetrievedItem] = field(default_factory=list)
    concepts: list[ConceptHit] = field(default_factory=list)
    prerequisites: list[PrerequisiteRow] = field(default_factory=list)  # refresher, nearest first, without the hits themselves
    elsewhere: list[ConceptHit] = field(default_factory=list)  # for outside_assignment: where the books do cover it


def retrieve(db: Session, text: str, *, embedder, store, book_ids: Sequence[uuid.UUID], scope: Optional[Scope] = None,
             threshold: Optional[float] = None, k: Optional[int] = None) -> RetrievalResult:
    threshold = settings.retrieval_min_similarity if threshold is None else threshold
    k = k or settings.retrieval_candidates
    result = RetrievalResult(NOT_IN_BOOK, threshold=threshold)
    ids = [str(b) for b in book_ids]
    if not ids or not (text or "").strip():
        return result  # no linked books (or nothing asked): never "search everything"
    if store is None or embedder is None:
        return RetrievalResult(UNAVAILABLE, threshold=threshold)

    try:
        vector = embedder.embed([text.strip()[: settings.embedding_max_chars]])[0]
        window = k * (settings.retrieval_scope_overfetch if scope else 1)
        concept_hits = store.search_concepts(vector, ids, k=window)
        page_hits = store.search_pages(vector, ids, k=window)
        item_hits = store.search_items(vector, ids, k=window) if hasattr(store, "search_items") else []
    except (EmbeddingError, GraphStoreError):
        logger.warning("Retrieval failed", exc_info=True)
        return RetrievalResult(UNAVAILABLE, threshold=threshold)

    result.elsewhere_confidence = max([h.similarity for h in concept_hits + page_hits + item_hits], default=0.0)
    if scope is not None:
        inside_concepts = [h for h in concept_hits if scope.has_concept(h.concept_id, h.chapter_id)]
        inside_pages = [h for h in page_hits if scope.has_page(h.page_id, h.chapter_id)]
        inside_items = [h for h in item_hits if scope.has_page(h.page_id, h.chapter_id)]
    else:
        inside_concepts, inside_pages, inside_items = concept_hits, page_hits, item_hits
    inside_concepts, inside_pages, inside_items = inside_concepts[:k], inside_pages[:k], inside_items[:k]
    result.confidence = max([h.similarity for h in inside_concepts + inside_pages + inside_items], default=0.0)

    if result.confidence >= threshold:
        result.status = GROUNDED
        result.concepts = [h for h in inside_concepts if h.similarity >= threshold]
        page_hits = [h for h in inside_pages if h.similarity >= threshold]
        # A short question often matches a concept strongly while no whole page scores above the cut-off (a page
        # embedding is diluted by everything else on it). The pages the best concepts are explained on are still the
        # right evidence, so they join the page hits (read from PostgreSQL, same scope and tenancy checks).
        page_hits += _concept_page_hits(db, result.concepts[:3], scope)
        result.items = _load_items(db, inside_items, set(ids))
        item_page_hits = [
            PageHit(i.page_id, i.page_number, i.chapter_id, i.book_id, i.similarity)
            for i in result.items[:3]
        ]
        result.pages = _load_pages(db, page_hits + item_page_hits, set(ids))
        result.prerequisites = _refresher(store, result.concepts, ids)
        if not result.pages and not result.concepts:  # the store named hits PostgreSQL does not stand behind
            result.status = NOT_IN_BOOK
    elif scope is not None and result.elsewhere_confidence >= threshold:
        result.status = OUTSIDE
        result.elsewhere = [h for h in concept_hits if h.similarity >= threshold][:3]
    return result


def _concept_page_hits(db: Session, concepts: Sequence[ConceptHit], scope: Optional[Scope]) -> list[PageHit]:
    """The pages the given concepts are explained on, carrying the concept's similarity. Only pages inside the scope."""
    if not concepts:
        return []
    sims = {uuid.UUID(c.concept_id): c.similarity for c in concepts}
    rows = db.execute(
        select(Concept.id, Page.id, Page.page_number, Page.chapter_id, Chapter.book_id)
        .join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id.in_(list(sims)))
    ).all()
    hits = []
    for concept_id, page_id, number, chapter_id, book_id in rows:
        if scope is None or scope.has_page(str(page_id), str(chapter_id)):
            hits.append(PageHit(str(page_id), number, str(chapter_id), str(book_id), sims[concept_id]))
    return hits


def _load_items(db: Session, hits: list[ItemHit], book_ids: set[str]) -> list[RetrievedItem]:
    if not hits:
        return []
    by_id = {uuid.UUID(h.item_id): h for h in hits}
    from app.models.content import PageItem
    rows = db.execute(
        select(PageItem, Page, Chapter)
        .join(Page, Page.id == PageItem.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(PageItem.id.in_(list(by_id)), Chapter.status == ChapterStatus.READY)
    ).all()
    out = [
        RetrievedItem(str(i.id), i.kind, i.label, i.text, i.solution_text, str(p.id), p.page_number,
                      str(c.id), c.title or "", str(c.book_id), by_id[i.id].similarity)
        for i, p, c in rows if str(c.book_id) in book_ids
    ]
    return sorted(out, key=lambda r: -r.similarity)


def _load_pages(db: Session, hits: list[PageHit], book_ids: set[str]) -> list[RetrievedPage]:
    """Page text comes from PostgreSQL, and only for ready chapters of the allowed books."""
    if not hits:
        return []
    by_id: dict[uuid.UUID, PageHit] = {}
    for h in hits:  # the same page may arrive as a page hit and as a concept's page: keep its best similarity
        key = uuid.UUID(h.page_id)
        if key not in by_id or h.similarity > by_id[key].similarity:
            by_id[key] = h
    rows = db.execute(
        select(Page, Chapter).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Page.id.in_(list(by_id)), Chapter.status == ChapterStatus.READY)
    ).all()
    loaded = [
        RetrievedPage(str(p.id), p.page_number, str(c.id), c.title or "", str(c.book_id), by_id[p.id].similarity, p.content_text)
        for p, c in rows if str(c.book_id) in book_ids
    ]
    return sorted(loaded, key=lambda r: -r.similarity)


def _refresher(store, concepts: list[ConceptHit], book_ids: list[str]) -> list[PrerequisiteRow]:
    """Prerequisites of the best 3 concepts, nearest first, each once, never a concept that is itself a hit."""
    hit_ids = {c.concept_id for c in concepts}
    seen: dict[str, PrerequisiteRow] = {}
    try:
        for hit in concepts[:3]:
            for row in store.prerequisites(hit.concept_id, book_ids, max_depth=settings.retrieval_prereq_depth):
                if row.concept_id not in hit_ids and (row.concept_id not in seen or row.depth < seen[row.concept_id].depth):
                    seen[row.concept_id] = row
    except GraphStoreError:
        logger.warning("Prerequisite lookup failed; answering without a refresher", exc_info=True)
    return sorted(seen.values(), key=lambda r: (r.depth, r.name))


def concepts_on_page(db: Session, page_id: uuid.UUID) -> list[Concept]:
    """For a photographed whole page: the concepts the student can pick from."""
    return list(db.scalars(select(Concept).where(Concept.page_id == page_id, Concept.is_canonical.is_(True)).order_by(Concept.position)))
