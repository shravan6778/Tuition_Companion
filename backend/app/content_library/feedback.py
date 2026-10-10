"""Layer 5: remembering what teachers decided about variant suggestions (table `match_feedback`)."""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MatchFeedback


def record(db: Session, book_id: uuid.UUID, base_book_id: uuid.UUID, decision: str, evidence: dict | None = None) -> MatchFeedback:
    """One row per (book, base). A later decision replaces the earlier one; evidence is kept unless new evidence is given
    (so clearing a variant keeps what the suggestion had shown when it was confirmed). Commits nothing."""
    row = db.scalar(select(MatchFeedback).where(MatchFeedback.book_id == book_id, MatchFeedback.base_book_id == base_book_id))
    if row is None:
        row = MatchFeedback(book_id=book_id, base_book_id=base_book_id, decision=decision, evidence=evidence)
        db.add(row)
    else:
        row.decision = decision
        if evidence is not None:
            row.evidence = evidence
    db.flush()
    return row


def dismissed_ids(db: Session, book_id: uuid.UUID) -> set[uuid.UUID]:
    return set(db.scalars(select(MatchFeedback.base_book_id).where(
        MatchFeedback.book_id == book_id, MatchFeedback.decision == "dismissed")))
