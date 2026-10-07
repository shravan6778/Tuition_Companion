"""Create embeddings and (re)build the graph-store copy from PostgreSQL.

    python -m app.db.sync_graph                  # every ready chapter whose embeddings/graph copy is pending or failed
    python -m app.db.sync_graph --book <id>      # only that book's chapters
    python -m app.db.sync_graph --chapter <id>   # one chapter, whatever its state
    python -m app.db.sync_graph --status         # just print the counts
    python -m app.db.sync_graph --rebuild        # wipe the graph-store copy and write EVERY ready chapter again from
                                                 # PostgreSQL, using the stored vectors: NO embedding calls
    python -m app.db.sync_graph --prune          # remove graph-store chapters that PostgreSQL no longer has as ready

Use it after switching on embeddings / Memgraph (it fills in chapters processed before), after a Memgraph outage
(failed chapters are retried), or after wiping the Memgraph volume (--rebuild). PostgreSQL stays the source of truth:
nothing here changes pages, concepts or the concept graph.
"""
import argparse
import sys
import uuid
from collections import Counter

from sqlalchemy import select

from app.core.config import refuse_fake_embeddings, settings
from app.db.session import SessionLocal
from app.graph_store import get_graph_store
from app.models import Book, Chapter, ChapterStatus
from app.pipeline.indexing import IndexReport, chapters_needing_index, index_chapter


def status_lines(db) -> list[str]:
    counts = Counter()
    for c in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY)):
        counts[(c.embedding_status, c.graph_sync_status)] += 1
    lines = [
        f"embeddings provider: {settings.embedding_provider}   graph store: {settings.graph_store_provider}",
        f"ready chapters: {sum(counts.values())}",
    ]
    lines += [f"  embeddings={e:8} graph={g:8} chapters={n}" for (e, g), n in sorted(counts.items())]
    return lines


def _describe(db, chapter_id, report: IndexReport) -> str:
    chapter = db.get(Chapter, chapter_id)
    book = db.get(Book, chapter.book_id)
    head = f"{'ok    ' if not report.errors else 'FAILED'} {book.publisher or ''} {book.class_name or ''} {book.subject or ''}: {chapter.title}"
    parts = []
    if report.embedding:
        parts.append(f"embeddings {report.embedding} (new {report.embedded}, reused {report.reused}, kept {report.kept}, removed {report.removed})")
    if report.graph == "done":
        parts.append(f"graph done ({report.graph_concepts} concepts, {report.graph_edges} edges, {report.graph_pages} pages"
                     + (f", {report.without_vectors} without vectors" if report.without_vectors else "") + ")")
    elif report.graph:
        parts.append(f"graph {report.graph}")
    line = f"{head} - " + "; ".join(parts) if parts else head
    return line + "".join(f"\n       ! {e}" for e in report.errors)


def sync_all(db_factory, *, book_id=None, chapter_id=None, rebuild: bool = False, prune: bool = False,
             allow_fake: bool = False) -> list[str]:
    refuse_fake_embeddings(allow_fake)
    out: list[str] = []
    store = get_graph_store()
    with db_factory() as db:
        ready_ids = {str(c.id) for c in db.scalars(select(Chapter).where(Chapter.status == ChapterStatus.READY))}
        if rebuild:
            if store is None:
                raise SystemExit("GRAPH_STORE_PROVIDER is 'none': there is no graph-store copy to rebuild.")
            store.ensure_schema()
            store.clear()
            out.append("graph store cleared; writing every ready chapter again from PostgreSQL (stored vectors, no embedding calls)")
            query = select(Chapter).where(Chapter.status == ChapterStatus.READY)
            if chapter_id is not None:
                query = query.where(Chapter.id == chapter_id)
            elif book_id is not None:
                query = query.where(Chapter.book_id == book_id)
            targets = [c.id for c in db.scalars(query.order_by(Chapter.book_id, Chapter.sequence_num))]
        else:
            targets = [c.id for c in chapters_needing_index(db, book_id, chapter_id)]

        if prune and store is not None and not rebuild:
            stale = sorted(store.list_chapter_ids() - ready_ids)
            for cid in stale:
                store.delete_chapter(cid)
            out.append(f"pruned {len(stale)} chapter(s) that PostgreSQL no longer has as ready")

    failed = False
    for cid in targets:
        report = index_chapter(db_factory, cid, embed=not rebuild)
        failed = failed or bool(report.errors)
        with db_factory() as db:
            out.append(_describe(db, cid, report))
    out.append(f"{len(targets)} chapter(s) processed" + ("; some FAILED, run again after fixing the cause" if failed else ""))
    if store is not None:
        try:
            out.append("graph store now holds: " + ", ".join(f"{k} {v}" for k, v in store.stats().items()))
        except Exception as exc:
            out.append(f"(could not read graph-store stats: {exc})")
    if failed:
        out.append("!FAILED")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--chapter")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--prune", action="store_true")
    parser.add_argument("--allow-fake", action="store_true", help="allow placeholder vectors (tests only)")
    a = parser.parse_args()
    if a.status:
        with SessionLocal() as db:
            print("\n".join(status_lines(db)))
        return
    lines = sync_all(
        SessionLocal, book_id=uuid.UUID(a.book) if a.book else None,
        chapter_id=uuid.UUID(a.chapter) if a.chapter else None,
        rebuild=a.rebuild, prune=a.prune, allow_fake=a.allow_fake,
    )
    print("\n".join(line for line in lines if line != "!FAILED"))
    if "!FAILED" in lines:
        sys.exit(1)


if __name__ == "__main__":
    main()
