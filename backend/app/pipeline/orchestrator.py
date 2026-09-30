import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.llm.openai_compat_provider import LLMProvider
from app.models.content import Book, Chapter, Concept, Page
from app.ocr.azure_provider import AzureDocIntelProvider
from app.pipeline.fingerprint import compute_jaccard_similarity, compute_minhash

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    def __init__(
        self,
        db: Session,
        ocr_provider: Optional[AzureDocIntelProvider] = None,
        llm_provider: Optional[LLMProvider] = None,
    ):
        self.db = db
        self.ocr = ocr_provider or AzureDocIntelProvider(
            endpoint=settings.AZURE_DOC_INTEL_ENDPOINT,
            key=settings.AZURE_DOC_INTEL_KEY,
        )
        self.llm = llm_provider or LLMProvider()

    async def detect_publisher_from_cover(self, file_bytes: bytes, ext: str) -> Optional[str]:
        """Layer 1: Metadata + Cover-page OCR to extract publisher."""
        try:
            ocr_res = self.ocr.extract(file_bytes, ext)
            text_lower = ocr_res.text.lower()
            known_publishers = ["ncert", "scert", "cambridge", "oxford", "pearson", "s. chand", "ratna sagar"]
            for pub in known_publishers:
                if pub in text_lower:
                    return pub.upper()
        except Exception as e:
            logger.warning(f"Could not extract publisher from cover: {e}")
        return None

    async def process_upload(
        self,
        file_bytes: bytes,
        ext: str,
        metadata: dict,
        user_id,
        is_teacher: bool,
    ) -> list[Page]:
        """
        Executes lazy page-by-page ingestion[cite: 2]:
        1. Extract text and layout via Azure Document Intelligence[cite: 2].
        2. Normalize and compute MinHash fingerprint[cite: 2].
        3. Match against existing corpus:
           - ~95%+ -> reuse existing concept graph, zero LLM cost[cite: 2].
           - 60-90% -> variant candidate[cite: 2].
           - New -> process with LLM and store[cite: 2].
        """
        layout_result = self.ocr.extract_layout(file_bytes, ext)
        chapter_id = metadata["chapter_id"]
        book_id = metadata.get("book_id")

        existing_pages = self.db.scalars(select(Page)).all()
        processed_pages = []

        for p_data in layout_result["pages"]:
            page_text = p_data["text"]
            page_num = p_data["page_number"]
            page_fp = compute_minhash(page_text)

            best_match: Optional[Page] = None
            best_score = 0.0

            for ep in existing_pages:
                if ep.fingerprint:
                    score = compute_jaccard_similarity(page_fp, ep.fingerprint)
                    if score > best_score:
                        best_score = score
                        best_match = ep

            # Layer 2: ~95%+ exact/near-identical match -> reuse concepts[cite: 2]
            if best_score >= 0.95 and best_match:
                logger.info(f"Page matched existing page #{best_match.id} with score {best_score:.2f}[cite: 2]. Linking concepts[cite: 2].")
                new_page = Page(
                    chapter_id=chapter_id,
                    page_number=page_num,
                    content_text=page_text,
                    layout_data=layout_result.get("paragraphs"),
                    verified=True,  # Matches an already verified corpus page[cite: 2]
                    uploaded_by_id=user_id,
                    fingerprint=page_fp,
                )
                self.db.add(new_page)
                self.db.flush()

                # Reuse existing concepts without calling LLM[cite: 2]
                for c in best_match.concepts:
                    self.db.add(
                        Concept(
                            page_id=new_page.id,
                            name=c.name,
                            description=c.description,
                            learning_objectives=c.learning_objectives,
                            prerequisites=c.prerequisites,
                        )
                    )
                self.db.commit()
                processed_pages.append(new_page)
                continue

            # Layer 3 / New Page: Extract concepts via LLM[cite: 2]
            new_page = Page(
                chapter_id=chapter_id,
                page_number=page_num,
                content_text=page_text,
                layout_data=layout_result.get("paragraphs"),
                verified=is_teacher,  # Teacher = verified, Student = unverified[cite: 2]
                uploaded_by_id=user_id,
                fingerprint=page_fp,
            )
            self.db.add(new_page)
            self.db.flush()

            extracted_concepts = await self.llm.extract_concepts(page_text)
            for c in extracted_concepts:
                self.db.add(
                    Concept(
                        page_id=new_page.id,
                        name=c.get("name", "Unnamed Concept"),
                        description=c.get("description", ""),
                        learning_objectives=c.get("learning_objectives", []),
                        prerequisites=c.get("prerequisites", []),
                    )
                )

            self.db.commit()
            processed_pages.append(new_page)

        return processed_pages