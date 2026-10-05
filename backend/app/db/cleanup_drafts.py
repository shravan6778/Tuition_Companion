"""Delete abandoned upload drafts (front pages / whole-book PDFs nobody confirmed) and their stored files.

    python -m app.db.cleanup_drafts            # drafts older than 7 days
    python -m app.db.cleanup_drafts --days 1

A stored file is removed only if nothing else still points at it (another draft, a chapter's source file,
or a book's front pages), because files are stored by content hash and can be shared."""
import argparse
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.storage import delete_file
from app.db.session import SessionLocal
from app.models import Book, Chapter, UploadDraft


def cleanup(db: Session, older_than_days: int = 7) -> tuple[int, int]:
    """Returns (drafts_deleted, files_deleted)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    old = db.scalars(select(UploadDraft).where(UploadDraft.created_at < cutoff)).all()
    paths = {d.source_file for d in old}
    for draft in old:
        db.delete(draft)
    db.flush()

    still_used = set(db.scalars(select(UploadDraft.source_file)).all())
    still_used |= {p for p in db.scalars(select(Chapter.source_file)).all() if p}
    still_used |= {p for p in db.scalars(select(Book.front_pages_file)).all() if p}
    removed = 0
    for path in paths - still_used:
        try:
            delete_file(path)
            removed += 1
        except OSError:
            pass  # already gone
    db.commit()
    return len(old), removed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    args = parser.parse_args()
    with SessionLocal() as session:
        drafts, files = cleanup(session, args.days)
    print(f"Removed {drafts} abandoned draft(s) and {files} stored file(s).")
