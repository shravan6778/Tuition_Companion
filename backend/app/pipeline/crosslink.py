"""Cross-chapter prerequisites: which concepts of EARLIER chapters of the same book a chapter's concepts need.

How it works (cheap layers first, LLM last):
  1. For every canonical concept of the chapter, the nearest canonical concepts of earlier READY chapters of the
     same book are found by the stored embeddings (PostgreSQL's copy; no embedding calls). Weak matches are dropped.
  2. ONE LLM call per batch sees only numbered concepts and numbered candidates and answers with numbers, so it
     cannot invent anything; a prerequisite outside a concept's own candidate list fails validation and is retried.
  3. The result replaces the chapter's rows in `cross_chapter_edges`. Edges only ever point from a lower chapter
     number to a higher one, so the book-wide graph cannot gain a cycle.
If the candidate set is unchanged since the last run the LLM is not asked again (`signature`). Everything here runs
AFTER the chapter is committed and can never fail it; the outcome is recorded in `chapter.graph_report["cross_chapter"]`.
Only the same book is ever searched, so nothing crosses teachers."""
import hashlib
import json
import logging
import re
import uuid

import numpy as np
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.models.content import Chapter, ChapterStatus, Concept, ContentEmbedding, CrossChapterEdge, Page
from app.embeddings.vectors import from_bytes

logger = logging.getLogger(__name__)
MAX_RETRIES = 2

SYSTEM = (
    "You are a curriculum analyst. You get NEW concepts of one textbook chapter and, for each, a short list of "
    "candidate concepts from EARLIER chapters of the same book. Pick a candidate ONLY if a student could not "
    "understand the new concept without first knowing that candidate: a direct, necessary prerequisite, not a "
    "related topic, not the same general subject, not background that merely helps. Most concepts have none, and "
    "choosing nothing is the normal, correct answer; when unsure, choose nothing. At most 2 per concept. Use only "
    "the given numbers, and for each concept only numbers from its own candidates list. Reply with JSON only, "
    'shaped exactly as: {"links":[{"concept":<number>,"prerequisites":[<number>,...]}]}. Omit concepts with no '
    "prerequisites."
)


class CrossLinkError(ProcessingError):
    pass


class _Item(BaseModel):
    concept: int
    prerequisites: list[int] = Field(default_factory=list)


class _Result(BaseModel):
    links: list[_Item]


def _clip(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _usable(row: ContentEmbedding) -> bool:
    from app.pipeline.indexing import _usable as usable  # same rule as the graph copy: no placeholder/odd-size vectors
    return usable(row)


def _canonical(db: Session, chapter_ids: list) -> list[tuple[Concept, Chapter]]:
    rows = db.execute(
        select(Concept, Chapter).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Chapter.id.in_(chapter_ids), Concept.is_canonical.is_(True))
        .order_by(Chapter.sequence_num, Page.page_number, Concept.position)
    ).all()
    return [(c, ch) for c, ch in rows]


def _vectors(db: Session, chapter_ids: list) -> dict:
    out = {}
    for row in db.scalars(select(ContentEmbedding).where(ContentEmbedding.chapter_id.in_(chapter_ids), ContentEmbedding.concept_id.is_not(None))):
        if _usable(row):
            out[row.concept_id] = (row.model, np.asarray(from_bytes(row.vector), dtype=float))
    return out


def earlier_chapters(db: Session, chapter: Chapter) -> list[Chapter]:
    if chapter.sequence_num is None:
        return []
    return list(db.scalars(
        select(Chapter).where(
            Chapter.book_id == chapter.book_id, Chapter.status == ChapterStatus.READY,
            Chapter.sequence_num < chapter.sequence_num, Chapter.id != chapter.id,
        ).order_by(Chapter.sequence_num)
    ))


def find_candidates(db: Session, chapter: Chapter) -> dict:
    """{concept: [(earlier concept, earlier chapter, similarity), ...]} nearest first, only above the floor."""
    earlier = earlier_chapters(db, chapter)
    if not earlier:
        return {}
    new = _canonical(db, [chapter.id])
    old = _canonical(db, [c.id for c in earlier])
    vectors = _vectors(db, [chapter.id, *[c.id for c in earlier]])
    old = [(c, ch) for c, ch in old if c.id in vectors]
    if not old:
        return {}
    matrix = np.vstack([vectors[c.id][1] / (np.linalg.norm(vectors[c.id][1]) or 1.0) for c, _ in old])
    models = [vectors[c.id][0] for c, _ in old]
    found = {}
    for concept, _ in new:
        if concept.id not in vectors:
            continue
        model, vec = vectors[concept.id]
        norm = np.linalg.norm(vec) or 1.0
        sims = matrix @ (vec / norm)
        order = np.argsort(-sims)
        picks = [
            (old[i][0], old[i][1], float(sims[i])) for i in order
            if models[i] == model and sims[i] >= settings.crosslink_min_similarity
        ][: settings.crosslink_candidates]
        if picks:
            found[concept] = picks
    return found


def _signature(candidates: dict, model: str) -> str:
    rows = sorted((str(c.id), sorted(str(p.id) for p, _, _ in picks)) for c, picks in candidates.items())
    return hashlib.sha256(json.dumps([model, settings.crosslink_max_per_concept, settings.crosslink_keep_similarity, rows]).encode()).hexdigest()


def _ask(provider, batch: list, chapter: Chapter) -> dict:
    """batch: [(concept, picks)] -> {concept id: [(prerequisite concept, similarity)]}. Validated, retried."""
    olds: dict = {}
    for _, picks in batch:
        for p, ch, _ in picks:
            olds.setdefault(p.id, (len(olds) + 1, p, ch))
    lines = [f"NEW CONCEPTS (chapter: {_clip(chapter.title, 80)})"]
    for i, (concept, picks) in enumerate(batch, 1):
        lines.append(f"{i}. {_clip(concept.name, 80)} - {_clip(concept.description, 120)}")
        lines.append("   candidates: " + ", ".join(str(olds[p.id][0]) for p, _, _ in picks))
    lines.append("EARLIER CONCEPTS")
    for number, p, ch in sorted(olds.values(), key=lambda t: t[0]):
        lines.append(f"{number}. [{_clip(ch.title, 50)}] {_clip(p.name, 80)} - {_clip(p.description, 120)}")
    user = "CROSS-CHAPTER\n" + "\n".join(lines)
    by_number = {number: p for number, p, _ in olds.values()}
    allowed = [{olds[p.id][0] for p, _, _ in picks} for _, picks in batch]
    sims = [{p.id: s for p, _, s in picks} for _, picks in batch]
    last = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user if not attempt else f"{user}\n\nYour previous reply was invalid: {last}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            result = _Result.model_validate_json(text)
        except ValidationError as exc:
            last = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        bad = next(
            (f"concept {it.concept} / prerequisite {n} is not allowed" for it in result.links for n in it.prerequisites
             if not 1 <= it.concept <= len(batch) or n not in allowed[it.concept - 1]),
            "",
        )
        if bad:
            last = bad
            continue
        out: dict = {}
        for it in result.links:
            concept = batch[it.concept - 1][0]
            chosen = list(dict.fromkeys(it.prerequisites))[: settings.crosslink_max_per_concept]
            out.setdefault(concept.id, [])
            out[concept.id] += [(by_number[n], sims[it.concept - 1][by_number[n].id]) for n in chosen if by_number[n] not in [x for x, _ in out[concept.id]]]
        return out
    raise CrossLinkError("Couldn't link this chapter's concepts to earlier chapters.")


def crosslink_chapter(db: Session, chapter: Chapter, provider) -> dict:
    """Recomputes this chapter's cross-chapter edges. Commits nothing. Returns the report (also stored on the chapter)."""
    report: dict = {"status": "done", "model": getattr(provider, "model_name", "unknown")}
    old_report = (chapter.graph_report or {}).get("cross_chapter") or {}

    def finish(rep: dict) -> dict:
        chapter.graph_report = {**(chapter.graph_report or {}), "cross_chapter": rep}
        db.flush()
        return rep

    if not settings.crosslink_enabled:
        return finish({"status": "disabled"})
    new_count = len(_canonical(db, [chapter.id]))
    if new_count > settings.crosslink_max_concepts:
        return finish({"status": "skipped_too_many_concepts"})
    candidates = find_candidates(db, chapter)
    if not candidates:
        db.execute(delete(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))
        return finish({"status": "no_candidates", "edges": 0, "earlier_chapters": len(earlier_chapters(db, chapter))})

    signature = _signature(candidates, report["model"])
    have = len(db.scalars(select(CrossChapterEdge.id).where(CrossChapterEdge.chapter_id == chapter.id)).all())
    if old_report.get("signature") == signature and old_report.get("edges") == have:
        return finish({**old_report, "status": "unchanged"})

    items = list(candidates.items())
    found: dict = {}
    for start in range(0, len(items), settings.crosslink_batch):
        for cid, picks in _ask(provider, items[start:start + settings.crosslink_batch], chapter).items():
            found.setdefault(cid, []).extend(picks)

    db.execute(delete(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))
    edges = dropped_weak = 0
    for cid, picks in found.items():
        for prereq, similarity in picks:
            if similarity < settings.crosslink_keep_similarity:  # the model chose it, but the match is too thin to trust
                dropped_weak += 1
                continue
            db.add(CrossChapterEdge(chapter_id=chapter.id, concept_id=cid, prerequisite_id=prereq.id, similarity=round(similarity, 3)))
            edges += 1
    return finish({**report, "edges": edges, "dropped_weak": dropped_weak, "concepts_with_candidates": len(candidates),
                   "signature": signature, "earlier_chapters": len(earlier_chapters(db, chapter))})


def explain_chapter(db: Session, chapter: Chapter, provider) -> list[str]:
    """Dry run for judging the settings on real data: for every concept with candidates, prints the candidates (nearest
    first, with similarity) and what the model chose (kept / dropped as too weak). Asks the model, writes nothing."""
    candidates = find_candidates(db, chapter)
    if not candidates:
        return [f"{chapter.title}: no candidates ({len(earlier_chapters(db, chapter))} earlier chapters)"]
    items = list(candidates.items())
    chosen: dict = {}
    for start in range(0, len(items), settings.crosslink_batch):
        chosen.update(_ask(provider, items[start:start + settings.crosslink_batch], chapter))
    lines = [f"{chapter.title}: {len(candidates)} concepts with candidates "
             f"(offer floor {settings.crosslink_min_similarity}, keep floor {settings.crosslink_keep_similarity})"]
    for concept, picks in items:
        picked = {p.id for p, _ in chosen.get(concept.id, [])}
        lines.append(f"  {concept.name}")
        for p, ch, sim in picks:
            if p.id in picked:
                mark = "CHOSEN, kept" if sim >= settings.crosslink_keep_similarity else "CHOSEN, dropped (weak)"
            else:
                mark = "-"
            lines.append(f"      {sim:.3f}  {p.name}  [{_clip(ch.title, 40)}]  {mark}")
    return lines


def crosslink_after(session_factory, chapter_id, provider=None) -> list[str]:
    """After a chapter is ready and embedded: link it, then re-link the later chapters of the same book (their
    candidates may have changed, and links INTO a re-processed chapter were deleted with its old concepts).
    NEVER raises. Returns one line per chapter for logs / scripts."""
    lines: list[str] = []
    db = session_factory()
    try:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY or not settings.crosslink_enabled:
            return lines
        if provider is None:
            from app.llm import get_llm_provider
            provider = get_llm_provider()
        later = list(db.scalars(
            select(Chapter).where(
                Chapter.book_id == chapter.book_id, Chapter.status == ChapterStatus.READY,
                Chapter.sequence_num > (chapter.sequence_num or 0),
            ).order_by(Chapter.sequence_num).limit(settings.crosslink_max_relinks)
        )) if chapter.sequence_num is not None else []
        book_id = chapter.book_id
        for target_id in [chapter.id, *[c.id for c in later]]:
            try:
                target = db.get(Chapter, target_id)
                rep = crosslink_chapter(db, target, provider)
                db.commit()
                lines.append(f"{target.title}: {rep.get('status')} ({rep.get('edges', 0)} cross-chapter edges)")
            except Exception as exc:
                db.rollback()
                logger.exception("Cross-chapter linking of chapter %s failed", target_id)
                lines.append(f"FAILED {target_id}: {type(exc).__name__}")
                try:
                    target = db.get(Chapter, target_id)
                    target.graph_report = {**(target.graph_report or {}), "cross_chapter": {"status": "failed"}}
                    db.commit()
                except Exception:
                    db.rollback()
        from app.pipeline.indexing import sync_cross_edges
        sync_cross_edges(db, book_id)
    except Exception:
        logger.exception("Cross-chapter linking crashed for chapter %s", chapter_id)
    finally:
        db.close()
    return lines
