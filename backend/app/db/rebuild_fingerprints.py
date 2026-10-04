"""Recompute every page's fingerprint + LSH index from its stored text.

    python -m app.db.rebuild_fingerprints

Run once after the migration that introduced shingle fingerprints (it clears the old ones), and any time
the fingerprint settings change. No OCR or LLM calls."""
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.content import Page, PageBand
from app.pipeline.fingerprint import apply_fingerprint


def rebuild(db) -> int:
    db.execute(delete(PageBand))
    count = 0
    for page in db.scalars(select(Page)).all():
        if apply_fingerprint(page, page.content_text):
            count += 1
    db.commit()
    return count


if __name__ == "__main__":
    with SessionLocal() as session:
        print(f"Fingerprinted {rebuild(session)} page(s).")
