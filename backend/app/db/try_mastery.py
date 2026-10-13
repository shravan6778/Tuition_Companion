"""See, on the real graph, what a weak result would flag. Writes nothing.

    python -m app.db.try_mastery --chapter <chapter id>                          # which concepts the most others depend on
    python -m app.db.try_mastery --chapter <chapter id> --weak "System of coordinates"   # who would be flagged, and the reason shown

The reason text is exactly what the student would see. Judge: do the flagged concepts really need the weak one? Are any missing,
or flagged without a good reason? (Depth is PROPAGATE_MAX_DEPTH; use --depth to try another.)"""
import argparse
import uuid


from app.assessment import mastery
from app.assignments.scope import chapter_concepts
from app.core.config import settings
from app.db.session import SessionLocal


def run(db, chapter_id, weak_name=None, depth=None) -> list[str]:
    concepts = chapter_concepts(db, chapter_id)
    if not concepts:
        return ["no concepts in that chapter"]
    by_name = {c.name.lower(): c for c in concepts}
    if weak_name is None:
        counts = []
        for c in concepts:
            counts.append((len(mastery.dependents(db, c.id, depth)), c.name))
        counts.sort(key=lambda t: (-t[0], t[1]))
        return [f"{len(concepts)} concepts; the ones the most others depend on (depth {depth or settings.propagate_max_depth}):"] + [f"  {n:3d} dependents  {name}" for n, name in counts[:10]]
    weak = by_name.get(weak_name.strip().lower())
    if weak is None:
        return [f"no concept named {weak_name!r} in that chapter"]
    deps = mastery.dependents(db, weak.id, depth)
    out = [f"If '{weak.name}' tested weak (below {settings.weak_below}), {len(deps)} concept(s) would be flagged at risk:"]
    out += [f"  - {d.name}: {mastery.reason_text(d.chain)}" for d in deps] or ["  (nothing depends on it)"]
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--weak")
    parser.add_argument("--depth", type=int)
    a = parser.parse_args()
    with SessionLocal() as db:
        print("\n".join(run(db, uuid.UUID(a.chapter), a.weak, a.depth)))
