"""Which concepts does an assignment cover? Everything in Phase 3 (the Doubt button's search scope, the size of
the comprehension check, the weak-area flags) starts from this list, so it is decided here, once, deterministically.

  concept  -> that concept
  chapter  -> the chapter's canonical concepts
  subject  -> canonical concepts of every READY chapter of the student's linked books for that subject
  items    -> the picked examples / exercise questions / figures are looked up in the student's own copy by kind + label.
              Their scope is those items, the pages they sit on, and the concepts they test (the ticked concepts, the
              concepts the items are linked to, or, for an item linked to none, the concepts explained on its page).
  exercise -> (legacy) exercise pages carry no concepts of their own (Phase 2 drops them on purpose), so the concepts whose
              stored vectors are closest to the exercise pages' vectors are PROPOSED. No model or embedding call:
              both vectors already sit in `content_embeddings`. The teacher sees and edits the list when assigning.
"""
import re
import unicodedata
import uuid
from dataclasses import dataclass, field

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, Concept, ContentEmbedding, Page, PageItem, PageItemConcept, PageKind
from app.pipeline.graph import loose_key


def chapter_concepts(db: Session, chapter_id: uuid.UUID) -> list[Concept]:
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter_id, Concept.is_canonical.is_(True))
        .order_by(Page.page_number, Concept.position)
    ))


def subject_concepts(db: Session, book_ids: list[uuid.UUID], subject: str) -> list[Concept]:
    """`book_ids` = the books the student has linked (the caller decides who may see what)."""
    if not book_ids:
        return []
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(Book.id.in_(book_ids), Book.subject.ilike(subject), Chapter.status == ChapterStatus.READY,
               Concept.is_canonical.is_(True))
        .order_by(Book.id, Chapter.sequence_num, Page.page_number, Concept.position)
    ))


@dataclass
class ProposedConcept:
    concept_id: uuid.UUID
    name: str
    similarity: float  # best cosine over the exercise pages
    pages: list[int] = field(default_factory=list)  # exercise page numbers that pointed at it


@dataclass
class ExerciseMapping:
    status: str  # "ok" | "no_exercise_pages" | "no_vectors"
    exercise_pages: list[int] = field(default_factory=list)
    per_page: dict[int, list[tuple[str, float]]] = field(default_factory=dict)  # page number -> [(concept name, similarity)] top candidates, whether kept or not
    proposed: list[ProposedConcept] = field(default_factory=list)


def propose_exercise_concepts(db: Session, chapter: Chapter, page_numbers: list[int] | None = None,
                              top_k: int | None = None, min_similarity: float | None = None,
                              max_concepts: int | None = None) -> ExerciseMapping:
    """Concepts an exercise practises. `page_numbers` = the pages the teacher picked (e.g. the pages of Ex.9.5);
    omitted = every page of the chapter labelled `exercise`. Only vectors from ONE embedding model are compared."""
    top_k = top_k or settings.exercise_map_top_k
    floor = settings.exercise_map_min_similarity if min_similarity is None else min_similarity
    cap = max_concepts or settings.exercise_map_max_concepts

    query = select(Page).where(Page.chapter_id == chapter.id)
    query = query.where(Page.page_number.in_(page_numbers)) if page_numbers else query.where(Page.page_kind == PageKind.EXERCISE)
    pages = list(db.scalars(query.order_by(Page.page_number)))
    if not pages:
        return ExerciseMapping("no_exercise_pages")

    page_vectors = {e.page_id: e for e in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.page_id.in_([p.id for p in pages])))}
    concepts = chapter_concepts(db, chapter.id)
    concept_vectors = {e.concept_id: e for e in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.concept_id.is_not(None)))}
    if not page_vectors or not concept_vectors:
        return ExerciseMapping("no_vectors", [p.page_number for p in pages])

    model = next(iter(page_vectors.values())).model
    usable = [c for c in concepts if c.id in concept_vectors and concept_vectors[c.id].model == model]
    if not usable:
        return ExerciseMapping("no_vectors", [p.page_number for p in pages])
    matrix = np.vstack([_unit(from_bytes(concept_vectors[c.id].vector)) for c in usable])

    result = ExerciseMapping("ok", [p.page_number for p in pages])
    best: dict[uuid.UUID, ProposedConcept] = {}
    for page in pages:
        embedding = page_vectors.get(page.id)
        if embedding is None or embedding.model != model:
            continue  # a page too short to be embedded (a stray heading) says nothing
        sims = matrix @ _unit(from_bytes(embedding.vector))
        order = np.argsort(-sims)[:top_k]
        result.per_page[page.page_number] = [(usable[i].name, round(float(sims[i]), 3)) for i in order]
        for i in order:
            if sims[i] < floor:
                continue
            concept = usable[i]
            entry = best.setdefault(concept.id, ProposedConcept(concept.id, concept.name, float(sims[i])))
            entry.similarity = max(entry.similarity, float(sims[i]))
            entry.pages.append(page.page_number)
    result.proposed = sorted(best.values(), key=lambda c: -c.similarity)[:cap]
    return result


def _unit(vector) -> np.ndarray:
    v = np.asarray(vector, dtype=float)
    return v / (np.linalg.norm(v) or 1.0)


# ---- items level ------------------------------------------------------------------------------------------------


def item_key(label: str) -> str:
    """Order-preserving key of an item label, so "Fig. 9.5", "Figure 9.5" and "fig 9.5" are one item while "Ex 5.9 Q4"
    and "Ex 9.5 Q4" stay two (the concept `loose_key` sorts its tokens, which would merge those)."""
    s = unicodedata.normalize("NFKC", label or "").casefold()
    s = re.sub(r"\bfigure\b", "fig", s)
    s = re.sub(r"\bexercises?\b", "ex", s)
    s = re.sub(r"\bexamples?\b", "example", s)
    s = re.sub(r"(?<=\d)\.(?=\d)", "_", s)  # keep the decimal point of 9.5
    return re.sub(r"[^\w]+", " ", s).strip().replace("_", ".")

@dataclass
class ResolvedItems:
    """What an `items` assignment means inside ONE student's copy of the chapter."""
    items: list[PageItem] = field(default_factory=list)
    concepts: list[Concept] = field(default_factory=list)  # canonical, book order
    page_ids: set[uuid.UUID] = field(default_factory=set)


def match_items(db: Session, chapter: Chapter, wanted) -> list[PageItem]:
    """The chapter's items that `wanted` (AssignmentItem rows or anything with kind / item_key / page_number) names.

    A label identifies an item inside a chapter, except where labels repeat ("Q1" in every exercise). The stored page
    number breaks that tie when this copy has the label on that page; if it does not (another edition paginates
    differently) every item with that label is kept, which errs towards covering the teacher's intent.
    """
    wanted = list(wanted)
    if not wanted:
        return []
    rows = db.execute(
        select(PageItem, Page.page_number).join(Page, Page.id == PageItem.page_id)
        .where(Page.chapter_id == chapter.id, PageItem.label.is_not(None))
        .order_by(Page.page_number, PageItem.position)
    ).all()
    by_key: dict[tuple[str, str], list[tuple[PageItem, int]]] = {}
    for item, number in rows:
        by_key.setdefault((item.kind, item_key(item.label)), []).append((item, number))
    chosen: dict[uuid.UUID, PageItem] = {}
    for w in wanted:
        candidates = by_key.get((w.kind, w.item_key), [])
        on_page = [c for c in candidates if w.page_number is not None and c[1] == w.page_number]
        for item, _ in (on_page or candidates):
            chosen.setdefault(item.id, item)
    return list(chosen.values())


def concepts_of_items(db: Session, chapter: Chapter, items: list[PageItem]) -> list[Concept]:
    """Canonical concepts the items test. An item linked to no concept falls back to the concepts explained on its page."""
    if not items:
        return []
    canonical = chapter_concepts(db, chapter.id)
    by_key = {c.name_key or loose_key(c.name): c for c in canonical}
    linked: dict[uuid.UUID, set[uuid.UUID]] = {}
    for item_id, concept_id in db.execute(select(PageItemConcept.item_id, PageItemConcept.concept_id)
                                          .where(PageItemConcept.item_id.in_([i.id for i in items]))):
        linked.setdefault(item_id, set()).add(concept_id)
    link_concepts = {c.id: c for c in db.scalars(select(Concept).where(Concept.id.in_({cid for s in linked.values() for cid in s})))} if linked else {}
    found: dict[uuid.UUID, Concept] = {}
    for item in items:
        ids = linked.get(item.id, set())
        picked = [link_concepts[i] for i in ids if i in link_concepts]
        if not picked:
            picked = [c for c in canonical if c.page_id == item.page_id]
        for c in picked:
            canon = c if c.is_canonical else by_key.get(c.name_key or loose_key(c.name))
            if canon is not None:
                found.setdefault(canon.id, canon)
    order = {c.id: n for n, c in enumerate(canonical)}
    return sorted(found.values(), key=lambda c: order.get(c.id, 10**6))


def resolve_items(db: Session, assignment, chapter: Chapter) -> ResolvedItems:
    """Items + concepts + pages of an `items` assignment in this student's chapter. Ticked concepts (stored by name on the
    assignment) are kept even when no picked item mentions them."""
    items = match_items(db, chapter, assignment.items)
    keys = {ac.concept_key for ac in assignment.concepts}
    ticked = [c for c in chapter_concepts(db, chapter.id) if loose_key(c.name) in keys]
    merged: dict[uuid.UUID, Concept] = {c.id: c for c in ticked}
    for c in concepts_of_items(db, chapter, items):
        merged.setdefault(c.id, c)
    order = {c.id: n for n, c in enumerate(chapter_concepts(db, chapter.id))}
    concepts = sorted(merged.values(), key=lambda c: order.get(c.id, 10**6))
    return ResolvedItems(items=items, concepts=concepts, page_ids={i.page_id for i in items})
