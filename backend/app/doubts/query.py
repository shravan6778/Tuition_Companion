"""Helpers for classifying and normalizing student doubts.

Typed doubts and photographed doubts use the same text-classification rules.
Photographs are OCR'd and are never stored as image data.

Doubt reuse uses a normalized textual representation. The normalization
removes differences such as case, punctuation and repeated whitespace.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from app.core.config import settings
from app.pipeline.fingerprint import tokenize


TOO_SHORT = "too_short"
DOUBT = "doubt"
PAGE = "page"

RETAKE_MESSAGE = (
    "We couldn't read enough of that photo. Please retake it in good light, "
    "with the page flat and filling the frame."
)


@dataclass
class DoubtInput:
    """Result of classifying text received from the student."""

    kind: str
    words: int
    text: str


def classify_doubt_text(
    text: str,
    from_photo: bool = False,
) -> DoubtInput:
    """Classify OCR/text input as too-short, doubt, or whole-page text."""

    clean = " ".join((text or "").split())
    words = len(tokenize(clean))

    # Typed text may be a single word, so the photo minimum only applies
    # when the input actually came from a photograph.
    if words == 0 or (
        from_photo and words < settings.photo_min_words
    ):
        return DoubtInput(
            kind=TOO_SHORT,
            words=words,
            text="",
        )

    # Long OCR text is treated as a photographed page rather than as a
    # student's actual question.
    if words >= settings.photo_page_words:
        return DoubtInput(
            kind=PAGE,
            words=words,
            text=clean,
        )

    return DoubtInput(
        kind=DOUBT,
        words=words,
        text=clean,
    )


def normalize_doubt_text(text: str) -> str:
    """Return the canonical text used for doubt reuse.

    Examples:

        "  WHAT is a tissue??? "
        -> "what is a tissue"

        "WHAT   IS a tissue!"
        -> "what is a tissue"

    Unicode NFKC normalization is applied before tokenization so visually
    equivalent Unicode forms are treated consistently.
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text)

    # tokenize() performs case-folding, punctuation removal and whitespace
    # collapsing.
    return " ".join(tokenize(normalized))[:1000]


def doubt_tokens(text: str) -> list[str]:
    """Return normalized tokens for controlled doubt-reuse matching."""

    normalized = normalize_doubt_text(text)

    if not normalized:
        return []

    return normalized.split()