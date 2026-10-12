"""Measure the "not in your book" cut-off on your real chapters (real LLM + real embeddings + the real graph store).

    python -m app.db.retrieval_probe                    # official books, 12 sampled pages
    python -m app.db.retrieval_probe --book <id> --pages 20

The model writes student-style doubts about sampled pages; ten off-topic questions are added; every question goes
through the same retrieval the Tutor will use. It prints how similar each group scored and where a cut-off could sit
(PASS / FAIL like the Phase 2 exit check). Needs embeddings + Memgraph synced (`python -m app.db.sync_graph`). Writes nothing."""
import argparse
import uuid

from sqlalchemy import select

from app.core.config import refuse_fake_embeddings, refuse_fake_llm, settings
from app.db.session import SessionLocal
from app.doubts.calibration import probe
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import Book


def format_report(r: dict) -> list[str]:
    if r["status"] != "done":
        return [f"cannot judge: {r}"]
    out = [
        f"{r['doubts']} student-style doubts, {len(r['off_topic_values'])} off-topic questions",
        f"in-book doubts   best similarity: min {r['in_book_min']:.3f}, 10th percentile {r['in_book_p10']:.3f}, median {r['in_book_median']:.3f}",
        f"off-topic        best similarity: median {r['off_topic_median']:.3f}, max {r['off_topic_max']:.3f}",
        f"top hit was the right chapter for {r['right_chapter_top_hit']:.0%} of in-book doubts",
    ]
    if r["wrong_chapter_outside"] is not None:
        out.append(f"asked inside the WRONG chapter: {r['wrong_chapter_outside']:.0%} came back `outside_assignment` (scoped max {r['wrong_chapter_scoped_max']:.3f})")
    out.append(f"current RETRIEVAL_MIN_SIMILARITY {r['threshold']}: answers {r['answered_in_book']:.0%} of in-book doubts, wrongly answers {r['wrongly_answered_off_topic']:.0%} of off-topic")
    if r["separable"]:
        out.append(f"groups are separable. Suggested cut-off: {r['recommended']}")
    else:
        out.append("groups OVERLAP: no single cut-off separates them cleanly. Do not rely on the threshold alone; paste this output.")
    out.append("PASS" if r["pass"] else "FAIL (at the current cut-off)")
    out.append("in-book values:   " + " ".join(map(str, r["in_book_values"])))
    out.append("off-topic values: " + " ".join(map(str, r["off_topic_values"])))
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--pages", type=int, default=12)
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_llm(a.allow_fake)
    refuse_fake_embeddings(a.allow_fake)
    embedder, store = get_embedding_provider(), get_graph_store()
    if embedder is None or store is None:
        raise SystemExit("Set EMBEDDING_PROVIDER and GRAPH_STORE_PROVIDER (see the Phase 2 run-book) first.")
    with SessionLocal() as db:
        ids = [uuid.UUID(a.book)] if a.book else list(db.scalars(select(Book.id).where(Book.is_reference.is_(True))))
        print("\n".join(format_report(probe(db, get_llm_provider(), embedder, store, ids, a.pages))))
