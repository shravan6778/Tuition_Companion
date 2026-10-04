"""Background job: process one chapter's stored upload and record the outcome on the chapter."""
import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.errors import ProcessingError
from app.core.storage import read_file
from app.models.content import Chapter, ChapterStatus
from app.pipeline.orchestrator import PipelineOrchestrator

logger = logging.getLogger(__name__)

GENERIC_ERROR = "Something went wrong while processing this chapter. Please try again."


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def is_actively_processing(chapter: Chapter) -> bool:
    """True while a job is running. A 'processing' chapter older than the timeout is treated as stuck
    (e.g. the server restarted mid-job), so the teacher can re-upload or retry instead of waiting forever."""
    if chapter.status != ChapterStatus.PROCESSING:
        return False
    started = chapter.processing_started_at
    if started is None:
        return False
    if started.tzinfo is None:  # SQLite returns naive datetimes
        started = started.replace(tzinfo=timezone.utc)
    return utcnow() - started < timedelta(minutes=settings.chapter_processing_timeout_min)


def mark_processing(chapter: Chapter) -> None:
    chapter.status = ChapterStatus.PROCESSING
    chapter.error_message = None
    chapter.processing_started_at = utcnow()


def run_chapter_job(chapter_id: uuid.UUID, user_id: uuid.UUID, session_factory) -> None:
    """Runs after the HTTP response, with its OWN session (the request's session is closed by then).
    Pages and the 'ready' status are committed together, so a failure never leaves half a chapter."""
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.PROCESSING or not chapter.source_file:
            return
        ext = chapter.source_file.rsplit(".", 1)[-1]
        try:
            data = read_file(chapter.source_file)
            PipelineOrchestrator(db).process_chapter_file(chapter, data, ext, user_id)
            chapter.status = ChapterStatus.READY
            chapter.error_message = None
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.exception("Chapter %s processing failed", chapter_id)
            # Only ProcessingError text is written for humans; anything else could leak internals.
            message = str(exc) if isinstance(exc, ProcessingError) else GENERIC_ERROR
            chapter = db.get(Chapter, chapter_id)
            chapter.status = ChapterStatus.FAILED
            chapter.error_message = message[:500]
            db.commit()
    finally:
        db.close()
