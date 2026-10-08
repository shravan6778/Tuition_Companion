"""Step 9: embeddings (durable copy in PostgreSQL) and the Memgraph copy of the concept graph.

Memgraph itself is not available in the test run: the store is exercised with the in-memory fake (same
behaviour contract) and the Memgraph client with a stub driver that records what it would send.
`python -m app.db.smoke_memgraph` is the real-server check."""
import uuid

import pytest
from sqlalchemy import select

from app.core.config import FAKE_EMBEDDING_MODEL, settings
from app.db import smoke_memgraph
from app.db.sync_graph import sync_all
from app.embeddings import EmbeddingError, get_embedding_provider
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.embeddings.openai_compat_provider import OpenAICompatEmbeddingProvider
from app.embeddings.vectors import cosine, from_bytes, to_bytes
from app.graph_store import FAKE_STORE, get_graph_store
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, GraphStoreError, PageNode
from app.graph_store.fake_store import FakeGraphStore
from app.graph_store.memgraph_store import CONCEPT_INDEX, PAGE_INDEX, MemgraphStore
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, IndexStatus, Page
from app.pipeline.indexing import build_chapter_payload, chapters_needing_index, embed_chapter, index_chapter
from app.pipeline.jobs import mark_processing
from tests.test_chapter_jobs import chapter_status, setup_chapter, upload
from tests.test_pipeline import _text_pdf


def words(tag: str, n: int = 20) -> str:
    """A page of n distinct words (>= 15 so it counts as a real page)."""
    return " ".join(f"{tag}{i}" for i in range(n))


class SharedProvider(FakeEmbeddingProvider):
    """One provider object for the whole test, so calls can be counted across the background job."""


@pytest.fixture()
def provider(monkeypatch, indexing_on):
    p = SharedProvider(settings.embedding_dim)
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: p)
    return p


def upload_ready(client, session_factory, *texts, tag="teachera"):
    th, book_id, ch = setup_chapter(client, session_factory, tag)
    assert upload(client, th, book_id, ch, _text_pdf(*texts)).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"
    return th, book_id, ch


def chapter_row(session_factory, ch) -> Chapter:
    with session_factory() as db:
        c = db.get(Chapter, uuid.UUID(str(ch)))
        db.expunge(c)
        return c


def embedding_rows(session_factory, ch):
    with session_factory() as db:
        return db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == uuid.UUID(str(ch)))).all()


# ---- vectors and the fake provider ----------------------------------------------------------------

def test_vector_bytes_roundtrip_and_cosine():
    v = [0.5, -0.25, 1.0]
    assert from_bytes(to_bytes(v)) == pytest.approx(v)
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 0]) == 0.0


def test_fake_embeddings_are_deterministic_unit_length_and_reflect_shared_words():
    p = FakeEmbeddingProvider(128)
    a, b, c = p.embed(["the cell membrane controls what enters the cell", "the cell membrane controls entry", "volcanic rock formation in mountains"])
    assert p.embed(["the cell membrane controls what enters the cell"])[0] == a
    assert len(a) == 128 and cosine(a, a) == pytest.approx(1.0)
    assert cosine(a, b) > cosine(a, c) + 0.2
    assert p.model_name == FAKE_EMBEDDING_MODEL


# ---- the pipeline stage ---------------------------------------------------------------------------

def test_upload_embeds_concepts_and_pages_and_writes_the_graph_copy(client, session_factory, provider):
    th, book_id, ch = upload_ready(client, session_factory, words("alpha"), words("beta"))
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("done", "done")
    assert row.index_error is None and row.indexed_at is not None

    with session_factory() as db:
        canonical = db.scalars(select(Concept).join(Page).where(Page.chapter_id == row.id, Concept.is_canonical.is_(True))).all()
        pages = db.scalars(select(Page).where(Page.chapter_id == row.id)).all()
        edges = db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == row.id)).all()
        rows = db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id == row.id)).all()
        assert len(rows) == len(canonical) + len(pages)
        assert {r.model for r in rows} == {FAKE_EMBEDDING_MODEL} and {r.dim for r in rows} == {settings.embedding_dim}

        graph = FAKE_STORE.chapter(str(row.id))
        assert graph is not None and graph.book_id == book_id
        assert {c.id for c in graph.concepts} == {str(c.id) for c in canonical}
        assert {(e.concept_id, e.prerequisite_id, e.source) for e in graph.edges} == {
            (str(e.concept_id), str(e.prerequisite_id), e.source) for e in edges}
        assert all(c.embedding is not None for c in graph.concepts) and all(p.embedding is not None for p in graph.pages)
        # derived data only: the page TEXT never travels to the graph store (concept names are short extracts)
        assert words("alpha") not in repr(graph) and words("beta") not in repr(graph)
        assert all(not hasattr(p, "content_text") and not hasattr(p, "text") for p in graph.pages)


def test_short_pages_are_not_embedded_but_stay_in_the_graph(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("long"), "Cover page")
    with session_factory() as db:
        pages = {p.page_number: p for p in db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(ch)))}
        assert pages[1].embedding is not None and pages[2].embedding is None
    graph = FAKE_STORE.chapter(ch)
    assert [p.embedding is not None for p in graph.pages] == [True, False]


def test_reprocessing_replaces_vectors_and_the_graph_copy(client, session_factory, provider):
    th, book_id, ch = upload_ready(client, session_factory, words("one"), words("two"))
    first_pages = {p.id for p in FAKE_STORE.chapter(ch).pages}
    assert upload(client, th, book_id, ch, _text_pdf(words("three"))).status_code == 202
    graph = FAKE_STORE.chapter(ch)
    assert len(graph.pages) == 1 and graph.pages[0].id not in first_pages
    with session_factory() as db:
        page_ids = {p.id for p in db.scalars(select(Page).where(Page.chapter_id == uuid.UUID(ch)))}
        assert {r.page_id for r in embedding_rows(session_factory, ch) if r.page_id} == page_ids  # old vectors are gone


def test_unchanged_chapter_is_not_embedded_again(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("same"))
    calls = provider.texts_embedded
    report = index_chapter(session_factory, uuid.UUID(ch))
    assert provider.texts_embedded == calls and report.embedded == 0 and report.kept > 0 and not report.errors


def test_identical_text_in_another_chapter_reuses_the_vector_without_a_call(client, session_factory, provider):
    upload_ready(client, session_factory, words("shared"), tag="teachera")
    calls = provider.texts_embedded
    upload_ready(client, session_factory, words("shared"), tag="teacherb")  # same text, other teacher
    assert provider.texts_embedded == calls
    assert len(embedding_rows(session_factory, FAKE_STORE.list_chapter_ids().pop())) > 0


def test_changing_the_embedding_model_re_embeds_everything(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("model"))
    before = len(embedding_rows(session_factory, ch))
    provider.model_name = "another-model"
    report = index_chapter(session_factory, uuid.UUID(ch))
    assert report.embedded == before and report.kept == 0
    assert {r.model for r in embedding_rows(session_factory, ch)} == {"another-model"}


def test_only_canonical_concepts_get_a_vector_and_stale_rows_are_removed(session_factory, provider):
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="T", is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="Ch", sequence_num=1, status=ChapterStatus.READY)
        db.add(ch)
        db.flush()
        p1 = Page(chapter_id=ch.id, page_number=1, content_text=words("a"))
        p2 = Page(chapter_id=ch.id, page_number=2, content_text=words("b"))
        db.add_all([p1, p2])
        db.flush()
        c1 = Concept(page_id=p1.id, name="Atom", description="d", position=0, name_key="atom", is_canonical=True)
        c2 = Concept(page_id=p2.id, name="atom", description="d2", position=0, name_key="atom", is_canonical=False)
        db.add_all([c1, c2])
        db.flush()
        embed_chapter(db, ch, provider)
        db.commit()
        concept_rows = db.scalars(select(ContentEmbedding).where(ContentEmbedding.concept_id.is_not(None))).all()
        assert [r.concept_id for r in concept_rows] == [c1.id]
        c1.is_canonical, c2.is_canonical = False, True  # identity changed (e.g. relink)
        db.flush()
        report = embed_chapter(db, ch, provider)
        db.commit()
        assert report.removed == 1
        assert [r.concept_id for r in db.scalars(select(ContentEmbedding).where(ContentEmbedding.concept_id.is_not(None)))] == [c2.id]


# ---- failures never fail the chapter ---------------------------------------------------------------

class DownProvider(FakeEmbeddingProvider):
    def embed(self, texts):
        raise EmbeddingError("secret-endpoint https://x.openai.azure.com key=hunter2")


def test_embedding_outage_keeps_the_chapter_ready_and_a_retry_completes_it(client, session_factory, indexing_on, monkeypatch):
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: DownProvider(settings.embedding_dim))
    th, book_id, ch = upload_ready(client, session_factory, words("down"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready"
    assert (row.embedding_status, row.graph_sync_status) == ("failed", "pending")
    assert "hunter2" not in row.index_error and "secret" not in row.index_error
    assert FAKE_STORE.chapter(ch) is None and embedding_rows(session_factory, ch) == []

    good = FakeEmbeddingProvider(settings.embedding_dim)
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: good)
    lines = sync_all(session_factory, allow_fake=True)
    assert not any(line == "!FAILED" for line in lines)
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status, row.index_error) == ("done", "done", None)
    assert FAKE_STORE.chapter(ch) is not None


def test_graph_store_outage_keeps_the_chapter_ready_and_retry_does_not_re_embed(client, session_factory, provider):
    FAKE_STORE.fail_with = RuntimeError("bolt://secret-host:7687 refused")
    th, book_id, ch = upload_ready(client, session_factory, words("graph"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready" and (row.embedding_status, row.graph_sync_status) == ("done", "failed")
    assert "secret-host" not in row.index_error
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"  # students/teacher see no difference

    FAKE_STORE.fail_with = None
    calls = provider.texts_embedded
    sync_all(session_factory, allow_fake=True)
    assert provider.texts_embedded == calls
    row = chapter_row(session_factory, ch)
    assert (row.graph_sync_status, row.index_error) == ("done", None) and FAKE_STORE.chapter(ch) is not None


def test_misconfigured_embeddings_are_recorded_not_raised(client, session_factory, monkeypatch, indexing_on):
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "llm_api_key", "")
    _, _, ch = upload_ready(client, session_factory, words("cfg"))
    row = chapter_row(session_factory, ch)
    assert row.status == "ready" and row.embedding_status == "failed" and "EMBEDDING_MODEL" in row.index_error


def test_with_everything_switched_off_both_stages_are_skipped(client, session_factory):
    _, _, ch = upload_ready(client, session_factory, words("off"))
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("skipped", "skipped")
    assert embedding_rows(session_factory, ch) == []


def test_mark_processing_resets_the_derived_state():
    ch = Chapter(embedding_status="done", graph_sync_status="done", index_error="x")
    mark_processing(ch)
    assert (ch.embedding_status, ch.graph_sync_status, ch.index_error) == ("pending", "pending", None)


# ---- sync_graph ------------------------------------------------------------------------------------

def test_rebuild_restores_the_graph_copy_from_stored_vectors_without_embedding_calls(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("r1"), words("r2"))
    before = FAKE_STORE.chapter(ch)
    FAKE_STORE.clear()
    monkeypatch.setattr("app.pipeline.indexing.get_embedding_provider", lambda: pytest.fail("the embedding service was called"))
    calls = provider.calls
    lines = sync_all(session_factory, rebuild=True, allow_fake=True)
    after = FAKE_STORE.chapter(ch)
    assert provider.calls == calls and after is not None
    assert [c.id for c in after.concepts] == [c.id for c in before.concepts]
    assert all(a.embedding == pytest.approx(b.embedding) for a, b in zip(after.concepts, before.concepts))
    assert all(a.embedding == pytest.approx(b.embedding) for a, b in zip(after.pages, before.pages) if b.embedding)
    assert any("graph store now holds" in line for line in lines)


def test_default_sync_only_touches_chapters_that_need_it(client, session_factory, provider):
    upload_ready(client, session_factory, words("done"))
    with session_factory() as db:
        assert chapters_needing_index(db) == []
    lines = sync_all(session_factory, allow_fake=True)
    assert "0 chapter(s) processed" in "\n".join(lines)


def test_prune_removes_graph_chapters_postgres_no_longer_has_as_ready(client, session_factory, provider):
    _, _, ch = upload_ready(client, session_factory, words("keep"))
    ghost = ChapterGraph(book_id=str(uuid.uuid4()), chapter_id=str(uuid.uuid4()), title="gone", sequence_num=1,
                         is_reference=True, owner_teacher_id=None, embedding_model=None)
    FAKE_STORE.replace_chapter(ghost)
    lines = sync_all(session_factory, prune=True, allow_fake=True)
    assert FAKE_STORE.list_chapter_ids() == {ch} and any("pruned 1" in line for line in lines)


def test_sync_refuses_placeholder_vectors_unless_allowed(session_factory, indexing_on):
    with pytest.raises(SystemExit, match="PLACEHOLDER"):
        sync_all(session_factory)
    sync_all(session_factory, allow_fake=True)


def test_placeholder_vectors_never_reach_a_real_store(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("fk"))
    monkeypatch.setattr(settings, "embedding_provider", "none")  # i.e. a real deployment now
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is None for n in [*payload.pages, *payload.concepts])
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is not None for n in payload.concepts)


def test_vectors_of_the_wrong_size_are_not_indexed(client, session_factory, provider, monkeypatch):
    _, _, ch = upload_ready(client, session_factory, words("dim"))
    monkeypatch.setattr(settings, "embedding_dim", 128)
    with session_factory() as db:
        payload = build_chapter_payload(db, db.get(Chapter, uuid.UUID(ch)))
    assert all(n.embedding is None for n in [*payload.pages, *payload.concepts])


# ---- graph store contract (fake) --------------------------------------------------------------------

def test_smoke_checks_pass_on_the_in_memory_store():
    smoke_memgraph.results.clear()
    made: list[str] = []
    smoke_memgraph.run_store_checks(FakeGraphStore(), 96, made)
    assert smoke_memgraph.results and all(smoke_memgraph.results)


def test_search_only_sees_the_given_books():
    store = FakeGraphStore()
    mine, theirs = str(uuid.uuid4()), str(uuid.uuid4())
    for book, name in ((mine, "mine"), (theirs, "theirs")):
        store.replace_chapter(ChapterGraph(
            book_id=book, chapter_id=str(uuid.uuid4()), title="c", sequence_num=1, is_reference=False, owner_teacher_id=None,
            embedding_model="m", concepts=[ConceptNode(str(uuid.uuid4()), name, "", 0, [1.0, 0.0])],
            pages=[PageNode(str(uuid.uuid4()), 1, [1.0, 0.0])]))
    assert [h.name for h in store.search_concepts([1.0, 0.0], [mine], k=5)] == ["mine"]
    assert store.search_concepts([1.0, 0.0], [], k=5) == [] and store.search_pages([1.0, 0.0], [], k=5) == []
    assert {h.book_id for h in store.search_pages([1.0, 0.0], [mine, theirs], k=5)} == {mine, theirs}


# ---- the Memgraph client against a stub driver --------------------------------------------------------

class StubRecord:
    def __init__(self, row):
        self._row = row

    def data(self):
        return self._row


class StubResult:
    def __init__(self, rows=()):
        self.rows = list(rows)

    def consume(self):
        return None

    def data(self):
        return self.rows

    def __iter__(self):
        return iter(StubRecord(r) for r in self.rows)


class StubDriver:
    """Records every statement; `script(query, params)` returns the rows to answer with (or raises)."""

    def __init__(self, script=None):
        self.log: list[tuple[str, dict]] = []
        self.writes = self.reads = 0
        self.script = script or (lambda q, p: [])
        self.closed = False

    def _run(self, query, **params):
        self.log.append((query, params))
        return StubResult(self.script(query, params))

    def session(self):
        driver = self

        class Session:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def run(self, statement, **params):
                return driver._run(statement, **params)

            def execute_write(self, fn):
                driver.writes += 1
                return fn(type("Tx", (), {"run": staticmethod(driver._run)}))

            def execute_read(self, fn):
                driver.reads += 1
                return fn(type("Tx", (), {"run": staticmethod(driver._run)}))

        return Session()

    def close(self):
        self.closed = True


def store_with(driver, **kw):
    return MemgraphStore("bolt://x", dim=4, driver=driver, **kw)


def sample_graph(n_concepts=3):
    concepts = [ConceptNode(str(uuid.uuid4()), f"c{i}", "d", i, [0.1] * 4) for i in range(n_concepts)]
    pages = [PageNode(str(uuid.uuid4()), 1, [0.2] * 4), PageNode(str(uuid.uuid4()), 2, None)]
    return ChapterGraph(
        book_id="B", chapter_id="CH", title="T", sequence_num=2, is_reference=True, owner_teacher_id=None, embedding_model="m",
        pages=pages, concepts=concepts, edges=[EdgeRow(concepts[1].id, concepts[0].id, "llm")],
        concept_pages=[(concepts[0].id, pages[0].id)],
    )


def test_ensure_schema_creates_label_and_vector_indexes_once():
    d = StubDriver()
    s = store_with(d, capacity=500, metric="cos")
    s.ensure_schema()
    s.ensure_schema()
    statements = [q for q, _ in d.log]
    assert sum(q.startswith("CREATE INDEX ON") for q in statements) == 5
    vector = [q for q in statements if q.startswith("CREATE VECTOR INDEX")]
    assert len(vector) == 2 and CONCEPT_INDEX in vector[0] and PAGE_INDEX in vector[1]
    assert '"dimension": 4' in vector[0] and '"capacity": 500' in vector[0] and '"metric": "cos"' in vector[0]
    assert statements.count("SHOW VECTOR INDEX INFO") == 1  # second call was a no-op


def test_ensure_schema_tolerates_existing_indexes_and_rejects_a_dimension_change():
    def exists(q, p):
        if q.startswith("CREATE"):
            raise RuntimeError("Index already exists")
        return [{"index_name": CONCEPT_INDEX, "dimension": 4}, {"index_name": PAGE_INDEX, "dimension": 4}]

    store_with(StubDriver(exists)).ensure_schema()

    def wrong(q, p):
        return [{"index_name": CONCEPT_INDEX, "dimension": 1536}] if q.startswith("SHOW") else []

    with pytest.raises(GraphStoreError, match="--rebuild"):
        store_with(StubDriver(wrong)).ensure_schema()


def test_replace_chapter_is_one_idempotent_transaction_with_no_page_text():
    d = StubDriver()
    s = store_with(d, batch=2)
    s.replace_chapter(sample_graph(5))
    assert d.writes == 1  # one transaction
    work = [(q, p) for q, p in d.log if not q.startswith(("CREATE INDEX", "CREATE VECTOR", "SHOW"))]
    assert all("DETACH DELETE" in q for q, _ in work[:3])  # starts by removing the chapter's old copy
    concept_batches = [p["rows"] for q, p in work if q.startswith("UNWIND $rows AS r CREATE (:Concept")]
    assert [len(b) for b in concept_batches] == [2, 2, 1]  # batched
    assert any("REQUIRES" in q for q, _ in work) and any("EXPLAINED_ON" in q for q, _ in work)
    page_rows = next(p["rows"] for q, p in work if ":Page {id: r.id" in q)
    assert page_rows[1]["embedding"] is None  # a page without a vector is still written
    assert "content_text" not in repr(d.log)


def test_every_search_is_filtered_by_book_and_widens_until_it_has_enough():
    seen = []

    def script(q, p):
        seen.append(p["limit"])
        return [] if p["limit"] < 500 else [{"id": "i", "name": "n", "description": None, "chapter_id": "c", "book_id": "B", "similarity": 0.9}]

    d = StubDriver(script)
    s = store_with(d, max_candidates=2000)
    hits = s.search_concepts([0.1] * 4, ["B", "B"], k=1)
    assert [h.name for h in hits] == [("n")] and hits[0].description == ""
    assert seen == [20, 80, 320, 1280]  # widened x4 until the window held one of this book's concepts
    query, params = d.log[0]
    assert "MATCH (node:Concept) WHERE id(node) = gid AND node.book_id IN $book_ids RETURN" in query  # the whole clause, nothing OR-ed in
    assert "node.book_id" not in query.split("MATCH (node:Concept)")[0]  # no property read on a raw hit (it may be a deleted node)
    assert params["book_ids"] == ["B"]
    d.log.clear()
    assert s.search_concepts([0.1] * 4, [], k=3) == [] and s.search_pages([0.1] * 4, [], k=3) == [] and d.log == []


def test_search_gives_up_at_the_ceiling():
    seen = []
    s = store_with(StubDriver(lambda q, p: seen.append(p["limit"]) or []), max_candidates=100)
    assert s.search_pages([0.1] * 4, ["B"], k=2) == [] and seen == [20, 80, 100]


def test_prerequisite_query_is_book_filtered_and_depth_is_bounded():
    d = StubDriver(lambda q, p: [{"id": "p", "name": "P", "depth": 1}])
    rows = store_with(d).prerequisites("c1", ["B"], max_depth=99)
    assert [(r.name, r.depth) for r in rows] == [("P", 1)]
    assert "c.book_id IN $book_ids" in d.log[0][0] and "*1..20" in d.log[0][0]
    assert store_with(StubDriver()).prerequisites("c1", []) == []


def test_driver_failures_become_graph_store_errors():
    def boom(q, p):
        raise ConnectionRefusedError("refused")

    with pytest.raises(GraphStoreError):
        store_with(StubDriver(boom)).replace_chapter(sample_graph())
    with pytest.raises(GraphStoreError):
        store_with(StubDriver(boom)).list_chapter_ids()


def test_unsafe_store_settings_are_rejected():
    with pytest.raises(ValueError):
        MemgraphStore("bolt://x", dim=4, metric='cos"} DROP')
    with pytest.raises(ValueError):
        MemgraphStore("bolt://x", dim=0)


# ---- providers and factories ---------------------------------------------------------------------------

class StubEmbeddingsClient:
    def __init__(self, dim=4, drop=0, fail=False):
        self.dim, self.drop, self.fail, self.calls = dim, drop, fail, []
        self.embeddings = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("401 key=hunter2")
        data = [type("D", (), {"index": i, "embedding": [float(i)] * self.dim}) for i in reversed(range(len(kwargs["input"]) - self.drop))]
        return type("R", (), {"data": data})


def test_openai_compat_embeddings_batch_keep_order_and_validate():
    client = StubEmbeddingsClient()
    p = OpenAICompatEmbeddingProvider("", "k", "dep", 4, batch_size=2, client=client)
    vectors = p.embed(["a", "b", "c", "d", "e"])
    assert [len(c["input"]) for c in client.calls] == [2, 2, 1] and all("dimensions" not in c for c in client.calls)
    assert vectors[0] == [0.0] * 4 and vectors[1] == [1.0] * 4  # sorted back into request order within a batch
    with_dims = StubEmbeddingsClient()
    OpenAICompatEmbeddingProvider("", "k", "dep", 4, send_dimensions=True, client=with_dims).embed(["a"])
    assert with_dims.calls[0]["dimensions"] == 4
    with pytest.raises(EmbeddingError, match="EMBEDDING_DIM"):
        OpenAICompatEmbeddingProvider("", "k", "dep", 8, client=StubEmbeddingsClient(dim=4)).embed(["a"])
    with pytest.raises(EmbeddingError, match="got 1"):
        OpenAICompatEmbeddingProvider("", "k", "dep", 4, client=StubEmbeddingsClient(drop=1)).embed(["a", "b"])
    with pytest.raises(EmbeddingError) as err:
        OpenAICompatEmbeddingProvider("", "k", "dep", 4, client=StubEmbeddingsClient(fail=True)).embed(["a"])
    assert "hunter2" not in str(err.value)


def test_embedding_provider_factory(monkeypatch):
    assert get_embedding_provider() is None  # "none" is the default under tests
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    assert get_embedding_provider().model_name == FAKE_EMBEDDING_MODEL
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embedding_api_key", "")
    monkeypatch.setattr(settings, "llm_api_key", "")
    with pytest.raises(RuntimeError, match="EMBEDDING_MODEL"):
        get_embedding_provider()
    captured = {}

    class Capture:
        def __init__(self, base_url, api_key, model, dim, **kw):
            captured.update(base_url=base_url, api_key=api_key, model=model, dim=dim)

    monkeypatch.setattr("app.embeddings.openai_compat_provider.OpenAICompatEmbeddingProvider", Capture)
    monkeypatch.setattr(settings, "embedding_base_url", "")  # a real .env may set EMBEDDING_BASE_URL; test the blank fallback
    monkeypatch.setattr(settings, "llm_api_key", "llm-key")
    monkeypatch.setattr(settings, "llm_base_url", "https://res.openai.azure.com/openai/v1/")
    monkeypatch.setattr(settings, "embedding_model", "emb-deployment")
    get_embedding_provider()  # blank EMBEDDING_* falls back to the LLM resource
    assert captured == {"base_url": "https://res.openai.azure.com/openai/v1/", "api_key": "llm-key", "model": "emb-deployment", "dim": settings.embedding_dim}


def test_graph_store_factory(monkeypatch):
    assert get_graph_store() is None
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    assert get_graph_store() is FAKE_STORE
    monkeypatch.setattr(settings, "graph_store_provider", "memgraph")
    first = get_graph_store()
    assert isinstance(first, MemgraphStore) and get_graph_store() is first and first.dim == settings.embedding_dim


def test_stages_skipped_while_switched_off_are_done_once_switched_on(client, session_factory, monkeypatch, indexing_on):
    monkeypatch.setattr(settings, "embedding_provider", "none")
    monkeypatch.setattr(settings, "graph_store_provider", "none")
    _, _, ch = upload_ready(client, session_factory, words("late"))
    assert (chapter_row(session_factory, ch).embedding_status, chapter_row(session_factory, ch).graph_sync_status) == ("skipped", "skipped")
    with session_factory() as db:
        assert chapters_needing_index(db) == []  # nothing to do while both stay off
    monkeypatch.setattr(settings, "embedding_provider", "fake")
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    sync_all(session_factory, allow_fake=True)
    row = chapter_row(session_factory, ch)
    assert (row.embedding_status, row.graph_sync_status) == ("done", "done") and FAKE_STORE.chapter(ch) is not None