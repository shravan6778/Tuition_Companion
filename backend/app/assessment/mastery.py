"""Mastery history and weak-concept propagation (Phase 3 step 6). See models/mastery.py for the event rules.

  * `record_check` turns a graded check into events: one `check` event per concept (asked, correct, score), then, for every
    concept that tested weak, a `propagated` event for each concept that DEPENDS on it (reason text always attached).
    It only adds rows; the caller commits, so a check and its events succeed or fail together.
  * propagation walks prerequisite edges the other way round (weak concept -> the concepts that need it), inside a chapter
    (concept_edges) and across chapters of the book (cross_chapter_edges), up to PROPAGATE_MAX_DEPTH steps. A dependent is
    NOT flagged when it was measured in the same check (fresher, direct evidence), is already weak by measurement, or is
    already flagged because of the same concept.
  * only a MEASURED weak concept propagates; a propagated flag never propagates further on its own.
  * `current_state` derives where a student stands from the log: weak / ok (latest check) or at_risk (latest check-or-propagated
    event is a propagated one, cleared by the next check on that concept)."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, MasteryEvent, Page

CHECK, QUIZ, DOUBT, PROPAGATED = "check", "quiz", "doubt", "propagated"
MEASURED = (CHECK, QUIZ)
WEAK, OK, AT_RISK = "weak", "ok", "at_risk"
MAX_DEPENDENTS = 200  # one weak concept never fans out beyond this, however large a book's graph is

@dataclass
class ConceptState:
    concept_id: uuid.UUID
    name: str
    status: str  # weak | ok | at_risk
    score: Optional[float] = None  # the latest MEASURED score (None when only ever flagged)
    asked: Optional[int] = None
    correct: Optional[int] = None
    last_checked: Optional[datetime] = None
    reason: Optional[str] = None  # at_risk only: why it was flagged
    flagged_by: Optional[uuid.UUID] = None  # at_risk only: the weak prerequisite


@dataclass
class Dependent:
    concept_id: uuid.UUID
    name: str
    chain: list[str] = field(default_factory=list)  # names from the weak concept down to this dependent


def reason_text(chain: list[str]) -> str:
    """chain = [weak, ..., dependent]. 'flagged because it depends on B, which depends on A, which tested weak'."""
    between = list(reversed(chain[:-1]))
    return "flagged because it depends on " + ", which depends on ".join(between) + ", which tested weak"


def dependents(db: Session, weak_id: uuid.UUID, max_depth: Optional[int] = None) -> list[Dependent]:
    """Concepts that need `weak_id`, nearest first. Only canonical concepts of ready chapters; never the weak concept itself."""
    depth_cap = settings.propagate_max_depth if max_depth is None else max_depth
    start = db.get(Concept, weak_id)
    if start is None or depth_cap < 1:
        return []
    names = {weak_id: start.name}
    chains: dict[uuid.UUID, list[uuid.UUID]] = {weak_id: [weak_id]}
    frontier, found = [weak_id], []
    for _ in range(depth_cap):
        if not frontier:
            break
        nxt = []
        for model in (ConceptEdge, CrossChapterEdge):
            for dep_id, pre_id in db.execute(select(model.concept_id, model.prerequisite_id).where(model.prerequisite_id.in_(frontier))):
                if dep_id in chains:
                    continue
                chains[dep_id] = chains[pre_id] + [dep_id]
                nxt.append(dep_id)
        frontier = nxt
        found += nxt
        if len(found) >= MAX_DEPENDENTS:
            found = found[:MAX_DEPENDENTS]
            break
    if not found:
        return []
    ready = {c.id: c for c in db.scalars(
        select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id.in_(found + [i for ch in chains.values() for i in ch]), Concept.is_canonical.is_(True), Chapter.status == ChapterStatus.READY))}
    out = []
    for dep_id in found:
        chain = chains[dep_id]
        if dep_id in ready and all(i in ready or i == weak_id for i in chain):  # no flag across a concept that is not in a ready chapter
            out.append(Dependent(dep_id, ready[dep_id].name, [names.get(i) or ready[i].name for i in chain]))
    return out


def current_state(db: Session, student_id: uuid.UUID, concept_ids: Optional[Iterable[uuid.UUID]] = None) -> dict[uuid.UUID, ConceptState]:
    query = select(MasteryEvent).where(MasteryEvent.student_id == student_id, MasteryEvent.kind.in_([CHECK, QUIZ, PROPAGATED]),
                                       MasteryEvent.concept_id.is_not(None)).order_by(MasteryEvent.id)
    if concept_ids is not None:
        ids = list(concept_ids)
        if not ids:
            return {}
        query = query.where(MasteryEvent.concept_id.in_(ids))
    state: dict[uuid.UUID, ConceptState] = {}
    for e in db.scalars(query):
        s = state.get(e.concept_id)
        if s is None:
            s = state[e.concept_id] = ConceptState(e.concept_id, e.concept_name, OK)
        s.name = e.concept_name
        if e.kind in MEASURED:
            s.score, s.asked, s.correct, s.last_checked = e.score, e.asked, e.correct, e.created_at
            s.status = WEAK if e.score < settings.weak_below else OK
            s.reason = s.flagged_by = None  # a measured check or quiz clears an earlier flag
        else:
            s.status, s.reason, s.flagged_by = AT_RISK, e.reason, e.source_concept_id
    return state


def doubted_concept_ids(db: Session, student_id: uuid.UUID) -> list[uuid.UUID]:
    """Concepts the student asked about, most recent first."""
    rows = db.scalars(select(MasteryEvent.concept_id).where(MasteryEvent.student_id == student_id, MasteryEvent.kind == DOUBT,
                                                            MasteryEvent.concept_id.is_not(None)).order_by(MasteryEvent.id.desc()))
    seen: list[uuid.UUID] = []
    for cid in rows:
        if cid not in seen:
            seen.append(cid)
    return seen


def record_doubt(db: Session, student_id: uuid.UUID, concept_id: uuid.UUID, assignment_id: Optional[uuid.UUID]) -> None:
    concept = db.get(Concept, concept_id)
    if concept is not None:
        db.add(MasteryEvent(student_id=student_id, concept_id=concept_id, concept_name=concept.name[:300], kind=DOUBT, assignment_id=assignment_id))


def record_check(db: Session, student_id: uuid.UUID, check_id: Optional[uuid.UUID], assignment_id: Optional[uuid.UUID],
                 results: dict[uuid.UUID, tuple[int, int]], *, kind: str = CHECK,
                 quiz_id: Optional[uuid.UUID] = None) -> list[MasteryEvent]:
    """results: concept -> (asked, correct). Adds the events and flushes; the CALLER commits (one transaction with the check/quiz)."""
    if kind not in MEASURED:
        raise ValueError(f"Unsupported measured event kind: {kind}")
    added: list[MasteryEvent] = []
    names: dict[uuid.UUID, str] = {}
    weak: list[uuid.UUID] = []
    for concept_id, (asked, correct) in results.items():
        concept = db.get(Concept, concept_id)
        if concept is None or asked < 1:
            continue
        names[concept_id] = concept.name
        score = round(correct / asked, 4)
        added.append(MasteryEvent(student_id=student_id, concept_id=concept_id, concept_name=concept.name[:300], kind=kind, score=score,
                                  asked=asked, correct=correct, assignment_id=assignment_id, check_id=check_id, quiz_id=quiz_id))
        if score < settings.weak_below:
            weak.append(concept_id)
    db.add_all(added)
    db.flush()
    flagged: set[tuple[uuid.UUID, uuid.UUID]] = set()
    for weak_id in weak:
        deps = [d for d in dependents(db, weak_id) if d.concept_id not in names]  # measured in this very check/quiz: fresher evidence
        state = current_state(db, student_id, [d.concept_id for d in deps])
        for d in deps:
            s = state.get(d.concept_id)
            if s is not None and (s.status == WEAK or (s.status == AT_RISK and s.flagged_by == weak_id)) or (d.concept_id, weak_id) in flagged:
                continue
            flagged.add((d.concept_id, weak_id))
            added.append(MasteryEvent(student_id=student_id, concept_id=d.concept_id, concept_name=d.name[:300], kind=PROPAGATED,
                                      assignment_id=assignment_id, check_id=check_id, quiz_id=quiz_id,
                                      reason=reason_text(d.chain), source_concept_id=weak_id))
            db.add(added[-1])
    db.flush()
    return added


def record_quiz(db: Session, student_id: uuid.UUID, quiz_id: uuid.UUID, assignment_id: Optional[uuid.UUID],
                results: dict[uuid.UUID, tuple[int, int]]) -> list[MasteryEvent]:
    """Same unified mastery log and weak-area propagation as `record_check`, recorded with `kind='quiz'`."""
    return record_check(db, student_id, None, assignment_id, results, kind=QUIZ, quiz_id=quiz_id)