"""Which answer styles a subject allows.

Typing is the baseline everywhere. Maths-type subjects (worked steps, symbols, diagrams) get NO long answers and NO spoken
answers: speech recognition cannot hear "x squared minus 4" reliably, and a long written answer is not how maths is marked.
Photo answers for working and diagrams are a later option; they are not part of this version.

The subject comes from the book (quizzes) or the assignment (checks) and is free text, so the match is by whole words,
case-insensitive: "Mathematics", "Maths (Class 9)" and "Applied Mathematics" all count; "Mathematical Reasoning" does not
unless the list says so. Teachers can extend the list with MATH_LIKE_SUBJECTS."""
import re
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings


def _words(text: str) -> set[str]:
    # split on separators, not on "word characters": \w would cut Hindi and Telugu words at their vowel signs
    return {w for w in re.split(r"[\s,;:()\[\]/\-\u2013.&]+", (text or "").casefold()) if w}


def is_math_like(subject: Optional[str]) -> bool:
    if not subject or not subject.strip():
        return False
    listed = {t.strip().casefold() for t in settings.math_like_subjects.split(",") if t.strip()}
    return bool(_words(subject) & listed) or subject.strip().casefold() in listed


@dataclass(frozen=True)
class AnswerPolicy:
    long_allowed: bool
    voice_allowed: bool


def policy_for(subject: Optional[str]) -> AnswerPolicy:
    allowed = not is_math_like(subject)
    return AnswerPolicy(long_allowed=allowed, voice_allowed=allowed)


def csv_list(value: str) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def speech_languages() -> list[str]:
    return csv_list(settings.speech_languages)
