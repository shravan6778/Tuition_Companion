"""Builds the chapter's prerequisite graph from its page-level concepts.

1. Concepts with the same normalized name inside a chapter are ONE concept: the first occurrence
   (lowest page, then position) is canonical; only canonical concepts get edges.
2. Candidate edges come from (a) page-level prerequisite names that match a canonical concept in this
   chapter and (b) one LLM linking call per chapter (pipeline/linking.py).
3. Cycles are broken deterministically: edges are added most-plausible first (prerequisite appears on an
   earlier-or-same page), and any edge that would close a cycle is dropped and listed in the report.
The stored graph is therefore always a DAG. Nothing is committed here; the caller commits."""
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.content import Chapter, Concept, ConceptEdge, Page
from app.pipeline.linking import propose_links

MAX_REPORTED = 50


def normalize_name(name: str) -> str:
    s = unicodedata.normalize("NFKC", name or "").casefold()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


@dataclass
class _Candidate:
    prerequisite: Concept
    concept: Concept
    source: str  # "page" | "llm"


def _creates_cycle(dependents: dict, prerequisite_id, concept_id) -> bool:
    """Adding prerequisite -> concept makes a cycle iff concept can already reach prerequisite."""
    stack, seen = [concept_id], set()
    while stack:
        node = stack.pop()
        if node == prerequisite_id:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(dependents.get(node, ()))
    return False


def build_chapter_graph(db: Session, chapter: Chapter, llm) -> dict:
    """(Re)builds concept identity + edges for one chapter and returns the report (also stored on the chapter)."""
    db.execute(delete(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id))

    rows = db.execute(
        select(Concept, Page.page_number)
        .join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id)
        .order_by(Page.page_number, Concept.position)
    ).all()

    # --- 1. identity: merge same-named concepts, first occurrence wins
    canon: dict[str, Concept] = {}
    page_of: dict = {}
    keyed: list[tuple[Concept, str]] = []
    for concept, page_number in rows:
        key = normalize_name(concept.name) or str(concept.id)
        concept.name_key = key
        concept.is_canonical = key not in canon
        canon.setdefault(key, concept)
        page_of[concept.id] = page_number
        keyed.append((concept, key))
    ordered = list(canon.values())  # chapter order

    # --- 2a. candidates from prerequisite names the page-level LLM wrote
    candidates: list[_Candidate] = []
    unresolved: list[dict] = []
    seen_unresolved: set[tuple[str, str]] = set()
    for concept, key in keyed:
        target = canon[key]
        for raw in concept.prerequisites or []:
            pkey = normalize_name(raw)
            if not pkey or pkey == key:
                continue
            if pkey in canon:
                candidates.append(_Candidate(canon[pkey], target, "page"))
            elif (key, pkey) not in seen_unresolved:
                seen_unresolved.add((key, pkey))
                unresolved.append({"concept": target.name, "prerequisite": raw})

    # --- 2b. candidates from the chapter-level LLM pass
    llm_status = "skipped_too_few_concepts"
    if len(ordered) >= 2:
        if len(ordered) > settings.link_max_concepts:
            llm_status = "skipped_too_many_concepts"
        else:
            pairs = propose_links(llm, [(c.name, c.description or "") for c in ordered])
            candidates += [_Candidate(ordered[p], ordered[c], "llm") for c, p in pairs]
            llm_status = "done"

    # --- 3. add plausible edges first; drop whatever would close a cycle
    def rank(c: _Candidate):
        backward = page_of[c.prerequisite.id] > page_of[c.concept.id]
        return (backward, c.source != "page", page_of[c.concept.id], page_of[c.prerequisite.id])

    dependents: dict = defaultdict(set)
    accepted: dict[tuple, str] = {}
    dropped: list[dict] = []
    for cand in sorted(candidates, key=rank):
        pair = (cand.prerequisite.id, cand.concept.id)
        if pair in accepted:
            continue
        if _creates_cycle(dependents, cand.prerequisite.id, cand.concept.id):
            dropped.append({"prerequisite": cand.prerequisite.name, "concept": cand.concept.name})
            continue
        accepted[pair] = cand.source
        dependents[cand.prerequisite.id].add(cand.concept.id)

    for (prereq_id, concept_id), source in accepted.items():
        db.add(ConceptEdge(chapter_id=chapter.id, concept_id=concept_id, prerequisite_id=prereq_id, source=source))

    report = {
        "concepts": len(ordered),
        "duplicate_names_merged": len(rows) - len(ordered),
        "edges": len(accepted),
        "llm_linking": llm_status,
        "model": getattr(llm, "model_name", "unknown"),  # 'fake' = placeholder concepts, not real extraction
        "unresolved_prerequisites": unresolved[:MAX_REPORTED],
        "dropped_cycle_edges": dropped[:MAX_REPORTED],
    }
    chapter.graph_report = report
    db.flush()
    return report
