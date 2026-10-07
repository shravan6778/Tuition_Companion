"""Memgraph implementation of the GraphStore (Bolt, via the `neo4j` driver).

Graph written per chapter:

    (:Chapter {id, book_id, title, sequence_num, is_reference, owner_teacher_id})
    (:Page    {id, chapter_id, book_id, page_number, embedding, embedding_model})
    (:Concept {id, chapter_id, book_id, name, description, position, embedding, embedding_model})
    (Concept)-[:REQUIRES {source}]->(Concept)   # "needs this first": the prerequisite graph, a DAG
    (Concept)-[:EXPLAINED_ON]->(Page)           # every page the concept is on
    (Page)-[:IN_CHAPTER]->(Chapter), (Concept)-[:IN_CHAPTER]->(Chapter)

Vector indexes: concept_embedding_idx on :Concept(embedding) and page_embedding_idx on :Page(embedding).
Nothing here is the source of truth: `python -m app.db.sync_graph --rebuild` recreates all of it from PostgreSQL.
"""
import logging
import re
import time
from contextlib import contextmanager
from typing import Iterable, Optional, Sequence

from neo4j import GraphDatabase

from app.graph_store.base import (
    ChapterGraph, ConceptHit, GraphStoreError, PageHit, PrerequisiteRow,
)

logger = logging.getLogger(__name__)

CONCEPT_INDEX = "concept_embedding_idx"
PAGE_INDEX = "page_embedding_idx"
LABEL_INDEXES = (("Chapter", "id"), ("Page", "id"), ("Page", "chapter_id"), ("Concept", "id"), ("Concept", "chapter_id"))
_SAFE_WORD = re.compile(r"^[a-z0-9_]+$")


def _chunks(rows: list, size: int) -> Iterable[list]:
    for start in range(0, len(rows), max(1, size)):
        yield rows[start:start + size]


class MemgraphStore:
    def __init__(self, uri: str, user: str = "", password: str = "", *, dim: int, capacity: int = 20000,
                 metric: str = "cos", batch: int = 200, max_candidates: int = 2000, driver=None):
        if not isinstance(dim, int) or dim <= 0:
            raise ValueError("dim must be a positive integer")
        if not _SAFE_WORD.match(metric):
            raise ValueError("unsupported vector metric")
        self.dim, self.capacity, self.metric = dim, int(capacity), metric
        self._batch, self._max_candidates = batch, max_candidates
        self._uri, self._auth = uri, ((user, password) if user else None)
        self._driver = driver  # tests inject a stub; otherwise created on first use
        self._schema_ready = False

    # ---- plumbing -----------------------------------------------------------------------------
    @property
    def driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self._uri, auth=self._auth, connection_timeout=10, max_transaction_retry_time=10,
            )
        return self._driver

    @contextmanager
    def _guard(self, what: str):
        try:
            yield
        except GraphStoreError:
            raise
        except Exception as exc:  # connection refused, auth, syntax on an old server, ...
            logger.exception("Memgraph: %s failed", what)
            raise GraphStoreError(f"Memgraph {what} failed: {type(exc).__name__}: {str(exc)[:200]}") from exc

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None
            self._schema_ready = False

    def _read(self, query: str, **params) -> list[dict]:
        def work(tx):
            return [record.data() for record in tx.run(query, **params)]

        with self.driver.session() as session:
            return session.execute_read(work)

    def run_admin(self, statement: str) -> list[dict]:
        """Run a SHOW ... / admin statement in an auto-commit session. Memgraph refuses these inside the explicit
        transaction that session.execute_read opens, which is why `_read("SHOW VERSION")` raised ClientError."""
        with self.driver.session() as session:
            return session.run(statement).data()

    # ---- schema -------------------------------------------------------------------------------
    @staticmethod
    def _ddl(session, statement: str) -> None:
        try:
            session.run(statement).consume()
        except Exception as exc:
            if "already exist" in str(exc).lower():  # idempotent: the index is there
                return
            raise

    def ensure_schema(self) -> None:
        if self._schema_ready:
            return
        with self._guard("schema setup"):
            with self.driver.session() as session:
                for label, prop in LABEL_INDEXES:
                    self._ddl(session, f"CREATE INDEX ON :{label}({prop})")
                for name, label in ((CONCEPT_INDEX, "Concept"), (PAGE_INDEX, "Page")):
                    self._ddl(
                        session,
                        f"CREATE VECTOR INDEX {name} ON :{label}(embedding) WITH CONFIG "
                        f'{{"dimension": {self.dim}, "capacity": {self.capacity}, "metric": "{self.metric}"}}',
                    )
                self._check_dimensions(session)
        self._schema_ready = True

    def _check_dimensions(self, session) -> None:
        try:
            rows = session.run("SHOW VECTOR INDEX INFO").data()
        except Exception:  # an older/odd server: creation above already proved vector indexes exist
            logger.warning("Memgraph: could not read SHOW VECTOR INDEX INFO; skipping the dimension check")
            return
        for row in rows:
            name = row.get("index_name") or row.get("name")
            found = row.get("dimension")
            if name in (CONCEPT_INDEX, PAGE_INDEX) and found is not None and int(found) != self.dim:
                raise GraphStoreError(
                    f"Memgraph index {name} has dimension {found} but EMBEDDING_DIM is {self.dim}. Drop the "
                    f"vector indexes (DROP VECTOR INDEX {name}) and run `python -m app.db.sync_graph --rebuild`."
                )

    # ---- writing ------------------------------------------------------------------------------
    def replace_chapter(self, graph: ChapterGraph) -> None:
        self.ensure_schema()
        cid, bid, model = graph.chapter_id, graph.book_id, graph.embedding_model
        page_rows = [{"id": p.id, "page_number": p.page_number, "embedding": p.embedding} for p in graph.pages]
        concept_rows = [
            {"id": c.id, "name": c.name, "description": c.description, "position": c.position, "embedding": c.embedding}
            for c in graph.concepts
        ]
        edge_rows = [{"concept_id": e.concept_id, "prerequisite_id": e.prerequisite_id, "source": e.source} for e in graph.edges]
        link_rows = [{"concept_id": c, "page_id": p} for c, p in graph.concept_pages]

        def work(tx):  # one transaction; safe to run again (it starts by deleting the chapter's old copy)
            tx.run("MATCH (n:Concept {chapter_id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run("MATCH (n:Page {chapter_id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run("MATCH (n:Chapter {id: $cid}) DETACH DELETE n", cid=cid).consume()
            tx.run(
                "CREATE (:Chapter {id: $cid, book_id: $bid, title: $title, sequence_num: $seq, "
                "is_reference: $is_reference, owner_teacher_id: $owner})",
                cid=cid, bid=bid, title=graph.title, seq=graph.sequence_num,
                is_reference=graph.is_reference, owner=graph.owner_teacher_id,
            ).consume()
            for batch in _chunks(page_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS r CREATE (:Page {id: r.id, chapter_id: $cid, book_id: $bid, "
                    "page_number: r.page_number, embedding: r.embedding, embedding_model: $model})",
                    rows=batch, cid=cid, bid=bid, model=model,
                ).consume()
            for batch in _chunks(concept_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS r CREATE (:Concept {id: r.id, chapter_id: $cid, book_id: $bid, name: r.name, "
                    "description: r.description, position: r.position, embedding: r.embedding, embedding_model: $model})",
                    rows=batch, cid=cid, bid=bid, model=model,
                ).consume()
            tx.run("MATCH (ch:Chapter {id: $cid}) MATCH (p:Page {chapter_id: $cid}) CREATE (p)-[:IN_CHAPTER]->(ch)", cid=cid).consume()
            tx.run("MATCH (ch:Chapter {id: $cid}) MATCH (c:Concept {chapter_id: $cid}) CREATE (c)-[:IN_CHAPTER]->(ch)", cid=cid).consume()
            for batch in _chunks(edge_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS e MATCH (c:Concept {id: e.concept_id}), (p:Concept {id: e.prerequisite_id}) "
                    "CREATE (c)-[:REQUIRES {source: e.source}]->(p)",
                    rows=batch,
                ).consume()
            for batch in _chunks(link_rows, self._batch):
                tx.run(
                    "UNWIND $rows AS l MATCH (c:Concept {id: l.concept_id}), (p:Page {id: l.page_id}) "
                    "CREATE (c)-[:EXPLAINED_ON]->(p)",
                    rows=batch,
                ).consume()

        with self._guard("chapter write"):
            with self.driver.session() as session:
                session.execute_write(work)

    def delete_chapter(self, chapter_id: str) -> None:
        def work(tx):
            tx.run("MATCH (n:Concept {chapter_id: $cid}) DETACH DELETE n", cid=chapter_id).consume()
            tx.run("MATCH (n:Page {chapter_id: $cid}) DETACH DELETE n", cid=chapter_id).consume()
            tx.run("MATCH (n:Chapter {id: $cid}) DETACH DELETE n", cid=chapter_id).consume()

        with self._guard("chapter delete"):
            with self.driver.session() as session:
                session.execute_write(work)

    def list_chapter_ids(self) -> set[str]:
        with self._guard("chapter listing"):
            return {row["id"] for row in self._read("MATCH (c:Chapter) RETURN c.id AS id")}

    def clear(self) -> None:
        def work(tx):
            for label in ("Concept", "Page", "Chapter"):
                tx.run(f"MATCH (n:{label}) DETACH DELETE n").consume()

        with self._guard("clear"):
            with self.driver.session() as session:
                session.execute_write(work)

    # ---- reading (tenant-filtered) ------------------------------------------------------------
    def _vector_search(self, index: str, label: str, vector: Sequence[float], book_ids: Sequence[str], k: int, returns: str) -> list[dict]:
        """Memgraph's vector search is global, so the book filter is applied to its hits. When most of the
        index belongs to other books the first window can hold fewer than k of ours: widen it (x4) up to the
        configured ceiling instead of silently returning too little.

        Deleted nodes linger in the vector index until Memgraph's garbage collector runs (default every 30 s),
        and reading ANY property of such a hit raises "Trying to get a property from a deleted object". So the
        hits are reduced to their internal id first (id() touches no storage) and the live nodes are re-matched
        by that id: a deleted node simply fails to match and drops out."""
        wanted = list(dict.fromkeys(str(b) for b in book_ids))
        if not wanted or k <= 0:
            return []
        query = (
            f'CALL vector_search.search("{index}", $limit, $vector) YIELD node AS hit, similarity '
            f"WITH id(hit) AS gid, similarity "
            f"MATCH (node:{label}) WHERE id(node) = gid AND node.book_id IN $book_ids "
            f"RETURN {returns}, similarity ORDER BY similarity DESC LIMIT $k"
        )
        ceiling = max(self._max_candidates, k)
        vec = [float(x) for x in vector]

        with self._guard("vector search"):
            retries = 5
            limit = min(max(k * 5, 20), ceiling)
            while True:
                try:
                    rows = self._read(query, limit=limit, vector=vec, book_ids=wanted, k=k)
                except Exception as exc:
                    # Safety net only: if some server build still trips over a not-yet-collected node, wait for GC.
                    if "deleted" in f"{exc} {exc!r}".lower() and retries > 0:
                        retries -= 1
                        time.sleep(1.0)
                        continue
                    raise
                if len(rows) >= k or limit >= ceiling:
                    return rows
                limit = min(limit * 4, ceiling)

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]:
        rows = self._vector_search(
            CONCEPT_INDEX, "Concept", vector, book_ids, k,
            "node.id AS id, node.name AS name, node.description AS description, "
            "node.chapter_id AS chapter_id, node.book_id AS book_id",
        )
        return [ConceptHit(r["id"], r["name"], r["description"] or "", r["chapter_id"], r["book_id"], r["similarity"]) for r in rows]

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]:
        rows = self._vector_search(
            PAGE_INDEX, "Page", vector, book_ids, k,
            "node.id AS id, node.page_number AS page_number, node.chapter_id AS chapter_id, node.book_id AS book_id",
        )
        return [PageHit(r["id"], r["page_number"], r["chapter_id"], r["book_id"], r["similarity"]) for r in rows]

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        wanted = list(dict.fromkeys(str(b) for b in book_ids))
        if not wanted:
            return []
        depth = max(1, min(int(max_depth), 20))
        query = (
            "MATCH (c:Concept {id: $id}) WHERE c.book_id IN $book_ids "
            f"MATCH (c)-[rels:REQUIRES*1..{depth}]->(p:Concept) "
            "RETURN p.id AS id, p.name AS name, min(size(rels)) AS depth ORDER BY depth, name"
        )
        with self._guard("prerequisite lookup"):
            rows = self._read(query, id=str(concept_id), book_ids=wanted)
        return [PrerequisiteRow(r["id"], r["name"], int(r["depth"])) for r in rows]

    def stats(self) -> dict:
        with self._guard("stats"):
            out = {"Chapter": 0, "Page": 0, "Concept": 0, "REQUIRES": 0}
            for row in self._read("MATCH (n) WHERE n:Chapter OR n:Page OR n:Concept RETURN labels(n)[0] AS label, count(n) AS n"):
                out[row["label"]] = row["n"]
            rows = self._read("MATCH (:Concept)-[r:REQUIRES]->(:Concept) RETURN count(r) AS n")
            out["REQUIRES"] = rows[0]["n"] if rows else 0
            return out