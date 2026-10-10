"""Layer 4 calibration on REAL data, without needing a second edition of a book.

For a sample of pages of the official books: (1) the real LLM rewords the page in different words, the real embedding
model embeds the rewording, and it is compared with the page's stored vector -> how similar 'the same content, other
words' really is; (2) the same page's vector is compared with pages of OTHER chapters -> how similar 'different
content, same subject' gets. A page-similarity threshold is only trustworthy if it sits between the two groups.
Reads PostgreSQL, makes LLM + embedding calls (about `pages` of each), writes nothing."""
import json
import re
import statistics

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.embeddings.vectors import from_bytes
from app.models.content import Book, Chapter, ChapterStatus, ContentEmbedding, Page
from app.pipeline.embedmatch import _usable

SYSTEM = (
    "You rewrite one textbook page. Reply with JSON only: {\"text\": \"<the rewritten page>\"}. Reword EVERY sentence "
    "in different words and a different sentence structure. Keep every fact, term, number and the same length. "
    "Do not copy any run of four or more words from the original."
)


def _unit(vec) -> np.ndarray:
    v = np.asarray(vec, dtype=float)
    return v / (np.linalg.norm(v) or 1.0)


def _words(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def kept_phrases(original: str, reworded: str) -> float:
    """Share of the original's 4-word runs that survive in the rewording (0 = fully reworded)."""
    def grams(text):
        w = _words(text)
        return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}
    a = grams(original)
    return len(a & grams(reworded)) / len(a) if a else 0.0


def reword(llm, text: str) -> str | None:
    try:
        raw = llm.complete_json(SYSTEM, "PAGE:\n" + text)
        out = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())).get("text")
        return out.strip()[: settings.embedding_max_chars] if isinstance(out, str) and out.strip() else None
    except Exception:
        return None


def probe(db: Session, llm, embedder, pages: int = 10) -> dict:
    from app.pipeline.indexing import page_text
    rows = db.execute(
        select(ContentEmbedding, Page, Chapter)
        .join(Page, Page.id == ContentEmbedding.page_id).join(Chapter, Chapter.id == ContentEmbedding.chapter_id)
        .join(Book, Book.id == Chapter.book_id)
        .where(ContentEmbedding.page_id.is_not(None), Chapter.status == ChapterStatus.READY, Book.is_reference.is_(True))
    ).all()
    usable = [(e, p, c) for e, p, c in rows
              if _usable(e) and e.model == embedder.model_name and e.dim == embedder.dim and page_text(p)]
    usable.sort(key=lambda t: (str(t[2].book_id), t[2].sequence_num, t[1].page_number))
    if len(usable) < 4:
        return {"status": "not_enough_pages", "pages_available": len(usable)}
    idx = sorted({int(i) for i in np.linspace(0, len(usable) - 1, min(pages, len(usable)))})
    matrix = np.vstack([_unit(from_bytes(e.vector)) for e, _, _ in usable])
    chapter_ids = [c.id for _, _, c in usable]
    several_chapters = len(set(chapter_ids)) > 1

    texts, picked, kept = [], [], []
    for i in idx:
        original = page_text(usable[i][1])
        new = reword(llm, original)
        if new:
            texts.append(new)
            picked.append(i)
            kept.append(kept_phrases(original, new))
    if len(texts) < 3:
        return {"status": "rewording_failed", "rewritten": len(texts), "asked": len(idx)}

    vectors = embedder.embed(texts)
    same = [float(matrix[i] @ _unit(v)) for i, v in zip(picked, vectors)]
    other = []
    for i in picked:
        sims = matrix @ matrix[i]
        mask = np.array([(cid != chapter_ids[i]) if several_chapters else (j != i) for j, cid in enumerate(chapter_ids)])
        other.append(float(sims[mask].max()))

    thr = settings.embed_match_similarity
    lo, hi = min(same), max(other)
    recall = sum(1 for s in same if s >= thr) / len(same)
    false_rate = sum(1 for s in other if s >= thr) / len(other)
    return {
        "status": "done", "pages": len(same), "several_chapters": several_chapters,
        "same_min": lo, "same_median": statistics.median(same), "other_max": hi, "other_median": statistics.median(other),
        "kept_phrases_median": statistics.median(kept), "threshold": thr, "recall": recall, "false_rate": false_rate,
        "separable": lo > hi, "recommended": round((lo + hi) / 2, 2) if lo > hi else None,
        "pass": recall >= 0.9 and false_rate == 0,
    }
