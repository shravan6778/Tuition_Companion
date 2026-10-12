"""Label the pages of chapters processed before `pages.page_kind` existed (exercise / recap / content).

    python -m app.db.backfill_page_kind            # DRY RUN: prints what would change per chapter
    python -m app.db.backfill_page_kind --yes      # write it

No OCR and no LLM calls: it applies the same deterministic rules the pipeline uses (a page that STARTS with an
"Exercises" / "Summary" heading, and every page after a chapter-end summary in the last 40% of the chapter). Only
pages still labelled `content` are touched, so re-running is safe and a label the model gave is never overwritten.
Labels only decide how exercise assignments are scoped; they never change concepts or a chapter's status."""
import argparse
from collections import Counter

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Chapter, ChapterStatus, Page
from app.pipeline.concepts import SUMMARY_TAIL_FROM, heading_page_kind, looks_like_summary_page


def label_pages(pages: list[Page]) -> dict:
    """{page: new kind} for the pages that should stop being plain `content` (pages sorted by number)."""
    changes, summary_seen, total = {}, False, len(pages)
    for index, page in enumerate(pages):
        kind = "exercise" if summary_seen else heading_page_kind(page.content_text)
        if looks_like_summary_page(page.content_text) and index >= SUMMARY_TAIL_FROM * total:
            summary_seen = True
        if kind and page.page_kind == "content":
            changes[page] = kind
    return changes


def run(db_factory, yes: bool = False) -> list[str]:
    out, totals = [], Counter()
    with db_factory() as db:
        for chapter in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)):
            pages = list(db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)))
            changes = label_pages(pages)
            kinds = Counter(changes.values())
            totals.update(kinds)
            out.append(f"{chapter.title}: {len(pages)} pages, " + (", ".join(f"{n} {k}" for k, n in kinds.items()) or "nothing to label"))
            if yes:
                for page, kind in changes.items():
                    page.page_kind = kind
        if yes:
            db.commit()
        else:
            db.rollback()
    out.append(("labelled " if yes else "dry run, would label ") + (", ".join(f"{n} {k}" for k, n in totals.items()) or "nothing"))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true")
    print("\n".join(run(SessionLocal, parser.parse_args().yes)))
