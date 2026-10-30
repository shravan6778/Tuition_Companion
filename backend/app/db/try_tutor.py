"""See what the Tutor would answer to a doubt, on your real books, with the real model. Writes nothing.

    python -m app.db.try_tutor --text "why does ice float" --book <id> [--book <id> ...] [--chapter <id>]
    python -m app.db.try_tutor --text "..." --book <id> --questions-file doubts.txt   # one doubt per line

Runs the same steps as POST /student/doubts: retrieval (scope = --chapter, like the assignment's Doubt button), and
only when that is `grounded`, the Tutor. Prints the status, the pages the Tutor was shown, its explanation, the pages
it says it used, the refresher, and whether it would be marked "auto-generated, please verify". Judge the answers
against the pages: is every sentence in them? Does a not-in-book doubt (try an off-topic one) get no explanation?"""
import argparse
import uuid

from app.core.config import refuse_fake_embeddings, settings
from app.core.errors import ProcessingError
from app.db.session import SessionLocal
from app.doubts import tutor
from app.doubts.retrieval import GROUNDED, Scope, retrieve
from app.doubts.service import _refresher_material
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.llm import get_llm_provider


def run(db, text: str, book_ids, chapter_ids, embedder, store, llm) -> list[str]:
    scope = Scope(chapter_ids={str(c) for c in chapter_ids}) if chapter_ids else None
    r = retrieve(db, text, embedder=embedder, store=store, book_ids=book_ids, scope=scope)
    out = [f"DOUBT: {text}", f"retrieval: {r.status} (best similarity {r.confidence:.3f} in scope, {r.elsewhere_confidence:.3f} anywhere; cut-off {r.threshold})"]
    if r.status != GROUNDED:
        return out + ["-> the Tutor is not asked; the student is told: " + {
            "outside_assignment": "not part of this assignment, try Ask a Doubt",
            "not_in_book": "not in your book yet, upload this chapter",
            "unavailable": "couldn't look this up right now"}[r.status], ""]
    pages = r.pages[: settings.tutor_max_pages]
    for i, p in enumerate(pages, 1):
        out.append(f"  shown P{i}: page {p.page_number} of '{p.chapter_title}' ({p.similarity:.3f}): {' '.join(p.text.split())[:140]}...")
    refresher = _refresher_material(db, r, list(book_ids))
    if refresher:
        out.append("  refresher material: " + ", ".join(name for name, _ in refresher))
    try:
        answer = tutor.explain(llm, text, pages, r.concepts, refresher)
    except ProcessingError as exc:
        return out + [f"-> the Tutor failed ({exc}); the student would see the pages only", ""]
    if answer.cannot_answer:
        return out + ["-> the Tutor says the pages do not answer this; no explanation is shown", ""]
    out.append("ANSWER: " + answer.answer)
    if answer.refresher:
        out.append("REFRESHER: " + answer.refresher)
    out.append("sources: " + ", ".join(f"page {p.page_number} of '{p.chapter_title}'" for p in answer.sources))
    if r.confidence < settings.tutor_verify_below:
        out.append(f"-> marked 'auto-generated, please verify' (similarity {r.confidence:.3f} < {settings.tutor_verify_below})")
    out.append(f"(model: {answer.model})")
    return out + [""]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--text", action="append")
    parser.add_argument("--questions-file")
    parser.add_argument("--book", action="append", required=True)
    parser.add_argument("--chapter", action="append")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_embeddings(a.allow_fake)
    if settings.llm_provider.lower() == "fake" and not a.allow_fake:
        raise SystemExit("LLM_PROVIDER is 'fake': its answers are placeholders. Use the real model, or pass --allow-fake.")
    texts = list(a.text or [])
    if a.questions_file:
        with open(a.questions_file, encoding="utf-8") as fh:
            texts += [line.strip() for line in fh if line.strip()]
    if not texts:
        raise SystemExit("Give --text or --questions-file.")
    embedder, store = get_embedding_provider(), get_graph_store()
    if embedder is None or store is None:
        raise SystemExit("Set EMBEDDING_PROVIDER and GRAPH_STORE_PROVIDER first.")
    llm = get_llm_provider()
    with SessionLocal() as db:
        for t in texts:
            print("\n".join(run(db, t, [uuid.UUID(b) for b in a.book], [uuid.UUID(c) for c in a.chapter or []], embedder, store, llm)))
