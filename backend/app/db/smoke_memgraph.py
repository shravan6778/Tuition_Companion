"""Check a running Memgraph with the app's OWN store code: connect, create the real indexes, write chapters,
vector-search with the tenant (book) filter, walk prerequisites, replace/delete, clean up.

    docker compose up -d memgraph
    python -m app.db.smoke_memgraph                       # uses MEMGRAPH_* / EMBEDDING_DIM from backend/.env
    python -m app.db.smoke_memgraph --uri bolt://localhost:7687 --keep

It only touches nodes it creates itself (random ids) and removes them at the end, unless --keep is given. The
indexes it creates are the app's real ones (concept_embedding_idx, page_embedding_idx) and stay in place.
Send the whole output back, including any FAIL line. Exit code 0 only when every check passed.
"""
import argparse
import sys
import time
import uuid

import numpy as np

from app.core.config import settings
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, PageNode
from app.graph_store.memgraph_store import CONCEPT_INDEX, PAGE_INDEX, MemgraphStore

results: list[bool] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    results.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -> {detail}" if detail else ""))
    return bool(ok)


def unit(rng, dim: int) -> np.ndarray:
    v = rng.normal(size=dim)
    return v / np.linalg.norm(v)


def near(base: np.ndarray, rng, noise: float) -> list[float]:
    v = base + rng.normal(size=base.shape) * noise / np.sqrt(base.shape[0])
    return (v / np.linalg.norm(v)).tolist()


def chapter(book_id, concepts: list[tuple[str, list[float]]], pages: list[list[float]], edges: list[tuple[int, int]]) -> ChapterGraph:
    chapter_id = str(uuid.uuid4())
    page_nodes = [PageNode(str(uuid.uuid4()), i + 1, vec) for i, vec in enumerate(pages)]
    nodes = [ConceptNode(str(uuid.uuid4()), name, f"About {name}", i, vec) for i, (name, vec) in enumerate(concepts)]
    return ChapterGraph(
        book_id=str(book_id), chapter_id=chapter_id, title="Smoke test chapter", sequence_num=1, is_reference=False,
        owner_teacher_id=str(uuid.uuid4()), embedding_model="smoke-test", pages=page_nodes, concepts=nodes,
        edges=[EdgeRow(nodes[c].id, nodes[p].id, "llm") for c, p in edges],
        concept_pages=[(n.id, page_nodes[0].id) for n in nodes],
    )


def run_store_checks(store, dim: int, made: list[str]) -> None:
    """The checks that need only the GraphStore interface (so tests can run them on the in-memory fake too).
    Chapter ids it creates are appended to `made` so the caller can clean up."""
    rng = np.random.default_rng(11)
    topic = unit(rng, dim)      # what the "student" asks about
    other = unit(rng, dim)      # unrelated content
    book_a, book_b = uuid.uuid4(), uuid.uuid4()
    query = near(topic, rng, 0.05)

    # Book A: the student's book. Book B: someone else's, with content EVEN CLOSER to the question.
    a = chapter(book_a,
                [("Cell", near(topic, rng, 0.3)), ("Cell membrane", near(topic, rng, 0.35)), ("Osmosis", near(topic, rng, 0.4)),
                 ("Photosynthesis", near(other, rng, 0.1))],
                pages=[near(topic, rng, 0.3), near(other, rng, 0.1)],
                edges=[(1, 0), (2, 1)])  # membrane needs cell; osmosis needs membrane
    b = chapter(book_b, [("Other book's cell", near(topic, rng, 0.02))] + [(f"Filler {i}", near(topic, rng, 0.05)) for i in range(40)],
                pages=[near(topic, rng, 0.02)], edges=[])
    made += [a.chapter_id, b.chapter_id]
    try:
        store.replace_chapter(a)
        store.replace_chapter(b)
        check("write two chapters (one transaction each)", True)
    except Exception as exc:
        check("write two chapters", False, str(exc))
        return

    s = store.stats()
    check("stats count what was written", s["Concept"] >= len(a.concepts) + len(b.concepts) and s["REQUIRES"] >= 2, str(s))

    hits = store.search_concepts(query, [str(book_a)], k=3)
    check("search finds the student's own concepts", bool(hits) and hits[0].name == "Cell", str([(h.name, round(h.similarity, 3)) for h in hits]))
    check("search NEVER returns another book's content", all(h.book_id == str(book_a) for h in hits) and bool(hits))
    check("search stays correct when other books dominate the nearest 20",
          len(hits) == 3, f"got {len(hits)} of 3 (40 closer concepts belong to the other book)")
    both = store.search_concepts(query, [str(book_a), str(book_b)], k=1)
    check("search over both books returns the nearer one", bool(both) and both[0].book_id == str(book_b))
    check("empty book list returns nothing", store.search_concepts(query, [], k=3) == [])
    pages = store.search_pages(query, [str(book_a)], k=2)
    check("page search is filtered the same way", bool(pages) and all(p.book_id == str(book_a) for p in pages) and pages[0].page_number == 1,
          str([(p.page_number, round(p.similarity, 3)) for p in pages]))

    osmosis = next(c for c in a.concepts if c.name == "Osmosis")
    prereqs = store.prerequisites(osmosis.id, [str(book_a)])
    check("prerequisites come back nearest first", [(p.name, p.depth) for p in prereqs] == [("Cell membrane", 1), ("Cell", 2)],
          str([(p.name, p.depth) for p in prereqs]))
    check("prerequisites respect the book filter", store.prerequisites(osmosis.id, [str(book_b)]) == [])

    before = store.stats()
    store.replace_chapter(a)
    check("writing the same chapter again changes nothing", store.stats() == before, f"{before} -> {store.stats()}")

    ids = store.list_chapter_ids()
    check("chapters are listed", a.chapter_id in ids and b.chapter_id in ids)
    store.delete_chapter(b.chapter_id)
    made.remove(b.chapter_id)
    time.sleep(0.5)
    check("delete removes a chapter completely", b.chapter_id not in store.list_chapter_ids()
          and store.search_concepts(query, [str(book_b)], k=1) == [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uri", default=settings.memgraph_uri)
    ap.add_argument("--keep", action="store_true", help="leave the test chapters in Memgraph")
    args = ap.parse_args()
    dim = settings.embedding_dim
    print(f"target {args.uri}; vector dimension {dim} (EMBEDDING_DIM); metric {settings.memgraph_vector_metric}")

    store = MemgraphStore(
        args.uri, settings.memgraph_user, settings.memgraph_password, dim=dim,
        capacity=settings.memgraph_vector_capacity, metric=settings.memgraph_vector_metric,
        batch=settings.graph_sync_batch, max_candidates=settings.graph_search_max_candidates,
    )
    made: list[str] = []
    try:
        try:
            store.driver.verify_connectivity()
            check("connect over Bolt", True)
        except Exception as exc:
            check("connect over Bolt", False, repr(exc))
            print("Is the container running?  docker compose ps   (and is MEMGRAPH_URI right?)")
            return 1

        try:
            rows = store.run_admin("SHOW VERSION")
            check("server version", True, str(list(rows[0].values())) if rows else "no rows")
        except Exception as exc:
            check("server version", False, str(exc))

        try:
            store.ensure_schema()
            check("create indexes (label + vector)", True)
        except Exception as exc:
            check("create indexes (label + vector)", False, str(exc))
            print("Vector indexes failed. If this is an older Memgraph, the message above says whether a feature flag "
                  "is needed; otherwise send it to me and we will pin another tag.")
            return 1
        try:
            info = store.run_admin("SHOW VECTOR INDEX INFO")
            names = [str(r.get("index_name") or r.get("name")) for r in info]
            check("both vector indexes exist", CONCEPT_INDEX in names and PAGE_INDEX in names, str(info))
        except Exception as exc:
            check("SHOW VECTOR INDEX INFO", False, str(exc))

        run_store_checks(store, dim, made)
    finally:
        if args.keep:
            print("--keep given: test chapters left in Memgraph:", made)
        else:
            for chapter_id in made:
                try:
                    store.delete_chapter(chapter_id)
                except Exception as exc:
                    print("cleanup failed for", chapter_id, exc)
            if made:
                print("cleaned up the test chapters")
        store.close()

    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())