"""Find known pages similar to a new page, and turn page matches into book-level suggestions.

Thresholds (settings): >= reuse_similarity is the same page (reuse its concepts, no LLM call);
variant_min_similarity..reuse_similarity is a page from a variant/edition of a known book.

Privacy: concept reuse may use any book's page (the uploader already holds near-identical text, so nothing
new is revealed). Book SUGGESTIONS are limited to books the uploading teacher can already see."""
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Book, Chapter, Page, PageBand
from app.pipeline.fingerprint import compute_jaccard_similarity

MAX_CANDIDATES = 30


@dataclass
class PageMatch:
    page_id: uuid.UUID
    score: float
    book_id: uuid.UUID
    is_reference: bool
    owner_teacher_id: Optional[uuid.UUID]


def find_matches(db: Session, signature: bytes, keys: Iterable[int]) -> list[PageMatch]:
    """Pages with similarity >= variant_min_similarity, best first. Looks up the LSH keys, then scores only
    the few candidates that share one, never the whole table."""
    shared = db.execute(
        select(PageBand.page_id, func.count().label("shared"))
        .where(PageBand.key.in_(list(keys)))
        .group_by(PageBand.page_id)
        .order_by(func.count().desc())
        .limit(MAX_CANDIDATES)
    ).all()
    if not shared:
        return []
    rows = db.execute(
        select(Page.id, Page.fingerprint, Book.id, Book.is_reference, Book.owner_teacher_id)
        .join(Chapter, Chapter.id == Page.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(Page.id.in_([r.page_id for r in shared]))
    ).all()
    matches = []
    for page_id, fingerprint, book_id, is_reference, owner_id in rows:
        score = compute_jaccard_similarity(signature, fingerprint)
        if score >= settings.variant_min_similarity:
            matches.append(PageMatch(page_id, score, book_id, is_reference, owner_id))
    return sorted(matches, key=lambda m: m.score, reverse=True)


def summarize_book_matches(
    per_page: list[list[PageMatch]], pages_checked: int, own_book_id: uuid.UUID, teacher_id: uuid.UUID
) -> list[dict]:
    """Book-level suggestions for one chapter: books (visible to the teacher, other than this one) that at least
    variant_min_coverage of the chapter's fingerprinted pages match. kind='same' if the matched pages are
    near-identical, else 'variant'."""
    if pages_checked == 0:
        return []
    best: dict[uuid.UUID, list[float]] = defaultdict(list)  # book -> best score for each page that matched it
    for matches in per_page:
        page_best: dict[uuid.UUID, float] = {}
        for m in matches:
            visible = m.is_reference or m.owner_teacher_id == teacher_id
            if visible and m.book_id != own_book_id:
                page_best[m.book_id] = max(page_best.get(m.book_id, 0.0), m.score)
        for book_id, score in page_best.items():
            best[book_id].append(score)

    suggestions = []
    for book_id, scores in best.items():
        coverage = len(scores) / pages_checked
        if coverage < settings.variant_min_coverage:
            continue
        average = sum(scores) / len(scores)
        suggestions.append({
            "book_id": str(book_id),
            "kind": "same" if average >= settings.reuse_similarity else "variant",
            "matched_pages": len(scores),
            "pages_checked": pages_checked,
            "avg_similarity": round(average, 3),
        })
    suggestions.sort(key=lambda s: (s["matched_pages"], s["avg_similarity"]), reverse=True)
    return suggestions[:3]
