import logging
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import ProcessingError
from app.llm import get_llm_provider
from app.models.content import Chapter, Concept, ConceptEdge, Page
from app.ocr import get_ocr_provider
from app.pipeline.concepts import ConceptExtractionError, extract_page_concepts
from app.pipeline.fingerprint import compute_jaccard_similarity, compute_minhash
from app.pipeline.graph import build_chapter_graph

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Synchronous on purpose: OCR and LLM clients block, and this runs in a background thread
    (see pipeline/jobs.py). Providers come from the factories, so tests and keyless dev use the
    fake ones (OCR_PROVIDER / LLM_PROVIDER=fake)."""

    def __init__(self, db: Session, ocr_provider=None, llm_provider=None):
        self.db = db
        self.ocr = ocr_provider or get_ocr_provider()
        self.llm = llm_provider or get_llm_provider()

    def process_chapter_file(self, chapter: Chapter, file_bytes: bytes, ext: str, user_id) -> list[Page]:
        """OCR -> per-page MinHash -> match against pages of OTHER chapters:
        ~95%+ reuse that page's concepts (no LLM call); otherwise extract concepts via LLM.

        The chapter's previous pages are replaced, so re-running (retry / re-upload) never duplicates.
        Nothing is committed here: the caller commits once, so any failure rolls back to the previous state."""
        layout = self.ocr.extract_layout(file_bytes, ext)  # slow network call, done before touching the DB

        known = [
            p for p in self.db.scalars(
                select(Page).where(Page.chapter_id != chapter.id, Page.fingerprint.isnot(None))
            ).all()
        ]

        self.db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
        for old in list(chapter.pages):
            self.db.delete(old)
        self.db.flush()

        created: list[Page] = []
        for p_data in layout["pages"]:
            text, number = p_data["text"], p_data["page_number"]
            fp = compute_minhash(text)

            best: Optional[Page] = None
            best_score = 0.0
            for kp in known:
                score = compute_jaccard_similarity(fp, kp.fingerprint)
                if score > best_score:
                    best, best_score = kp, score
            matched = best is not None and best_score >= 0.95

            page = Page(
                chapter_id=chapter.id,
                page_number=number,
                content_text=text,
                layout_data=p_data.get("lines"),
                verified=True,
                uploaded_by_id=user_id,
                fingerprint=fp,
            )
            self.db.add(page)
            self.db.flush()

            if matched:
                logger.info("Page %s matched %s (%.2f); reusing concepts", number, best.id, best_score)
                concepts = [
                    (c.name, c.description, c.learning_objectives, c.prerequisites)
                    for c in sorted(best.concepts, key=lambda c: c.position)
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
            known.append(page)

        # A chapter only becomes 'ready' (the caller's commit) once its concepts are linked into a graph.
        self.db.flush()
        build_chapter_graph(self.db, chapter, self.llm)
        return created
