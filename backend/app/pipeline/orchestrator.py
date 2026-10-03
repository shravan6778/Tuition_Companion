import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import get_llm_provider
from app.models.content import Concept, Page
from app.ocr import get_ocr_provider
from app.pipeline.concepts import extract_page_concepts
from app.pipeline.fingerprint import compute_jaccard_similarity, compute_minhash

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Synchronous on purpose: OCR and LLM clients are blocking, and FastAPI runs plain `def`
    routes in a threadpool, so this doesn't stall the event loop. Providers come from the
    factories, so tests and keyless dev use the fake ones (OCR_PROVIDER / LLM_PROVIDER=fake)."""

    def __init__(self, db: Session, ocr_provider=None, llm_provider=None):
        self.db = db
        self.ocr = ocr_provider or get_ocr_provider()
        self.llm = llm_provider or get_llm_provider()

    def process_upload(self, file_bytes: bytes, ext: str, metadata: dict, user_id, is_teacher: bool) -> list[Page]:
        """OCR -> per-page MinHash -> match against existing pages:
        ~95%+ reuse that page's concepts (no LLM call); otherwise extract concepts via LLM.
        All pages are written in ONE transaction: any failure rolls the whole upload back."""
        layout = self.ocr.extract_layout(file_bytes, ext)
        chapter_id = metadata["chapter_id"]

        existing = [p for p in self.db.scalars(select(Page)).all() if p.fingerprint]
        created: list[Page] = []
        try:
            for p_data in layout["pages"]:
                text, number = p_data["text"], p_data["page_number"]
                fp = compute_minhash(text)

                best: Optional[Page] = None
                best_score = 0.0
                for ep in existing:
                    score = compute_jaccard_similarity(fp, ep.fingerprint)
                    if score > best_score:
                        best, best_score = ep, score

                page = Page(
                    chapter_id=chapter_id,
                    page_number=number,
                    content_text=text,
                    layout_data=p_data.get("lines"),
                    verified=True if (best and best_score >= 0.95) else is_teacher,
                    uploaded_by_id=user_id,
                    fingerprint=fp,
                )
                self.db.add(page)
                self.db.flush()

                if best and best_score >= 0.95:
                    logger.info("Page %s matched %s (%.2f); reusing concepts", number, best.id, best_score)
                    for c in best.concepts:
                        self.db.add(Concept(
                            page_id=page.id, name=c.name, description=c.description,
                            learning_objectives=c.learning_objectives, prerequisites=c.prerequisites,
                        ))
                else:
                    for c in extract_page_concepts(self.llm, text):
                        self.db.add(Concept(
                            page_id=page.id, name=c.name, description=c.description,
                            learning_objectives=c.learning_objectives, prerequisites=c.prerequisites,
                        ))
                created.append(page)
                existing.append(page)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return created
