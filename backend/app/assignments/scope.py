"""Which concepts does an assignment cover? Everything in Phase 3 (the Doubt button's search scope, the size of
the comprehension check, the weak-area flags) starts from this list, so it is decided here, once, deterministically.

  concept  -> that concept
  chapter  -> the chapter's canonical concepts
  subject  -> canonical concepts of every READY chapter of the student's linked books for that subject
  exercise -> exercise pages carry no concepts of their own (Phase 2 drops them on purpose), so the concepts whose
              stored vectors are closest to the exercise pages' vectors are PROPOSED. No model or embedding call:
              both vectors already sit in `content_embeddings`. The teacher sees and edits the list when assigning.
"""
import uuid
from dataclasses import dataclass, field

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, Concept, ContentEmbedding, Page, PageKind


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
