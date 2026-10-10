"""Layer 5 report: what teachers decided about variant suggestions, and how often they correct the front-page metadata.

    python -m app.db.match_feedback

Read-only, operator use: counts and number ranges only (no book titles, ids or teachers). Nothing here changes a
threshold on its own; use it to set the guesses (EMBED_MATCH_SIMILARITY, STRUCTURE_TITLE_OVERLAP, VARIANT_MIN_COVERAGE)
from real decisions: a threshold should sit above the biggest number among `dismissed` and below the smallest among
`confirmed`. `confirmed without a suggestion` are books the system missed entirely."""
import statistics
from collections import defaultdict

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Book, MatchFeedback
from app.pipeline.graph import normalize_name

FIELDS = ("board", "class_name", "subject", "publisher", "edition", "school")


def _range(values: list[float]) -> str:
    return "n/a" if not values else f"min {min(values):.2f}, median {statistics.median(values):.2f}, max {max(values):.2f}"


def summarize(db) -> list[str]:
    rows = list(db.scalars(select(MatchFeedback)))
    out = [f"variant suggestions: {len(rows)} teacher decisions"]
    by: dict = defaultdict(lambda: defaultdict(list))  # signal -> decision -> [evidence]
    missed = 0
    for r in rows:
        if r.evidence is None:
            if r.decision == "confirmed":
                missed += 1
            continue
        by[r.evidence.get("signal", "pages")][r.decision].append(r.evidence)
    for signal in sorted(by):
        out.append(f"  signal {signal}:")
        for decision in ("confirmed", "dismissed", "retracted"):
            ev = by[signal].get(decision, [])
            if ev:
                out.append(f"    {decision}: {len(ev)}  coverage {_range([e.get('coverage', 0) for e in ev])}  "
                           f"avg similarity {_range([e.get('avg_similarity', 0) for e in ev])}")
    out.append(f"  confirmed without a suggestion (the system missed it): {missed}")

    books = [b for b in db.scalars(select(Book).where(Book.extracted_metadata.is_not(None)))]
    out.append(f"front-page metadata: {len(books)} books confirmed from front pages")
    for f in FIELDS:
        pairs = [(normalize_name((b.extracted_metadata or {}).get(f) or ""), normalize_name(getattr(b, f) or "")) for b in books]
        changed = sum(1 for read, final in pairs if read != final)
        if books:
            out.append(f"  {f}: teacher changed {changed} of {len(books)}")
    return out


if __name__ == "__main__":
    with SessionLocal() as session:
        print("\n".join(summarize(session)))
