"""Layer 4: embeddings as a SECOND similarity signal for 'this chapter looks like a chapter of a book I can see'.

The fingerprint (3-word shingles) is exact about reused text but blind when a book was re-typeset, lightly
reworded or re-scanned badly. Page embeddings catch similar meaning. This runs after the chapter is `ready`
and embedded, uses only the vectors PostgreSQL already holds (no embedding calls, no LLM), and only ever
adds SUGGESTIONS (`signal: "embedding"`) for books the fingerprint did not already suggest. It never reuses
concepts or sets anything by itself: the teacher still confirms `variant_of`.

Privacy: the same rule as the fingerprint suggestions. A teacher's chapter is compared with official books and
with that teacher's own other books only; an official chapter only with other official books. Nothing here
can name another teacher's book. The outcome is recorded in `chapter.match_report["embedding_match"]`."""
import logging
from collections import defaultdict

import numpy as np
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, ContentEmbedding

logger = logging.getLogger(__name__)
MAX_SUGGESTIONS = 3


def _usable(row: ContentEmbedding) -> bool:
    from app.pipeline.indexing import _usable as usable  # no placeholder / odd-size vectors, same rule as the graph copy
    return usable(row)


def _unit(row: ContentEmbedding) -> np.ndarray:
    vec = np.asarray(from_bytes(row.vector), dtype=float)
    return vec / (np.linalg.norm(vec) or 1.0)


def compute(db: Session, chapter: Chapter) -> tuple[list[dict], dict]:
    """(suggestions, info). `info` has the status and, for tuning, the closest books even below the threshold."""
    mine = [r for r in db.scalars(select(ContentEmbedding).where(
        ContentEmbedding.chapter_id == chapter.id, ContentEmbedding.page_id.is_not(None))) if _usable(r)]
    if not mine:
        return [], {"status": "no_vectors"}
    book = db.get(Book, chapter.book_id)
    visible = Book.is_reference.is_(True)
    if book.owner_teacher_id is not None:
        visible = or_(visible, and_(Book.is_reference.is_(False), Book.owner_teacher_id == book.owner_teacher_id))
    rows = db.execute(
        select(ContentEmbedding, Chapter, Book)
        .join(Chapter, Chapter.id == ContentEmbedding.chapter_id).join(Book, Book.id == Chapter.book_id)
        .where(ContentEmbedding.page_id.is_not(None), Chapter.status == ChapterStatus.READY, Book.id != book.id, visible)
    ).all()
    model = mine[0].model
    others = [(e, ch, b) for e, ch, b in rows if e.model == model and _usable(e)]
    if not others:
        return [], {"status": "no_candidates", "pages_compared": len(mine)}
    if len(others) > settings.embed_match_max_pages:
        return [], {"status": "skipped_too_many_pages"}

    matrix = np.vstack([_unit(e) for e, _, _ in others])
    per_book: dict = defaultdict(list)  # book id -> [(similarity, chapter)] for each of my pages that matched it
    for row in mine:
        sims = matrix @ _unit(row)
        best: dict = {}
        for i in np.argsort(-sims)[: 50]:
            b = others[i][2]
            if sims[i] >= settings.embed_match_similarity and b.id not in best:
                best[b.id] = (float(sims[i]), others[i][1])
        for bid, hit in best.items():
            per_book[bid].append(hit)

    books = {str(b.id): b for _, _, b in others}
    scored = []
    for bid, hits in per_book.items():
        chapters: dict = defaultdict(lambda: [0, None])
        for _, ch in hits:
            chapters[ch.id][0] += 1
            chapters[ch.id][1] = ch.title
        top_id, (_, top_title) = max(chapters.items(), key=lambda kv: kv[1][0])
        scored.append({
            "book_id": str(bid), "chapter_id": str(top_id), "chapter_title": top_title, "kind": "variant",
            "matched_pages": len(hits), "pages_checked": len(mine),
            "avg_similarity": round(sum(s for s, _ in hits) / len(hits), 3), "signal": "embedding",
        })
    scored.sort(key=lambda s: (s["matched_pages"], s["avg_similarity"]), reverse=True)
    suggestions = [s for s in scored if s["matched_pages"] / len(mine) >= settings.variant_min_coverage]
    closest = [
        {"book": " ".join(str(x) for x in (books[s["book_id"]].publisher, books[s["book_id"]].subject, books[s["book_id"]].class_name)),
         "chapter": s["chapter_title"], "matched_pages": s["matched_pages"], "pages_checked": len(mine),
         "avg_similarity": s["avg_similarity"]}
        for s in scored[:3]
    ]
    return suggestions, {"status": "done", "model": model, "pages_compared": len(mine), "closest": closest}


def embedmatch_chapter(db: Session, chapter: Chapter) -> dict:
    """Recomputes this chapter's embedding suggestions and merges them into `match_report`. Commits nothing.
    Fingerprint suggestions stay first and untouched; an embedding one is added only for a book the
    fingerprint did not already suggest, and only while there is room (at most 3 in all)."""
    report = dict(chapter.match_report or {})
    if not settings.embed_match_enabled:
        return {"status": "disabled"}
    found, info = compute(db, chapter)
    base = [s for s in (report.get("suggestions") or []) if s.get("signal") != "embedding"]
    known = {s["book_id"] for s in base}
    extra = [s for s in found if s["book_id"] not in known][: max(0, MAX_SUGGESTIONS - len(base))]
    stored = {k: v for k, v in info.items() if k != "closest"}
    stored["added"] = len(extra)
    chapter.match_report = {**report, "suggestions": base + extra, "embedding_match": stored}
    db.flush()
    return {**info, "added": len(extra)}


def embedmatch_after(session_factory, chapter_id) -> str:
    """After a chapter is ready and embedded. NEVER raises. Returns a one-line outcome for logs."""
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY or not settings.embed_match_enabled:
            return "skipped"
        rep = embedmatch_chapter(db, chapter)
        db.commit()
        return f"{rep.get('status')} (+{rep.get('added', 0)} suggestions)"
    except Exception:
        db.rollback()
        logger.exception("Embedding match crashed for chapter %s", chapter_id)
        return "failed"
    finally:
        db.close()
