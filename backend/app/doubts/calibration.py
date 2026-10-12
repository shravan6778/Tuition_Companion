"""Measuring the "not in your book" cut-off instead of guessing it (same idea as pipeline/embedprobe.py for Layer 4).

Three groups of questions are run through the real retrieval path:
  in_book        a student-style doubt written by the model about a real page of the books (must be answered)
  off_topic      questions about things no school book here covers (must be refused)
  wrong_chapter  the same doubts, asked INSIDE the scope of a different chapter (must come back `outside_assignment`)
A cut-off is only trustworthy if it sits in the gap between `in_book` and `off_topic`."""
import json
import math
import re
import statistics
import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.doubts.retrieval import GROUNDED, OUTSIDE, Scope, retrieve
from app.models.content import Chapter, ChapterStatus, Concept, Page, PageKind
from app.pipeline.fingerprint import tokenize

OFF_TOPIC = [
    "Who won the cricket world cup last time?",
    "How do I install Python on my laptop?",
    "What is the capital of Australia?",
    "How do I make a cup of tea?",
    "Explain how GST is calculated on a restaurant bill",
    "Which phone should I buy for gaming?",
    "What is the plot of the movie Titanic?",
    "How do I improve my handwriting?",
    "What is the price of gold today?",
    "Tell me a joke about teachers",
]

SYSTEM = (
    "You are a school student reading one textbook page. Write ONE question you might ask your tutor about the main "
    "idea of this page, in your own everyday words, 8 to 25 words, as a confused student would. Do not copy any run of "
    "three or more words from the page. Reply with JSON only: {\"doubt\": \"<your question>\"}."
)


def write_doubt(llm, page_text: str) -> Optional[str]:
    try:
        raw = llm.complete_json(SYSTEM, "STUDENT DOUBT\nPAGE:\n" + page_text[: settings.concept_max_chars])
        doubt = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())).get("doubt")
        return doubt.strip() if isinstance(doubt, str) and doubt.strip() else None
    except Exception:
        return None


def percentile_low(values: list[float], share: float = 0.10) -> float:
    """Nearest-rank low percentile (the value 90% of the group is at or above)."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(share * len(ordered)) - 1)]


def summarize(in_book: list[float], off_topic: list[float], wrong_chapter: list[float], threshold: float) -> dict:
    """Pure function of the measured similarities (testable without any service)."""
    low_in, high_off = percentile_low(in_book), max(off_topic)
    separable = low_in > high_off
    return {
        "in_book_min": min(in_book), "in_book_p10": low_in, "in_book_median": statistics.median(in_book),
        "off_topic_max": high_off, "off_topic_median": statistics.median(off_topic),
        "wrong_chapter_scoped_max": max(wrong_chapter) if wrong_chapter else None,
        "threshold": threshold,
        "answered_in_book": sum(1 for s in in_book if s >= threshold) / len(in_book),
        "wrongly_answered_off_topic": sum(1 for s in off_topic if s >= threshold) / len(off_topic),
        "separable": separable,
        "recommended": round((low_in + high_off) / 2, 2) if separable else None,
        "pass": separable
                and sum(1 for s in in_book if s >= threshold) / len(in_book) >= 0.9
                and all(s < threshold for s in off_topic),
    }


def probe(db: Session, llm, embedder, store, book_ids: list[uuid.UUID], pages: int = 12) -> dict:
    chapters = list(db.scalars(select(Chapter).where(Chapter.book_id.in_(book_ids), Chapter.status == ChapterStatus.READY)
                               .order_by(Chapter.book_id, Chapter.sequence_num)))
    candidates = []
    for ch in chapters:
        for p in db.scalars(select(Page).where(Page.chapter_id == ch.id, Page.page_kind == PageKind.CONTENT).order_by(Page.page_number)):
            if len(tokenize(p.content_text)) >= settings.fingerprint_min_words and db.scalar(select(Concept.id).where(Concept.page_id == p.id).limit(1)):
                candidates.append((ch, p))
    if len(candidates) < 4 or len(chapters) < 1:
        return {"status": "not_enough_pages", "pages_available": len(candidates)}
    step = max(1, len(candidates) // pages)
    picked = candidates[::step][:pages]

    in_book, wrong, right_chapter, outside_hits = [], [], 0, 0
    for ch, page in picked:
        doubt = write_doubt(llm, page.content_text)
        if not doubt:
            continue
        r = retrieve(db, doubt, embedder=embedder, store=store, book_ids=book_ids, threshold=0.0)
        in_book.append(r.confidence)
        right_chapter += 1 if r.pages and r.pages[0].chapter_id == str(ch.id) else 0
        others = [c for c in chapters if c.id != ch.id]
        if others:
            scoped = retrieve(db, doubt, embedder=embedder, store=store, book_ids=book_ids,
                              scope=Scope(chapter_ids={str(others[0].id)}), threshold=settings.retrieval_min_similarity)
            wrong.append(scoped.confidence)
            outside_hits += 1 if scoped.status == OUTSIDE else 0
    off = [retrieve(db, q, embedder=embedder, store=store, book_ids=book_ids, threshold=0.0).confidence for q in OFF_TOPIC]
    if len(in_book) < 3:
        return {"status": "doubt_writing_failed", "written": len(in_book), "asked": len(picked)}
    summary = summarize(in_book, off, wrong, settings.retrieval_min_similarity)
    summary.update({
        "status": "done", "doubts": len(in_book), "right_chapter_top_hit": right_chapter / len(in_book),
        "wrong_chapter_outside": (outside_hits / len(wrong)) if wrong else None, "in_book_values": sorted(round(v, 3) for v in in_book),
        "off_topic_values": sorted(round(v, 3) for v in off),
    })
    return summary
