"""Background job: process one chapter's stored upload and record the outcome on the chapter."""
import logging
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.errors import ProcessingError
from app.content_library.link_requests import fulfill_requests_for_chapter
from app.core.storage import read_file
from app.models.content import Chapter, ChapterStatus, IndexStatus
from app.pipeline.crosslink import crosslink_after
from app.pipeline.embedmatch import embedmatch_after
from app.pipeline.indexing import index_chapter
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
    # The old pages (and their vectors) are replaced by this run, so the derived copies are out of date again.
    chapter.embedding_status = IndexStatus.PENDING
    chapter.graph_sync_status = IndexStatus.PENDING
    chapter.index_error = None


def run_chapter_job(chapter_id: uuid.UUID, user_id: uuid.UUID, session_factory, fresh: bool = False) -> None:
    """Runs after the HTTP response, with its OWN session (the request's session is closed by then).
    Pages and the 'ready' status are committed together, so a failure never leaves half a chapter."""
    db = session_factory()
    committed_ready = False
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.PROCESSING or not chapter.source_file:
            return
        ext = chapter.source_file.rsplit(".", 1)[-1]
        try:
            data = read_file(chapter.source_file)
            PipelineOrchestrator(db, reuse_concepts=not fresh).process_chapter_file(chapter, data, ext, user_id)
            chapter.status = ChapterStatus.READY
            chapter.error_message = None
            fulfill_requests_for_chapter(db, chapter)  # students who asked for this chapter get closure
            db.commit()
            committed_ready = True
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
    if committed_ready:
        # Embeddings + the graph-store copy come AFTER the commit and can never fail the chapter (see
        # pipeline/indexing.py). Their outcome is recorded on the chapter; sync_graph retries failures.
        index_chapter(session_factory, chapter_id)
        embedmatch_after(session_factory, chapter_id)  # Layer 4: needs the page vectors; never raises
        crosslink_after(session_factory, chapter_id)  # needs the vectors the line above just made; never raises
