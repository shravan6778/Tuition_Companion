import logging

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.llm import get_llm_provider
from app.models.content import Chapter, ChapterStatus, Concept, ConceptEdge, Page
from app.ocr import get_ocr_provider
from app.embeddings import get_embedding_provider
from app.pipeline.concepts import ConceptExtractionError, SUMMARY_TAIL_FROM, extract_page, looks_like_activity, looks_like_recap_page, looks_like_summary_page
from app.pipeline.fingerprint import apply_fingerprint, band_keys, compute_minhash, tokenize
from app.pipeline.graph import build_chapter_graph, copy_chapter_graph
from app.pipeline.matching import PageMatch, find_matches, summarize_book_matches

logger = logging.getLogger(__name__)

REVIEW_MIN_WORDS = 40  # a page this long that yields zero concepts is suspicious
MAX_REVIEW_REPORTED = 50


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

    def __init__(self, db: Session, ocr_provider=None, llm_provider=None, embedder=None, reuse_concepts: bool = True):
        self.db = db
        self._ocr = ocr_provider
        self.llm = llm_provider or get_llm_provider()
        self._embedder = embedder  # callable list[str] -> vectors; None -> built from settings (or off)
        self.reuse_concepts = reuse_concepts  # False ('reprocess --fresh'): extract every page again

    def _name_embedder(self):
        """Only a real embedding provider is used to merge near-duplicate concept names; never the fake one."""
        if self._embedder is not None:
            return self._embedder
        if settings.embedding_provider.lower() != "openai_compat":
            return None
        try:
            provider = get_embedding_provider()
        except Exception:
            logger.warning("Embedding provider is not usable; skipping name merge", exc_info=True)
            return None
        return provider.embed if provider else None

    @property
    def ocr(self):  # created lazily: an exact-duplicate upload never needs OCR (or Azure credentials)
        if self._ocr is None:
            self._ocr = get_ocr_provider()
        return self._ocr

    @property
    def model_name(self) -> str:
        return getattr(self.llm, "model_name", "unknown")

    def _reusable(self, source_page: Page) -> bool:
        """Concepts are reused only if we know which model made them, and never the fake model's placeholders
        for a real run (otherwise one dev run with LLM_PROVIDER=fake would poison every later upload)."""
        made_by = source_page.concepts_model
        return made_by is not None and (made_by != "fake" or self.model_name == "fake")

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
        review_pages: list[dict] = []
        dropped_concepts = recap_pages = 0
        reused_from: list[tuple[Page, Page, list[Concept]]] = []  # (new page, source page, its new concepts)
        uncovered = 0  # pages that were extracted/filtered, so the source chapter's edges cannot be copied
        short_empty_pages: list[int] = []
        summary_seen = False  # after a chapter-end summary, pages are exercises: no concepts, no LLM calls
        total_pages = len(layout["pages"])
        for index, p_data in enumerate(layout["pages"]):
            text, number = p_data["text"], p_data["page_number"]
            tail = summary_seen
            if looks_like_summary_page(text) and index >= SUMMARY_TAIL_FROM * total_pages:
                summary_seen = True

            matches: list[PageMatch] = []
            signature = compute_minhash(text)
            if signature:
                pages_checked += 1
                matches = find_matches(self.db, signature, band_keys(signature))
                per_page_matches.append(matches)
            best = matches[0] if matches and matches[0].score >= settings.reuse_similarity else None
            source_page = self.db.get(Page, best.page_id) if best else None
            if source_page is not None and (not self.reuse_concepts or not self._reusable(source_page)):
                logger.info("Not reusing concepts of page %s (made by %r)", source_page.id, source_page.concepts_model)
                best, source_page = None, None

            page = Page(
                chapter_id=chapter.id, page_number=number, content_text=text,
                layout_data=p_data.get("lines"), uploaded_by_id=user_id,
            )
            apply_fingerprint(page, text)
            self.db.add(page)
            self.db.flush()  # also makes this page's bands visible to the next page's lookup

            recap = looks_like_recap_page(text) or tail
            filtered = False
            if tail:
                best, source_page = None, None
                page.concepts_model = self.model_name
                concepts, filtered = [], True
            elif best:
                pages_reused += 1
                logger.info("Page %s matches %s (%.2f); reusing concepts", number, best.page_id, best.score)
                page.concepts_model = source_page.concepts_model
                concepts = [
                    (c.name, c.description, c.learning_objectives, c.prerequisites)
                    for c in sorted(source_page.concepts, key=lambda c: c.position)
                ]
                kept = [] if recap else [c for c in concepts if not looks_like_activity(c[0])]
                filtered = len(kept) != len(concepts)
                dropped_concepts += len(concepts) - len(kept)
                concepts = kept
            else:
                page.concepts_model = self.model_name
                try:
                    extraction = extract_page(self.llm, text)
                except ConceptExtractionError as exc:
                    raise ProcessingError(f"{exc} (page {number})") from exc
                dropped_concepts += extraction.dropped
                filtered = extraction.dropped > 0
                recap = recap or extraction.page_kind in ("recap", "exercise")
                concepts = [(c.name, c.description, c.learning_objectives, c.prerequisites) for c in extraction.concepts]
            recap_pages += 1 if recap else 0

            if best and source_page.needs_review:  # a reused page keeps its source's verdict, never a fresh one
                page.needs_review, page.review_note = True, source_page.review_note
                review_pages.append({"page": number, "note": page.review_note})
            elif not best and not concepts and not filtered and not recap and len(tokenize(text)) >= REVIEW_MIN_WORDS:
                page.needs_review = True
                page.review_note = "No concepts were found on a page with a lot of text. It may be a bad scan."
                review_pages.append({"page": number, "note": page.review_note})

            new_concepts: list[Concept] = []
            for position, (name, description, objectives, prerequisites) in enumerate(concepts):
                concept = Concept(
                    page_id=page.id, name=name, description=description, position=position,
                    learning_objectives=objectives, prerequisites=prerequisites,
                )
                self.db.add(concept)
                new_concepts.append(concept)
            created.append(page)
            if best and not filtered:
                reused_from.append((page, source_page, new_concepts))
            elif tail or (not signature and not concepts):
                short_empty_pages.append(number)  # a page with no concepts by design is neutral for copying
            else:
                uncovered += 1

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
        report = self._copied_graph(chapter, reused_from, uncovered, short_empty_pages)
        if report is None:
            report = build_chapter_graph(self.db, chapter, self.llm, self._name_embedder())
        counters = {"dropped_concepts": dropped_concepts, "recap_pages": recap_pages}
        if report.get("edges_copied"):  # same pages as the source: its counters are the right ones
            counters = {k: report.get(k, v) for k, v in counters.items()}
        chapter.graph_report = {**report, "review_pages": review_pages[:MAX_REVIEW_REPORTED], **counters}
        return created

    def _copied_graph(self, chapter, reused_from, uncovered, short_empty_pages):
        """Every page reused unchanged from ONE finished chapter with the same concepts -> copy its graph, so a
        second run over the same content gives the same edges (and costs no LLM call). None = build normally."""
        if uncovered or not reused_from:
            return None
        source_ids = {src.chapter_id for _, src, _ in reused_from}
        if len(source_ids) != 1:
            return None
        source = self.db.get(Chapter, source_ids.pop())
        if (
            source is None or source.id == chapter.id or source.status != ChapterStatus.READY
            or (source.graph_report or {}).get("llm_linking") != "done"
        ):
            return None
        source_concepts = self.db.scalars(
            select(Concept).join(Page, Page.id == Concept.page_id).where(Page.chapter_id == source.id)
        ).all()
        by_page: dict = {}
        for c in source_concepts:
            by_page.setdefault(c.page_id, []).append(c)
        source_pages = {p.id: p.page_number for p in self.db.scalars(select(Page).where(Page.chapter_id == source.id))}
        if any(source_pages[pid] in short_empty_pages for pid in by_page):
            return None
        concept_map: dict = {}
        for _, src_page, new_concepts in reused_from:
            old = sorted(by_page.get(src_page.id, []), key=lambda c: c.position)
            if len(old) != len(new_concepts):
                return None
            concept_map.update({o.id: n for o, n in zip(old, new_concepts)})
        if set(concept_map) != {c.id for c in source_concepts}:
            return None  # the source has concepts on pages we did not reuse
        try:
            return copy_chapter_graph(self.db, chapter, source, concept_map)
        except KeyError:
            return None
