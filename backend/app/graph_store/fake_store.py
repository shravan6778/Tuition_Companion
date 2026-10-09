import threading
from collections import deque
from typing import Sequence

from app.embeddings.vectors import cosine
from app.graph_store.base import (
    ChapterGraph, ConceptHit, GraphStoreError, PageHit, PrerequisiteRow,
)


class FakeGraphStore:
    """In-memory store with the same behaviour as the Memgraph one (replace-per-chapter, tenant-filtered
    search), for tests and for running the pipeline without Docker. Process-wide singleton: see factory."""

    def __init__(self):
        self._chapters: dict[str, ChapterGraph] = {}
        self._cross: dict[str, list] = {}  # book id -> cross-chapter EdgeRows
        self._lock = threading.Lock()
        self.fail_with: Exception | None = None  # tests set this to simulate an outage
        self.replace_calls = 0

    def _check(self):
        if self.fail_with is not None:
            raise GraphStoreError("simulated graph store outage") from self.fail_with

    def ensure_schema(self) -> None:
        self._check()

    def replace_chapter(self, graph: ChapterGraph) -> None:
        self._check()
        with self._lock:
            self.replace_calls += 1
            self._chapters[graph.chapter_id] = graph

    def replace_cross_edges(self, book_id: str, edges) -> None:
        self._check()
        with self._lock:
            self._cross[book_id] = list(edges)

    def cross_edges(self, book_id: str) -> list:  # test helper
        return list(self._cross.get(book_id, []))

    def delete_chapter(self, chapter_id: str) -> None:
        self._check()
        with self._lock:
            self._chapters.pop(chapter_id, None)

    def list_chapter_ids(self) -> set[str]:
        self._check()
        return set(self._chapters)

    def clear(self) -> None:
        self._check()
        with self._lock:
            self._chapters.clear()
            self._cross.clear()

    def chapter(self, chapter_id: str) -> ChapterGraph | None:  # test helper
        return self._chapters.get(chapter_id)

    def search_concepts(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[ConceptHit]:
        self._check()
        allowed = set(book_ids)
        hits = [
            ConceptHit(c.id, c.name, c.description, g.chapter_id, g.book_id, cosine(vector, c.embedding))
            for g in self._chapters.values() if g.book_id in allowed
            for c in g.concepts if c.embedding is not None
        ]
        return sorted(hits, key=lambda h: -h.similarity)[:k]

    def search_pages(self, vector: Sequence[float], book_ids: Sequence[str], k: int = 5) -> list[PageHit]:
        self._check()
        allowed = set(book_ids)
        hits = [
            PageHit(p.id, p.page_number, g.chapter_id, g.book_id, cosine(vector, p.embedding))
            for g in self._chapters.values() if g.book_id in allowed
            for p in g.pages if p.embedding is not None
        ]
        return sorted(hits, key=lambda h: -h.similarity)[:k]

    def prerequisites(self, concept_id: str, book_ids: Sequence[str], max_depth: int = 5) -> list[PrerequisiteRow]:
        self._check()
        allowed = set(book_ids)
        for g in self._chapters.values():
            if g.book_id not in allowed or concept_id not in {c.id for c in g.concepts}:
                continue
            names = {c.id: c.name for other in self._chapters.values() if other.book_id == g.book_id for c in other.concepts}
            needs: dict[str, list[str]] = {}
            for e in [*g.edges, *self._cross.get(g.book_id, [])]:
                needs.setdefault(e.concept_id, []).append(e.prerequisite_id)
            depth_of: dict[str, int] = {}
            queue = deque([(concept_id, 0)])
            while queue:
                node, depth = queue.popleft()
                if depth >= max_depth:
                    continue
                for prerequisite in needs.get(node, []):
                    if prerequisite not in depth_of and prerequisite != concept_id:
                        depth_of[prerequisite] = depth + 1
                        queue.append((prerequisite, depth + 1))
            rows = [PrerequisiteRow(i, names[i], d) for i, d in depth_of.items()]
            return sorted(rows, key=lambda r: (r.depth, r.name))
        return []

    def stats(self) -> dict:
        self._check()
        graphs = list(self._chapters.values())
        return {
            "Chapter": len(graphs),
            "Page": sum(len(g.pages) for g in graphs),
            "Concept": sum(len(g.concepts) for g in graphs),
            "REQUIRES": sum(len(g.edges) for g in graphs) + sum(len(v) for v in self._cross.values()),
        }

    def close(self) -> None:
        pass
