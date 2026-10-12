"""See what a student's photographed (or typed) doubt would retrieve, on your real books. Writes nothing; the photo is not kept.

    python -m app.db.try_doubt_photo <photo.jpg|png|pdf> --book <id> [--book <id> ...] [--chapter <id>]
    python -m app.db.try_doubt_photo --text "why does ice float" --book <id>

The same OCR service as the front pages reads the photo. Prints the text read, how it is classified (too short /
a doubt / a whole page), and what retrieval returns: status, best similarity, matching pages, concepts and prerequisites.
`--chapter` narrows the search the way the assignment's Doubt button will."""
import argparse
import os
import uuid

from app.core.config import refuse_fake_embeddings, settings
from app.db.session import SessionLocal
from app.doubts.query import DOUBT, PAGE, RETAKE_MESSAGE, TOO_SHORT, classify_doubt_text
from app.doubts.retrieval import Scope, concepts_on_page, retrieve
from app.embeddings import get_embedding_provider
from app.graph_store import get_graph_store
from app.ocr import get_ocr_provider


def run(db, text: str, from_photo: bool, book_ids, chapter_ids, embedder, store) -> list[str]:
    q = classify_doubt_text(text, from_photo)
    out = [f"text read ({q.words} words): {' '.join(text.split())[:300]}{'...' if len(text) > 300 else ''}", f"classified as: {q.kind}"]
    if q.kind == TOO_SHORT:
        return out + [f"-> would tell the student: {RETAKE_MESSAGE}"]
    scope = Scope(chapter_ids={str(c) for c in chapter_ids}) if chapter_ids else None
    r = retrieve(db, q.text, embedder=embedder, store=store, book_ids=book_ids, scope=scope)
    out.append(f"retrieval: {r.status} (best similarity {r.confidence:.3f} in scope, {r.elsewhere_confidence:.3f} anywhere; cut-off {r.threshold})")
    for p in r.pages[:3]:
        out.append(f"  page {p.page_number} of '{p.chapter_title}' ({p.similarity:.3f}): {' '.join(p.text.split())[:100]}...")
    for c in r.concepts[:5]:
        out.append(f"  concept {c.name} ({c.similarity:.3f})")
    if r.prerequisites:
        out.append("  refresher (prerequisites): " + ", ".join(f"{p.name} (depth {p.depth})" for p in r.prerequisites[:6]))
    if q.kind == PAGE and r.pages:
        out.append("  whole page: the student would now pick the concept that confused them: "
                   + ", ".join(c.name for c in concepts_on_page(db, uuid.UUID(r.pages[0].page_id))))
    if r.status == "outside_assignment":
        out.append("  -> would offer the standalone Ask a Doubt: " + ", ".join(h.name for h in r.elsewhere))
    if r.status == "not_in_book":
        out.append("  -> would say: this isn't in your book yet, ask your teacher to add it")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", nargs="?")
    parser.add_argument("--text")
    parser.add_argument("--book", action="append", required=True)
    parser.add_argument("--chapter", action="append")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_embeddings(a.allow_fake)
    if not a.file and not a.text:
        raise SystemExit("Give a photo file or --text.")
    embedder, store = get_embedding_provider(), get_graph_store()
    if embedder is None or store is None:
        raise SystemExit("Set EMBEDDING_PROVIDER and GRAPH_STORE_PROVIDER first.")
    if a.file:
        with open(a.file, "rb") as fh:
            data = fh.read()
        text = get_ocr_provider().extract(data, os.path.splitext(a.file)[1].lstrip(".").lower()).text
    else:
        text = a.text
    with SessionLocal() as db:
        print("\n".join(run(db, text, bool(a.file), [uuid.UUID(b) for b in a.book], [uuid.UUID(c) for c in a.chapter or []], embedder, store)))
