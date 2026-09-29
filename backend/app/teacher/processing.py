import logging
import uuid

from sqlalchemy.orm import Session

from app.core import storage
from app.models import Chapter, ChapterExtraction, ChapterStatus
from app.ocr import get_ocr_provider

logger = logging.getLogger(__name__)


def process_chapter(session_factory, chapter_id: uuid.UUID) -> None:
    """Runs as a background task after upload or retry. Opens its own session because
    the request's session may already be closed by the time this runs."""
    with session_factory() as db:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status not in (ChapterStatus.uploaded, ChapterStatus.failed):
            return  # nothing to do, or a concurrent run already handled it

        chapter.status = ChapterStatus.processing
        chapter.error_message = None
        db.commit()

        try:
            text, page_count = _extract_with_cache(db, chapter)
        except Exception:
            logger.exception("OCR failed for chapter %s", chapter_id)
            chapter.status = ChapterStatus.failed
            chapter.error_message = "Couldn't process this file. Please re-upload it or try again."
            db.commit()
            return

        chapter.status = ChapterStatus.ready
        chapter.error_message = None
        db.commit()


def _extract_with_cache(db: Session, chapter: Chapter) -> tuple[str, int]:
    cached = db.get(ChapterExtraction, chapter.file_hash)
    if cached is not None:
        return cached.text, cached.page_count  # never re-run OCR on an already-processed file (Rules.md)

    data = storage.read_file(chapter.file_path)
    ext = chapter.file_path.rsplit(".", 1)[-1]
    result = get_ocr_provider().extract(data, ext)

    db.merge(
        ChapterExtraction(
            file_hash=chapter.file_hash, text=result.text, page_count=result.page_count, provider="ocr"
        )
    )
    db.commit()
    return result.text, result.page_count