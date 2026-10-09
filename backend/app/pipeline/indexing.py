"""Derived data for a chapter that is already `ready`: embeddings (PostgreSQL) and the Memgraph copy.

Runs AFTER the chapter's all-or-nothing commit, never inside it: an outage of the embedding service or of
Memgraph must not make a good chapter `failed`. Students use the graph in PostgreSQL either way; this stage
only feeds search. Each stage records its state on the chapter (`embedding_status`, `graph_sync_status`,
`index_error`), and `python -m app.db.sync_graph` retries whatever is pending or failed.

  1. embeddings: one vector per page (its text) and per canonical concept (name + description), stored in
     `content_embeddings`. Unchanged text keeps its vector; identical text anywhere reuses one; so a
     reprocess or an identical re-upload costs few or no embedding calls.
  2. graph store: the chapter's pages, concepts, prerequisite edges and vectors are written to Memgraph from
     what PostgreSQL holds (stored vectors included, so no embedding calls are needed to rebuild it).
"""
import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import FAKE_EMBEDDING_MODEL, settings
from app.embeddings import EmbeddingError, get_embedding_provider
from app.embeddings.vectors import from_bytes, to_bytes
from app.graph_store import GraphStoreError, get_graph_store
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, PageNode
from app.models.content import Book, Chapter, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, CrossChapterEdge, IndexStatus, Page
from app.pipeline.fingerprint import tokenize

logger = logging.getLogger(__name__)

GENERIC_EMBEDDING_ERROR = "Embeddings could not be created. See the server log, then run python -m app.db.sync_graph."
GENERIC_GRAPH_ERROR = "The graph store could not be updated. See the server log, then run python -m app.db.sync_graph."


@dataclass
class IndexReport:
    chapter_id: str = ""
    embedding: str = ""          # status after this run (done / skipped / failed / unchanged)
    graph: str = ""              # same for the graph store
    embedded: int = 0            # vectors created with a call to the embedding service
    reused: int = 0              # vectors copied from identical text elsewhere (no call)
    kept: int = 0                # vectors already up to date
    removed: int = 0             # vectors of concepts/pages that no longer exist as such
    graph_pages: int = 0
    graph_concepts: int = 0
    graph_edges: int = 0
    without_vectors: int = 0     # nodes written to the graph store with no vector
    errors: list[str] = field(default_factory=list)  # detailed messages for the operator (the DB keeps a generic one)


# ---- what gets embedded -------------------------------------------------------------------------
@dataclass
class _Item:
    kind: str       # "page" | "concept"
    id: object      # page/concept id
    text: str

    @property
    def sha(self) -> str:
        return hashlib.sha256(self.text.encode("utf8")).hexdigest()


def concept_text(concept: Concept) -> str:
    return f"{concept.name}. {concept.description or ''}".strip()[: settings.embedding_max_chars]


def page_text(page: Page) -> Optional[str]:
    """None for covers/blank pages (the same 'too short to matter' rule the fingerprints use)."""
    text = (page.content_text or "").strip()
    if len(tokenize(text)) < settings.fingerprint_min_words:
        return None
    return text[: settings.embedding_max_chars]


def _chapter_pages(db: Session, chapter: Chapter) -> list[Page]:
    return list(db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)))


def _canonical_concepts(db: Session, chapter: Chapter) -> list[Concept]:
    return list(db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id, Concept.is_canonical.is_(True))
        .order_by(Page.page_number, Concept.position)
    ))


def chapter_items(db: Session, chapter: Chapter) -> list[_Item]:
    items = [_Item("concept", c.id, concept_text(c)) for c in _canonical_concepts(db, chapter)]
    for page in _chapter_pages(db, chapter):
        text = page_text(page)
        if text:
            items.append(_Item("page", page.id, text))
    return items


# ---- stage 1: embeddings ------------------------------------------------------------------------
def embed_chapter(db: Session, chapter: Chapter, provider) -> IndexReport:
    """Brings the chapter's `content_embeddings` up to date. Nothing is committed (the caller commits)."""
    report = IndexReport(chapter_id=str(chapter.id))
    existing = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == chapter.id)):
        existing[("page", row.page_id) if row.page_id else ("concept", row.concept_id)] = row

    wanted: set = set()
    todo: list[tuple[_Item, str, Optional[bytes]]] = []  # (item, sha, vector bytes when found in the cache)
    for item in chapter_items(db, chapter):
        key = (item.kind, item.id)
        wanted.add(key)
        sha = item.sha
        row = existing.get(key)
        if row and row.model == provider.model_name and row.dim == provider.dim and row.text_sha256 == sha:
            report.kept += 1
            continue
        cached = db.scalar(
            select(ContentEmbedding).where(
                ContentEmbedding.model == provider.model_name, ContentEmbedding.dim == provider.dim,
                ContentEmbedding.text_sha256 == sha,
            ).limit(1)
        )
        todo.append((item, sha, cached.vector if cached else None))

    fresh_texts = {sha: item.text for item, sha, vec in todo if vec is None}
    fresh: dict[str, bytes] = {}
    if fresh_texts:
        shas = list(fresh_texts)
        vectors = provider.embed([fresh_texts[s] for s in shas])
        if len(vectors) != len(shas):
            raise EmbeddingError(f"Asked for {len(shas)} embeddings, got {len(vectors)}.")
        fresh = {sha: to_bytes(vec) for sha, vec in zip(shas, vectors)}

    for item, sha, cached_vector in todo:
        vector = cached_vector if cached_vector is not None else fresh[sha]
        if cached_vector is not None:
            report.reused += 1
        else:
            report.embedded += 1
        row = existing.get((item.kind, item.id))
        if row is None:
            row = ContentEmbedding(chapter_id=chapter.id)
            if item.kind == "page":
                row.page_id = item.id
            else:
                row.concept_id = item.id
            db.add(row)
        row.model, row.dim, row.text_sha256, row.vector = provider.model_name, provider.dim, sha, vector
        row.created_at = datetime.now(timezone.utc)

    for key, row in existing.items():  # e.g. a concept that stopped being the canonical one
        if key not in wanted:
            db.delete(row)
            report.removed += 1
    db.flush()
    return report


# ---- stage 2: the graph store copy --------------------------------------------------------------
def _usable(row: ContentEmbedding) -> bool:
    """Placeholder (fake) vectors never go into a real store; vectors of the wrong size can't be indexed."""
    if row.dim != settings.embedding_dim:
        return False
    return row.model != FAKE_EMBEDDING_MODEL or settings.embedding_provider.lower() == "fake"


def build_chapter_payload(db: Session, chapter: Chapter) -> ChapterGraph:
    """Everything the graph store needs, read from PostgreSQL. No page text: ids, numbers, names, vectors."""
    book = db.get(Book, chapter.book_id)
    vectors: dict[tuple[str, object], tuple[str, list[float]]] = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == chapter.id)):
        if _usable(row):
            key = ("page", row.page_id) if row.page_id else ("concept", row.concept_id)
            vectors[key] = (row.model, from_bytes(row.vector))

    pages = _chapter_pages(db, chapter)
    rows = db.execute(
        select(Concept, Page.id).join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id).order_by(Page.page_number, Concept.position)
    ).all()
    pages_by_key: dict[str, list[str]] = defaultdict(list)
    for concept, page_id in rows:
        if str(page_id) not in pages_by_key[concept.name_key]:
            pages_by_key[concept.name_key].append(str(page_id))
    canonical = [c for c, _ in rows if c.is_canonical]

    models = {m for m, _ in vectors.values()}
    graph = ChapterGraph(
        book_id=str(book.id), chapter_id=str(chapter.id), title=chapter.title or "", sequence_num=chapter.sequence_num or 0,
        is_reference=bool(book.is_reference), owner_teacher_id=str(book.owner_teacher_id) if book.owner_teacher_id else None,
        embedding_model=models.pop() if len(models) == 1 else None,
    )
    graph.pages = [
        PageNode(str(p.id), p.page_number or 0, vectors.get(("page", p.id), (None, None))[1]) for p in pages
    ]
    graph.concepts = [
        ConceptNode(str(c.id), c.name, c.description or "", c.position or 0, vectors.get(("concept", c.id), (None, None))[1])
        for c in canonical
    ]
    for c in canonical:
        graph.concept_pages += [(str(c.id), page_id) for page_id in pages_by_key.get(c.name_key, [])]
    graph.edges = [
        EdgeRow(str(e.concept_id), str(e.prerequisite_id), e.source)
        for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))
    ]
    return graph


def sync_cross_edges(db: Session, book_id) -> bool:
    """Copy the book's cross-chapter prerequisite edges (PostgreSQL) into the graph store. Best effort: a store
    outage is logged and the next chapter write / `sync_graph` repeats it. Returns True when written."""
    try:
        store = get_graph_store()
        if store is None:
            return False
        rows = db.execute(
            select(CrossChapterEdge.concept_id, CrossChapterEdge.prerequisite_id)
            .join(Chapter, Chapter.id == CrossChapterEdge.chapter_id).where(Chapter.book_id == book_id)
        ).all()
        store.ensure_schema()
        store.replace_cross_edges(str(book_id), [EdgeRow(str(c), str(p), "book") for c, p in rows])
        return True
    except Exception:
        logger.warning("Cross-chapter edge sync for book %s failed", book_id, exc_info=True)
        return False


# ---- orchestration ------------------------------------------------------------------------------
def _fail(db: Session, chapter_id, field_name: str, message: str) -> None:
    """Record a failed stage on a fresh view of the chapter (the failed transaction was rolled back)."""
    chapter = db.get(Chapter, chapter_id)
    setattr(chapter, field_name, IndexStatus.FAILED)
    chapter.index_error = message[:500]
    db.commit()


def index_chapter(session_factory, chapter_id, *, embed: bool = True) -> IndexReport:
    """Both stages for one ready chapter, with its own session. NEVER raises (it runs in the background and
    after the chapter is already committed). `embed=False` skips stage 1: that is what a rebuild of the graph
    store uses, so it works from the stored vectors without calling the embedding service."""
    report = IndexReport(chapter_id=str(chapter_id))
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY:
            report.errors.append("chapter is not ready")
            return report

        if embed:
            try:
                provider = get_embedding_provider()
            except RuntimeError as exc:  # misconfigured settings; the text names the settings, never a secret
                provider = False
                report.embedding = IndexStatus.FAILED
                report.errors.append(str(exc))
                _fail(db, chapter_id, "embedding_status", str(exc))
            if provider is None:
                chapter.embedding_status = IndexStatus.SKIPPED
                report.embedding = IndexStatus.SKIPPED
                db.commit()
            elif provider is not False:
                try:
                    done = embed_chapter(db, chapter, provider)
                    chapter.embedding_status = IndexStatus.DONE
                    db.commit()
                    report.embedding = IndexStatus.DONE
                    report.embedded, report.reused, report.kept, report.removed = done.embedded, done.reused, done.kept, done.removed
                except Exception as exc:
                    db.rollback()
                    logger.exception("Embedding chapter %s failed", chapter_id)
                    report.embedding = IndexStatus.FAILED
                    report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
                    _fail(db, chapter_id, "embedding_status", GENERIC_EMBEDDING_ERROR)
            if report.embedding == IndexStatus.FAILED:
                return report  # nothing worth sending to the graph store yet: the retry does both stages

        chapter = db.get(Chapter, chapter_id)
        try:
            store = get_graph_store()
        except Exception as exc:
            store = False
            report.graph = IndexStatus.FAILED
            report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
            _fail(db, chapter_id, "graph_sync_status", GENERIC_GRAPH_ERROR)
        if store is None:
            chapter.graph_sync_status = IndexStatus.SKIPPED
            report.graph = IndexStatus.SKIPPED
            db.commit()
        elif store is not False:
            try:
                payload = build_chapter_payload(db, chapter)
                store.ensure_schema()
                store.replace_chapter(payload)
                chapter.graph_sync_status = IndexStatus.DONE
                report.graph = IndexStatus.DONE
                report.graph_pages, report.graph_concepts, report.graph_edges = len(payload.pages), len(payload.concepts), len(payload.edges)
                report.without_vectors = sum(1 for n in [*payload.pages, *payload.concepts] if n.embedding is None)
                db.commit()
                sync_cross_edges(db, chapter.book_id)  # replacing the chapter dropped its edges to other chapters
            except Exception as exc:
                db.rollback()
                logger.exception("Graph sync of chapter %s failed", chapter_id)
                report.graph = IndexStatus.FAILED
                report.errors.append(f"{type(exc).__name__}: {str(exc)[:300]}")
                _fail(db, chapter_id, "graph_sync_status", GENERIC_GRAPH_ERROR)

        chapter = db.get(Chapter, chapter_id)
        if (chapter.embedding_status in (IndexStatus.DONE, IndexStatus.SKIPPED)
                and chapter.graph_sync_status in (IndexStatus.DONE, IndexStatus.SKIPPED)):
            chapter.index_error = None
            chapter.indexed_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as exc:  # last resort: indexing must never take the caller down
        logger.exception("Indexing chapter %s crashed", chapter_id)
        report.errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()
    return report


def chapters_needing_index(db: Session, book_id=None, chapter_id=None) -> list[Chapter]:
    query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
    if chapter_id is not None:
        query = query.where(Chapter.id == chapter_id)
    elif book_id is not None:
        query = query.where(Chapter.book_id == book_id)
    embeddings_on = settings.embedding_provider.lower() != "none"
    graph_on = settings.graph_store_provider.lower() != "none"

    def needs_work(status: str, switched_on: bool) -> bool:
        # 'skipped' means "that stage was off when the chapter was processed": once it is switched on, do it now
        return status in (IndexStatus.PENDING, IndexStatus.FAILED) or (status == IndexStatus.SKIPPED and switched_on)

    return [
        c for c in db.scalars(query)
        if chapter_id is not None or needs_work(c.embedding_status, embeddings_on) or needs_work(c.graph_sync_status, graph_on)
    ]
