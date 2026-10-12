"""Turning what the student sent (typed text, or the OCR text of a photo) into something searchable.

Decided in Phase 3 (see Phases.md "Settled before building"): the photo is read by the same OCR service as front pages
and is NOT stored. By length of the text read:
  < PHOTO_MIN_WORDS      too_short -> "retake the photo" (a bad scan would only retrieve noise)
  < PHOTO_PAGE_WORDS     doubt     -> the text IS the doubt, searched as it is
  >= PHOTO_PAGE_WORDS    page      -> a whole page: matched to its page in the book, then the student picks the concept
                                      that confused them (searching a whole page as a "question" is meaningless)
Typed text is never "too short" (a single word is a legitimate doubt); only an empty message is. It can still be a page."""
from dataclasses import dataclass

from app.core.config import settings
from app.pipeline.fingerprint import tokenize

TOO_SHORT, DOUBT, PAGE = "too_short", "doubt", "page"


@dataclass
class DoubtInput:
    kind: str
    words: int
    text: str  # cleaned text to search with (empty when too_short)


def classify_doubt_text(text: str, from_photo: bool = False) -> DoubtInput:
    clean = " ".join((text or "").split())
    words = len(tokenize(clean))
    if words == 0 or (from_photo and words < settings.photo_min_words):
        return DoubtInput(TOO_SHORT, words, "")
    if words >= settings.photo_page_words:
        return DoubtInput(PAGE, words, clean)
    return DoubtInput(DOUBT, words, clean)


RETAKE_MESSAGE = "We couldn't read enough of that photo. Please retake it in good light, with the page flat and filling the frame."
