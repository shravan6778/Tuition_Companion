"""Layer 3: the chapter-title sequence as a third way to say 'this book looks like an edition of that one'.

Pages can differ a lot between editions (re-typeset, reworded, bad scan) while the book keeps the same chapters
in the same order, often with slightly different titles ('Exploration and Entering' / 'Exploration: Entering the
World of Secondary Science'). So titles are compared by word overlap, and what counts is the longest run of
my chapters whose matches appear in the SAME ORDER in the other book. It needs no page text, so it also works
before a single chapter has been processed, and it only ever adds SUGGESTIONS (the teacher still confirms
`variant_of`). Exercise numbering, the other half of the original idea, is not used: it would need parsing page
text and is too fragile to trust.

Privacy: only official books and the teacher's own other books are compared, exactly like the page signals."""
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Book, Chapter, ChapterStatus

STOP = {"a", "an", "the", "of", "and", "in", "to", "for", "on", "with", "our", "its", "is", "are", "at", "by", "from", "chapter", "unit", "lesson"}


def title_words(title: str) -> frozenset:
    """Lower-case words without filler and numbering ('Chapter 2: ...' -> the title only)."""
    return frozenset(w for w in re.findall(r"[a-z0-9]+", (title or "").lower()) if w not in STOP and not w.isdigit())


def title_overlap(a: frozenset, b: frozenset) -> float:
    """Share of the SHORTER title's words that the other title has. Empty titles never match."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def ordered_matches(mine: list[str], other: list[str]) -> tuple[int, float]:
    """(how many of my chapters match chapters of `other` in the same order, their average overlap).
    Each of my chapters is paired with its best-matching title; the answer is the longest in-order run."""
    other_words = [title_words(t) for t in other]
    pairs: list[tuple[int, float]] = []  # per chapter of mine: (position in other, overlap) or (-1, 0)
    for title in mine:
        words = title_words(title)
        best = (-1, 0.0)
        for pos, ow in enumerate(other_words):
            score = title_overlap(words, ow)
            if score >= settings.structure_title_overlap and score > best[1]:
                best = (pos, score)
        pairs.append(best)
    # longest strictly increasing run of positions (small inputs, so the simple O(n^2) version)
    length = [0] * len(pairs)
    total = [0.0] * len(pairs)
    for i, (pos, score) in enumerate(pairs):
        if pos < 0:
            continue
        length[i], total[i] = 1, score
        for j in range(i):
            if pairs[j][0] >= 0 and pairs[j][0] < pos and length[j] + 1 > length[i]:
                length[i], total[i] = length[j] + 1, total[j] + score
    if not length or max(length) == 0:
        return 0, 0.0
    k = max(range(len(length)), key=lambda i: (length[i], total[i]))
    return length[k], total[k] / length[k]


def _titles(db: Session, book_id, ready_only: bool) -> list[str]:
    query = select(Chapter.title).where(Chapter.book_id == book_id).order_by(Chapter.sequence_num)
    if ready_only:
        query = query.where(Chapter.status == ChapterStatus.READY)
    return [t for (t,) in db.execute(query)]


def suggest(db: Session, book: Book, teacher_id, exclude=frozenset()) -> list[dict]:
    """Books (official, or the teacher's own) whose chapter titles follow the same order as `book`'s, best first.
    Needs >= structure_min_chapters in-order matches covering >= variant_min_coverage of this book's chapters.
    Only chapters that are already `ready` count on the OTHER side (an official book fills up over time)."""
    if not settings.structure_enabled:
        return []
    mine = _titles(db, book.id, ready_only=False)
    if len(mine) < settings.structure_min_chapters:
        return []
    candidates = db.scalars(select(Book).where(
        Book.id != book.id, (Book.is_reference.is_(True)) | (Book.owner_teacher_id == teacher_id)))
    found = []
    for other in candidates:
        if other.id in exclude:
            continue
        theirs = _titles(db, other.id, ready_only=True)
        matched, avg = ordered_matches(mine, theirs)
        if matched < settings.structure_min_chapters or matched / len(mine) < settings.variant_min_coverage:
            continue
        found.append({"book": other, "matched_chapters": matched, "chapters_checked": len(mine),
                      "coverage": round(matched / len(mine), 3), "avg_overlap": round(avg, 3),
                      "candidate_chapters_loaded": len(theirs)})
    return sorted(found, key=lambda h: (h["coverage"], h["avg_overlap"]), reverse=True)
