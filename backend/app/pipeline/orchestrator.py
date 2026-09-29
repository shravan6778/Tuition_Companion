from app.pipeline.fingerprint import compute_minhash, compute_jaccard_similarity
from app.models.content import Book, Page, Concept
from sqlalchemy.orm import Session

class PipelineOrchestrator:
    def __init__(self, db: Session, ocr_provider, llm_provider):
        self.db = db
        self.ocr_provider = ocr_provider
        self.llm_provider = llm_provider

    async def process_upload(self, file_stream, metadata: dict, user_id: str, is_teacher: bool):
        # 1. Azure OCR & Layout Extraction [source: 2]
        layout_results = await self.ocr_provider.extract_text_and_layout(file_stream)
        
        # Determine verified status based on uploader role [source: 2]
        is_verified = is_teacher 
        
        processed_pages = []
        for page_data in layout_results["pages"]:
            page_text = page_data["text"]
            
            # Layer 2: Fuzzy fingerprint match [source: 2]
            page_fingerprint = compute_minhash(page_text)
            existing_pages = self.db.query(Page).all() # Optimize this with vector/hash search in production
            
            best_match = None
            best_score = 0.0
            
            for ep in existing_pages:
                if ep.fingerprint:
                    score = compute_jaccard_similarity(page_fingerprint, ep.fingerprint)
                    if score > best_score:
                        best_score = score
                        best_match = ep

            if best_score >= 0.95:
                # High match: link to existing concept graph, skip LLM [source: 2]
                processed_pages.append(best_match)
                continue
            
            elif 0.60 <= best_score < 0.95:
                # Partial match: Variant tracking logic here (Layer 3) [source: 2]
                # Requires structural signature check & teacher confirmation
                pass # MVP simplification: Process as new for now, log variant relationship
                
            # Low match or MVP fallback: Process as new page [source: 2]
            new_page = Page(
                chapter_id=metadata.get("chapter_id"), # Assuming chapter exists
                page_number=page_data["page_number"],
                content_text=page_text,
                layout_data=layout_results["paragraphs"],
                verified=is_verified,
                uploaded_by_id=user_id,
                fingerprint=page_fingerprint
            )
            self.db.add(new_page)
            self.db.commit()
            
            # LLM extraction per section on new/differing pages only [source: 2]
            concepts = await self.llm_provider.extract_concepts(page_text)
            for c in concepts:
                new_concept = Concept(page_id=new_page.id, name=c['name'], description=c['description'])
                self.db.add(new_concept)
                
            self.db.commit()
            processed_pages.append(new_page)
            
        return processed_pages