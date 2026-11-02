"""The comprehension check that follows "mark complete". Pure functions plus one validated model call per question.

Decided in Phase 3 (Phases.md "Settled before building"):
  * size    : one question per concept, never fewer than CHECK_MIN_QUESTIONS and never more than CHECK_MAX_QUESTIONS.
              Fewer concepts than the floor -> several questions on the same concept; more than the ceiling -> concepts
              the student asked doubts about or scored weak on come first, then the rest in book order.
  * type    : mostly multiple choice (exactly 4 options, one correct), graded in plain code (Rules.md §1), never a model. A configurable
              share of the questions (CHECK_SHORT_SHARE, CHECK_LONG_SHARE) are written or spoken answers marked against a rubric of
              key points; a maths-type subject gets no long answers (`plan_formats`).
  * source  : the question is written from the concept's description and the text of ITS OWN page (grounded), checked
              against a schema, retried twice with a correction prompt like concept extraction. For an item-level
              assignment the picked examples / questions / figures that test the concept are added as `focus`, so the
              question is about what the teacher actually set, not about the whole page.
  * no leak : `student_view` has no key and no explanation; those are only revealed by `grade` after submission.
  * order   : the model tends to put the right answer first, so options are shuffled in code (seeded per question id)."""
import json
import random
import re
from dataclasses import dataclass
from typing import Optional, Sequence

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.assessment import rubric
from app.core.config import settings
from app.core.errors import ProcessingError
from app.models import AnswerFormat

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


WRITTEN_SYSTEM = (
    "You write ONE {kind} comprehension question for a school student, about ONE concept, using only the textbook page given. "
    "Reply with JSON only: "
    '{{"question":str,"expected_answer":str,"key_points":[{{"point":str,"marks":int}}],"explanation":str}}. '
    "{shape} 'key_points' is the marking rubric: {points} separate ideas a good answer contains, each a short English sentence "
    "taken from the page, each worth 1 to 3 marks (1 = a detail, 3 = the central idea), at most {cap} marks in total, no overlap. "
    "'expected_answer' is a model answer that covers every key point. 'explanation' is one or two sentences of reasoning. Test "
    "understanding, not copying: do not quote the page's own sentence as the question. Add no outside knowledge. If a list of "
    "questions already asked is given, ask about a different aspect."
)
_KIND = {
    AnswerFormat.SHORT_ANSWER: ("short-answer", "The student answers in one or two sentences.", "1 to 4", rubric.SHORT_MAX_MARKS),
    AnswerFormat.LONG_ANSWER: ("long-answer", "The student answers in a paragraph: ask them to explain, describe or compare.", "3 to 8", rubric.LONG_MAX_MARKS),
}


class CheckQuestionError(ProcessingError):
    pass


class WrittenSchema(BaseModel):
    question: str = Field(min_length=8, max_length=500)
    expected_answer: str = Field(min_length=5, max_length=1500)
    key_points: list[rubric.KeyPoint] = Field(min_length=1, max_length=8)
    explanation: str = Field(default="", max_length=500)


@dataclass
class WrittenQuestion:
    """A short or long question with its rubric. Server-side only until the check is submitted."""
    concept_id: str
    answer_format: str
    question: str
    expected_answer: str
    key_points: list
    explanation: str


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


def plan_formats(n: int, allow_long: bool = True) -> list[str]:
    """The answer format of each of `n` questions: `round(n * CHECK_SHORT_SHARE)` short and `round(n * CHECK_LONG_SHARE)` long
    answers, spread through the check (long ones towards the end), the rest multiple choice. A tiny check can round to no written
    question at all. `allow_long=False` (a maths-type subject) turns the long ones into short ones. At least one question stays
    multiple choice, so every check has some part that is marked in code."""
    n_long = round(n * settings.check_long_share) if allow_long else 0
    n_short = round(n * settings.check_short_share) + (0 if allow_long else round(n * settings.check_long_share))
    while n_long + n_short > max(n - 1, 0):
        if n_short > 0:
            n_short -= 1
        else:
            n_long -= 1
    formats = [AnswerFormat.MCQ] * n
    total = n_long + n_short
    slots = sorted({min(n - 1, int((k + 0.5) * n / total)) for k in range(total)}) if total else []
    for rank, slot in enumerate(slots):
        formats[slot] = AnswerFormat.SHORT_ANSWER if rank < n_short else AnswerFormat.LONG_ANSWER
    return formats


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
                      already_asked: Sequence[str] = (), seed: Optional[str] = None, focus: str = "") -> Question:
    """Raises CheckQuestionError after MAX_RETRIES failed corrections (the caller shows "couldn't generate this right
    now", never a blank question or a stale one)."""
    user = f"CHECK QUESTION\nCONCEPT: {name}\nDESCRIPTION: {description or ''}\nPAGE:\n{(page_text or '')[: settings.concept_max_chars]}"
    if focus.strip():
        user += ("\nASSIGNED ITEMS (the teacher set these; ask about the idea they practise, from the page above, and do "
                 "not copy them or reveal their solutions):\n" + focus.strip()[: settings.concept_max_chars])
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


def generate_written_question(provider, fmt: str, concept_id: str, name: str, description: str, page_text: str,
                              already_asked: Sequence[str] = (), focus: str = "") -> WrittenQuestion:
    """A short or long question with its key-point rubric, from the concept's own page. Validated, corrected twice, then
    CheckQuestionError (the caller marks it failed: never a blank or stale question)."""
    kind, shape, points, cap = _KIND[fmt]
    system = WRITTEN_SYSTEM.format(kind=kind, shape=shape, points=points, cap=cap)
    user = f"CHECK QUESTION ({fmt.upper()})\nCONCEPT: {name}\nDESCRIPTION: {description or ''}\nPAGE:\n{(page_text or '')[: settings.concept_max_chars]}"
    if focus.strip():
        user += ("\nASSIGNED ITEMS (the teacher set these; ask about the idea they practise, from the page above, and do "
                 "not copy them or reveal their solutions):\n" + focus.strip()[: settings.concept_max_chars])
    if already_asked:
        user += "\nQUESTIONS ALREADY ASKED:\n" + "\n".join(f"- {q}" for q in already_asked)
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user + (f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly." if attempt else "")
        raw = provider.complete_json(system, prompt)
        try:
            parsed = WrittenSchema.model_validate_json(_strip_fences(raw))
            points_ok = rubric.check_rubric(parsed.key_points, fmt)
        except (ValidationError, ValueError) as exc:
            last_error = ("; ".join(e["msg"] for e in exc.errors()) if isinstance(exc, ValidationError) else str(exc))[:300]
            continue
        return WrittenQuestion(concept_id, fmt, parsed.question.strip(), parsed.expected_answer.strip(), rubric.to_json(points_ok), parsed.explanation.strip())
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
