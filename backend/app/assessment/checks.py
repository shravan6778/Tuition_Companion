"""The comprehension check that follows "mark complete". Pure functions plus one validated model call per question.

Decided in Phase 3 (Phases.md "Settled before building"):
  * size    : one question per concept, never fewer than CHECK_MIN_QUESTIONS and never more than CHECK_MAX_QUESTIONS.
              Fewer concepts than the floor -> several questions on the same concept; more than the ceiling -> concepts
              the student asked doubts about or scored weak on come first, then the rest in book order.
  * type    : multiple choice only (exactly 4 options, one correct), so grading is plain code (Rules.md §1), never a model.
  * source  : the question is written from the concept's description and the text of ITS OWN page (grounded), checked
              against a schema, retried twice with a correction prompt like concept extraction.
  * no leak : `student_view` has no key and no explanation; those are only revealed by `grade` after submission.
  * order   : the model tends to put the right answer first, so options are shuffled in code (seeded per question id)."""
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Sequence

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.config import settings
from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You write ONE multiple-choice comprehension question for a school student, about ONE concept, using only the "
    "textbook page given. Reply with JSON only: "
    '{"question":str,"options":[str,str,str,str],"correct_index":int,"explanation":str}. '
    "Exactly 4 options, exactly one correct, the others plausible but clearly wrong according to the page. Test "
    "understanding, not copying: do not quote the page's own sentence as the question. Do not use 'all of the above', "
    "'none of the above' or 'both A and B'. The explanation is one or two sentences saying why the answer is right. "
    "Add no outside knowledge. If a list of questions already asked is given, ask about a different aspect."
)


class CheckQuestionError(ProcessingError):
    pass


class McqSchema(BaseModel):
    question: str = Field(min_length=8, max_length=400)
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


@dataclass
class Question:
    """The server-side record: includes the key. Never send this to a student before submission."""
    concept_id: str
    question: str
    options: list[str]
    correct_index: int
    explanation: str


def question_count(n_concepts: int) -> int:
    return max(settings.check_min_questions, min(settings.check_max_questions, n_concepts))


def plan_check(concept_ids: Sequence[str], priority_ids: Sequence[str] = ()) -> list[str]:
    """The concept each question is about, in order. Repeats a concept only to reach the floor."""
    unique = list(dict.fromkeys(concept_ids))
    if not unique:
        return []
    n = question_count(len(unique))
    if len(unique) > n:
        first = [c for c in dict.fromkeys(priority_ids) if c in set(unique)][:n]
        rest = [c for c in unique if c not in set(first)]
        need = n - len(first)
        # The rest are SPREAD evenly through the scope, not taken from its start: a chapter check that only ever asked
        # about the first ten concepts would never test the later pages (real-data finding, Oct 2026).
        spread = [rest[int((i + 0.5) * len(rest) / need)] for i in range(need)] if need else []
        chosen_set = set(first) | set(spread)
        return [c for c in unique if c in chosen_set]  # back into book order
    return [unique[i % len(unique)] for i in range(n)]


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def generate_question(provider, concept_id: str, name: str, description: str, page_text: str,
                      already_asked: Sequence[str] = (), seed: Optional[str] = None) -> Question:
    """Raises CheckQuestionError after MAX_RETRIES failed corrections (the caller shows "couldn't generate this right
    now", never a blank question or a stale one)."""
    user = f"CHECK QUESTION\nCONCEPT: {name}\nDESCRIPTION: {description or ''}\nPAGE:\n{(page_text or '')[: settings.concept_max_chars]}"
    if already_asked:
        user += "\nQUESTIONS ALREADY ASKED:\n" + "\n".join(f"- {q}" for q in already_asked)
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user + (f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly." if attempt else "")
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            parsed = McqSchema.model_validate_json(_strip_fences(raw))
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        return shuffle_options(Question(concept_id, parsed.question.strip(), parsed.options, parsed.correct_index, parsed.explanation.strip()), seed)
    raise CheckQuestionError("Couldn't generate this check right now. Please try again in a moment.")


def shuffle_options(q: Question, seed: Optional[str]) -> Question:
    order = list(range(len(q.options)))
    random.Random(seed if seed is not None else json.dumps([q.concept_id, q.question])).shuffle(order)
    return Question(q.concept_id, q.question, [q.options[i] for i in order], order.index(q.correct_index), q.explanation)


def student_view(q: Question) -> dict:
    """Everything a student may see BEFORE submitting: no key, no explanation."""
    return {"concept_id": q.concept_id, "question": q.question, "options": list(q.options)}


@dataclass
class Graded:
    concept_id: str
    correct: bool
    correct_index: int
    explanation: str


def grade(q: Question, chosen_index: Optional[int]) -> Graded:
    """Deterministic. An unanswered or out-of-range choice is simply wrong."""
    ok = isinstance(chosen_index, int) and not isinstance(chosen_index, bool) and chosen_index == q.correct_index
    return Graded(q.concept_id, ok, q.correct_index, q.explanation)


def concept_scores(graded: Sequence[Graded]) -> dict[str, float]:
    """Share correct per concept (0..1). One concept asked twice and answered once right scores 0.5."""
    totals: dict[str, list[int]] = {}
    for g in graded:
        t = totals.setdefault(g.concept_id, [0, 0])
        t[0] += 1 if g.correct else 0
        t[1] += 1
    return {cid: right / asked for cid, (right, asked) in totals.items()}
