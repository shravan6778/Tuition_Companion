import logging

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.llm import get_llm_provider
from app.models.content import Chapter, ChapterStatus, Concept, ConceptEdge, Page
from app.ocr import get_ocr_provider
from app.pipeline.concepts import ConceptExtractionError, extract_page_concepts
from app.pipeline.fingerprint import apply_fingerprint, band_keys, compute_minhash
from app.pipeline.graph import build_chapter_graph
from app.pipeline.matching import PageMatch, find_matches, summarize_book_matches

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Synchronous on purpose: OCR and LLM clients block, and this runs in a background thread
    (see pipeline/jobs.py). Providers come from the factories, so tests and keyless dev use the
    fake ones (OCR_PROVIDER / LLM_PROVIDER=fake).

    Cost layers, cheapest first:
      0. identical FILE already processed anywhere -> skip OCR (reuse its page text)
      1. identical/near-identical PAGE already known (>= reuse_similarity) -> reuse its concepts, no LLM call
      2. otherwise OCR text -> LLM concept extraction
    Pages that are only similar (a variant/edition) are still processed normally; they feed the
    book-level 'looks like a variant of X' suggestion instead."""

    def __init__(self, db: Session, ocr_provider=None, llm_provider=None):
        self.db = db
        self._ocr = ocr_provider
        self.llm = llm_provider or get_llm_provider()

    @property
    def ocr(self):  # created lazily: an exact-duplicate upload never needs OCR (or Azure credentials)
        if self._ocr is None:
            self._ocr = get_ocr_provider()
        return self._ocr

    def _cached_layout(self, chapter: Chapter):
        """Layer 0: the same file (by SHA-256) already processed into another chapter -> its page text."""
        if not chapter.source_sha256:
            return None
        source = self.db.scalar(
            select(Chapter).where(
                Chapter.source_sha256 == chapter.source_sha256,
                Chapter.status == ChapterStatus.READY,
                Chapter.id != chapter.id,
            ).limit(1)
        )
        if source is None:
            return None
        pages = self.db.scalars(select(Page).where(Page.chapter_id == source.id).order_by(Page.page_number)).all()
        if not pages:
            return None
        return {"pages": [{"page_number": p.page_number, "text": p.content_text, "lines": p.layout_data} for p in pages]}

    def process_chapter_file(self, chapter: Chapter, file_bytes: bytes, ext: str, user_id) -> list[Page]:
        """The chapter's previous pages are replaced, so re-running (retry / re-upload) never duplicates.
        Nothing is committed here: the caller commits once, so any failure rolls back to the previous state."""
        layout = self._cached_layout(chapter)
        ocr_reused = layout is not None
        if layout is None:
            layout = self.ocr.extract_layout(file_bytes, ext)  # slow, billable; done before touching the DB

        self.db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
        for old in list(chapter.pages):
            self.db.delete(old)
        self.db.flush()

        created: list[Page] = []
        per_page_matches: list[list[PageMatch]] = []
        pages_checked = pages_reused = 0
        for p_data in layout["pages"]:
            text, number = p_data["text"], p_data["page_number"]

            matches: list[PageMatch] = []
            signature = compute_minhash(text)
            if signature:
                pages_checked += 1
                matches = find_matches(self.db, signature, band_keys(signature))
                per_page_matches.append(matches)
            best = matches[0] if matches and matches[0].score >= settings.reuse_similarity else None

            page = Page(
                chapter_id=chapter.id, page_number=number, content_text=text,
                layout_data=p_data.get("lines"), verified=True, uploaded_by_id=user_id,
            )
            apply_fingerprint(page, text)
            self.db.add(page)
            self.db.flush()  # also makes this page's bands visible to the next page's lookup

            if best:
                pages_reused += 1
                logger.info("Page %s matches %s (%.2f); reusing concepts", number, best.page_id, best.score)
                source_page = self.db.get(Page, best.page_id)
                concepts = [
                    (c.name, c.description, c.learning_objectives, c.prerequisites)
                    for c in sorted(source_page.concepts, key=lambda c: c.position)
                ]
            else:
                try:
                    extracted = extract_page_concepts(self.llm, text)
                except ConceptExtractionError as exc:
                    raise ProcessingError(f"{exc} (page {number})") from exc
                concepts = [(c.name, c.description, c.learning_objectives, c.prerequisites) for c in extracted]

            for position, (name, description, objectives, prerequisites) in enumerate(concepts):
                self.db.add(Concept(
                    page_id=page.id, name=name, description=description, position=position,
                    learning_objectives=objectives, prerequisites=prerequisites,
                ))
            created.append(page)

        chapter.match_report = {
            "ocr_reused": ocr_reused,
            "pages_checked": pages_checked,
            "pages_reused": pages_reused,
            "suggestions": summarize_book_matches(
                per_page_matches, pages_checked, chapter.book_id, user_id
            ),
        }

        # A chapter only becomes 'ready' (the caller's commit) once its concepts are linked into a graph.
        self.db.flush()
        build_chapter_graph(self.db, chapter, self.llm)
        return created
