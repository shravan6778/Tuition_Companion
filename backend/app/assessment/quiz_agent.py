"""Quiz Agent (Phase 4 Step 1): plans and generates mixed-difficulty quiz questions grounded in textbook pages.

Decided in Phase 4 (phase_4.md "Settled before building"):
  * question mix  : 50% recall, 30% application, 20% cross_concept (minimum 1 cross_concept guaranteed whenever at least
                    2 concepts or a prerequisite link exist and total >= 2).
  * answer format : multiple-choice (`mcq`, 4 options, 1 correct, shuffled in code, graded by code) and short-answer
                    (`short_answer`, graded by LLM against `expected_answer` in Step 4). Recall uses `mcq`; cross_concept
                    and a share of application questions use `short_answer` so every quiz exercises both grading paths.
  * grounding     : every question is generated strictly from the concept's textbook page text (and the related concept's
                    page text for `cross_concept`), validated against a Pydantic schema with up to 2 correction retries.
  * no leak       : `student_view` strips `correct_index`, `expected_answer`, and `explanation` before submission."""
import json
import logging
import random
import re
import uuid
from dataclasses import dataclass
from typing import Optional, Sequence

from pydantic import BaseModel, Field, ValidationError, field_validator
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ProcessingError
from app.graph_store.base import GraphStoreError
from app.models import AnswerFormat, Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, Page, QuestionType

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

MCQ_SYSTEM = (
    "You are the Quiz Agent for a school textbook platform. Write ONE multiple-choice question matching the requested "
    "QUESTION TYPE, using ONLY the textbook page(s) given. Reply with JSON only: "
    '{"question":str,"options":[str,str,str,str],"correct_index":int,"explanation":str}. '
    "Rules: (1) Exactly 4 options, 1-250 chars each, all distinct, exactly one correct, the others plausible but clearly "
    "wrong according to the page. (2) Do not use 'all of the above', 'none of the above' or 'both A and B'. "
    "(3) For RECALL: test a key definition, fact, or principle stated on the page without copying a sentence verbatim. "
    "(4) For APPLICATION: present a concrete scenario or problem where the student must apply the concept from the page. "
    "(5) For CROSS_CONCEPT: require the student to connect BOTH the primary concept and the related concept. "
    "(6) Make sure options[correct_index] is the exact option that your explanation proves right. "
    "(7) Add no outside facts. If QUESTIONS ALREADY ASKED are listed, ask about a different aspect."
)

SHORT_SYSTEM = (
    "You are the Quiz Agent for a school textbook platform. Write ONE short-answer question (1-2 sentences for the student "
    "to answer) matching the requested QUESTION TYPE, using ONLY the textbook page(s) given. Reply with JSON only: "
    '{"question":str,"expected_answer":str,"explanation":str}. '
    "Rules: (1) For APPLICATION: ask the student to apply the concept to a specific situation or explain 'why/how' based on "
    "the page. (2) For CROSS_CONCEPT: ask how the primary concept and the related concept connect, depend on, or contrast "
    "with each other according to the pages. (3) For RECALL: ask the student to state the core idea in their own words. "
    "(4) 'expected_answer' (1-3 sentences) states the key points a full-credit student answer must contain, grounded only "
    "in the page(s). (5) 'explanation' briefly explains the reasoning. Add no outside knowledge."
)


class QuizAgentError(ProcessingError):
    pass


class McqQuizSchema(BaseModel):
    question: str = Field(min_length=8, max_length=500)
    options: list[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str = Field(default="", max_length=500)

    @field_validator("options")
    @classmethod
    def _distinct(cls, options: list[str]) -> list[str]:
        cleaned = [o.strip() for o in options]
        if any(not o or len(o) > 250 for o in cleaned):
            raise ValueError("every option must be 1-250 characters")
        if len({o.lower() for o in cleaned}) != 4:
            raise ValueError("options must be different from each other")
        if any(re.search(r"\b(all|none) of the above\b|\bboth [a-d] and [a-d]\b", o, re.I) for o in cleaned):
            raise ValueError("no 'all/none of the above' options")
        return cleaned


class ShortAnswerQuizSchema(BaseModel):
    question: str = Field(min_length=8, max_length=500)
    expected_answer: str = Field(min_length=5, max_length=600)
    explanation: str = Field(default="", max_length=500)

    @field_validator("question", "expected_answer")
    @classmethod
    def _non_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 5:
            raise ValueError("field cannot be blank")
        return cleaned


@dataclass
class ConceptContext:
    concept_id: uuid.UUID
    name: str
    description: str
    page_number: int
    page_text: str
    chapter_id: uuid.UUID
    book_id: uuid.UUID


@dataclass
class PlannedQuizItem:
    position: int
    concept_id: uuid.UUID
    related_concept_id: Optional[uuid.UUID]
    question_type: str  # recall | application | cross_concept
    answer_format: str  # mcq | short_answer


@dataclass
class GeneratedQuizQuestion:
    """Server-side generated question including the answer key (`correct_index` or `expected_answer`).
    Never return this directly to a student before submission; use `student_view`."""
    concept_id: str
    related_concept_id: Optional[str]
    question_type: str
    answer_format: str
    question: str
    options: Optional[list[str]]
    correct_index: Optional[int]
    expected_answer: Optional[str]
    explanation: str


def question_mix(total: int, can_cross: bool = True) -> tuple[int, int, int]:
    """Returns `(n_recall, n_application, n_cross_concept)` summing to `total`.
    Baseline: 50% recall, 30% application, 20% cross_concept, with at least 1 cross_concept and at least 1 recall
    whenever `total >= 2` and `can_cross`."""
    if total <= 0:
        return 0, 0, 0
    if total == 1 or not can_cross:
        n_cross = 0
        n_app = min(round(total * settings.quiz_application_share), total - 1) if total > 1 else 0
        n_recall = total - n_app
        return n_recall, n_app, n_cross

    n_cross = max(1, round(total * settings.quiz_cross_concept_share))
    n_app = max(0, min(round(total * settings.quiz_application_share), total - n_cross - 1))
    n_recall = total - n_app - n_cross
    return n_recall, n_app, n_cross


def load_concept_contexts(
    db: Session,
    concept_ids: Sequence[uuid.UUID],
    book_ids: Optional[Sequence[uuid.UUID]] = None,
    store=None,
) -> tuple[dict[uuid.UUID, ConceptContext], dict[uuid.UUID, list[uuid.UUID]]]:
    """Loads grounded `ConceptContext` rows from PostgreSQL (ready chapters of allowed books only) and builds a map of
    `concept_id -> [related_concept_ids]` using Memgraph (`store.prerequisites`) when available plus PostgreSQL edges."""
    unique_ids = list(dict.fromkeys(concept_ids))
    if not unique_ids:
        return {}, {}

    query = (
        select(Concept, Page, Chapter)
        .join(Page, Page.id == Concept.page_id)
        .join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id.in_(unique_ids), Concept.is_canonical.is_(True), Chapter.status == ChapterStatus.READY)
    )
    if book_ids is not None:
        allowed_books = list(book_ids)
        if not allowed_books:
            return {}, {}
        query = query.where(Chapter.book_id.in_(allowed_books))

    contexts: dict[uuid.UUID, ConceptContext] = {}
    for concept, page, chapter in db.execute(query).all():
        contexts[concept.id] = ConceptContext(
            concept_id=concept.id,
            name=concept.name,
            description=concept.description or "",
            page_number=page.page_number or 1,
            page_text=page.content_text or "",
            chapter_id=chapter.id,
            book_id=chapter.book_id,
        )
    if not contexts:
        return {}, {}

    allowed_book_strs = [str(b) for b in (book_ids if book_ids is not None else {c.book_id for c in contexts.values()})]
    related_ids_needed: set[uuid.UUID] = set()
    related_map: dict[uuid.UUID, list[uuid.UUID]] = {cid: [] for cid in contexts}

    # 1. Pull connected prerequisite concepts from Memgraph when available
    if store is not None:
        for cid in list(contexts):
            try:
                prereqs = store.prerequisites(str(cid), allowed_book_strs, max_depth=1)
                for p in prereqs:
                    pid = uuid.UUID(p.concept_id)
                    if pid != cid and pid not in related_map[cid]:
                        related_map[cid].append(pid)
                        related_ids_needed.add(pid)
            except (GraphStoreError, ValueError):
                logger.warning("Graph store prerequisite lookup failed in quiz_agent; falling back to PostgreSQL edges", exc_info=True)

    # 2. Supplement with PostgreSQL edges (both prerequisite and dependent directions)
    known = list(contexts)
    for model in (ConceptEdge, CrossChapterEdge):
        rows = db.execute(
            select(model.concept_id, model.prerequisite_id).where(
                or_(model.concept_id.in_(known), model.prerequisite_id.in_(known))
            )
        ).all()
        for dep_id, pre_id in rows:
            if dep_id in related_map and pre_id != dep_id and pre_id not in related_map[dep_id]:
                related_map[dep_id].append(pre_id)
                related_ids_needed.add(pre_id)
            if pre_id in related_map and dep_id != pre_id and dep_id not in related_map[pre_id]:
                related_map[pre_id].append(dep_id)
                related_ids_needed.add(dep_id)

    # Load contexts for any related concepts not already in `contexts` (enforcing the exact same book + READY tenancy rules)
    missing = [rid for rid in related_ids_needed if rid not in contexts]
    if missing:
        rel_q = (
            select(Concept, Page, Chapter)
            .join(Page, Page.id == Concept.page_id)
            .join(Chapter, Chapter.id == Page.chapter_id)
            .where(Concept.id.in_(missing), Concept.is_canonical.is_(True), Chapter.status == ChapterStatus.READY)
        )
        if book_ids is not None:
            rel_q = rel_q.where(Chapter.book_id.in_(list(book_ids)))
        for concept, page, chapter in db.execute(rel_q).all():
            contexts[concept.id] = ConceptContext(
                concept_id=concept.id,
                name=concept.name,
                description=concept.description or "",
                page_number=page.page_number or 1,
                page_text=page.content_text or "",
                chapter_id=chapter.id,
                book_id=chapter.book_id,
            )

    # Keep only related concepts that passed the ready + tenant check
    for cid in list(related_map):
        related_map[cid] = [rid for rid in related_map[cid] if rid in contexts and rid != cid]

    return contexts, related_map


def plan_quiz_questions(
    concept_ids: Sequence[uuid.UUID],
    total_questions: int,
    related_map: Optional[dict[uuid.UUID, list[uuid.UUID]]] = None,
) -> list[PlannedQuizItem]:
    """Plans `total_questions` items across `concept_ids` with the 50/30/20 recall/application/cross_concept mix."""
    ordered = list(dict.fromkeys(concept_ids))
    if not ordered or total_questions <= 0:
        return []
    related_map = related_map or {}

    has_any_pair = len(ordered) >= 2 or any(bool(related_map.get(c)) for c in ordered)
    n_recall, n_app, n_cross = question_mix(total_questions, can_cross=has_any_pair)

    if len(ordered) >= total_questions:
        picked = [ordered[int((i + 0.5) * len(ordered) / total_questions)] for i in range(total_questions)]
    else:
        picked = [ordered[i % len(ordered)] for i in range(total_questions)]

    types = (
        [QuestionType.RECALL] * n_recall
        + [QuestionType.APPLICATION] * n_app
        + [QuestionType.CROSS_CONCEPT] * n_cross
    )

    plan: list[PlannedQuizItem] = []
    for idx, (cid, qtype) in enumerate(zip(picked, types)):
        rel_id: Optional[uuid.UUID] = None
        if qtype == QuestionType.CROSS_CONCEPT:
            partners = related_map.get(cid) or [other for other in ordered if other != cid]
            if partners:
                rel_id = partners[idx % len(partners)]
            else:
                qtype = QuestionType.APPLICATION

        if qtype == QuestionType.RECALL:
            fmt = AnswerFormat.MCQ
        elif qtype == QuestionType.CROSS_CONCEPT:
            fmt = AnswerFormat.SHORT_ANSWER if (idx % 2 == 0 or n_cross == 1) else AnswerFormat.MCQ
        else:
            fmt = AnswerFormat.SHORT_ANSWER if idx == n_recall else AnswerFormat.MCQ

        plan.append(
            PlannedQuizItem(
                position=idx,
                concept_id=cid,
                related_concept_id=rel_id,
                question_type=qtype,
                answer_format=fmt,
            )
        )
    return plan


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def _shuffle_mcq(options: list[str], correct_index: int, seed: str) -> tuple[list[str], int]:
    order = list(range(len(options)))
    random.Random(seed).shuffle(order)
    return [options[i] for i in order], order.index(correct_index)


def _build_user_prompt(
    item: PlannedQuizItem,
    primary: ConceptContext,
    related: Optional[ConceptContext],
    already_asked: Sequence[str],
) -> str:
    header = f"QUIZ QUESTION ({item.answer_format.upper()})\nQUESTION TYPE: {item.question_type.upper()}\n"
    body = (
        f"PRIMARY CONCEPT: {primary.name}\n"
        f"PRIMARY DESCRIPTION: {primary.description}\n"
        f"PRIMARY PAGE (p.{primary.page_number}):\n{primary.page_text[: settings.concept_max_chars]}"
    )
    if related is not None:
        body += (
            f"\n\nRELATED CONCEPT: {related.name}\n"
            f"RELATED DESCRIPTION: {related.description}\n"
            f"RELATED PAGE (p.{related.page_number}):\n{related.page_text[: settings.concept_max_chars // 2]}"
        )
    if already_asked:
        body += "\n\nQUESTIONS ALREADY ASKED:\n" + "\n".join(f"- {q}" for q in already_asked)
    return header + body


def generate_quiz_question(
    provider,
    item: PlannedQuizItem,
    primary: ConceptContext,
    related: Optional[ConceptContext] = None,
    already_asked: Sequence[str] = (),
    seed: Optional[str] = None,
) -> GeneratedQuizQuestion:
    """Calls `provider.complete_json`, validates against `McqQuizSchema` or `ShortAnswerQuizSchema` with up to
    `MAX_RETRIES` corrections, and returns `GeneratedQuizQuestion`. Raises `QuizAgentError` if all attempts fail."""
    if not primary.page_text.strip():
        raise QuizAgentError("Cannot generate a quiz question from an empty page.")

    user_prompt = _build_user_prompt(item, primary, related, already_asked)
    system_prompt = MCQ_SYSTEM if item.answer_format == AnswerFormat.MCQ else SHORT_SYSTEM
    last_error = ""

    for attempt in range(MAX_RETRIES + 1):
        prompt = user_prompt + (
            f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
            if attempt
            else ""
        )
        raw = provider.complete_json(system_prompt, prompt)
        cleaned = _strip_fences(raw)
        try:
            if item.answer_format == AnswerFormat.MCQ:
                parsed = McqQuizSchema.model_validate_json(cleaned)
                shuf_seed = seed if seed is not None else json.dumps([str(primary.concept_id), parsed.question, item.position])
                opts, key_idx = _shuffle_mcq(parsed.options, parsed.correct_index, shuf_seed)
                return GeneratedQuizQuestion(
                    concept_id=str(primary.concept_id),
                    related_concept_id=str(related.concept_id) if related else None,
                    question_type=item.question_type,
                    answer_format=AnswerFormat.MCQ,
                    question=parsed.question.strip(),
                    options=opts,
                    correct_index=key_idx,
                    expected_answer=None,
                    explanation=parsed.explanation.strip(),
                )
            else:
                parsed_sa = ShortAnswerQuizSchema.model_validate_json(cleaned)
                return GeneratedQuizQuestion(
                    concept_id=str(primary.concept_id),
                    related_concept_id=str(related.concept_id) if related else None,
                    question_type=item.question_type,
                    answer_format=AnswerFormat.SHORT_ANSWER,
                    question=parsed_sa.question.strip(),
                    options=None,
                    correct_index=None,
                    expected_answer=parsed_sa.expected_answer.strip(),
                    explanation=parsed_sa.explanation.strip(),
                )
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue

    raise QuizAgentError("Couldn't generate this quiz question right now. Please try again in a moment.")


def student_view(q: GeneratedQuizQuestion) -> dict:
    """Everything a student may see BEFORE submitting: no `correct_index`, no `expected_answer`, no `explanation`."""
    return {
        "concept_id": q.concept_id,
        "related_concept_id": q.related_concept_id,
        "question_type": q.question_type,
        "answer_format": q.answer_format,
        "question": q.question,
        "options": list(q.options) if q.options is not None else None,
    }