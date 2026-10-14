"""Photographed doubts (Phase 3 step 4). The photo is read by OCR and is NEVER stored: only the text read survives, and
only as the doubt's text. Rules (Phases.md "Settled before building"):

  OCR text under PHOTO_MIN_WORDS   -> too_short: "retake the photo" (a bad scan would only retrieve noise); nothing is saved
  PHOTO_MIN_WORDS .. PHOTO_PAGE_WORDS-1 -> doubt: the text IS the doubt, handled exactly like a typed one (retrieval + Tutor)
  PHOTO_PAGE_WORDS or more         -> page: a whole page is not a question. It is matched to its page in the student's books and the student
                                      picks the concept that confused them (POST /student/doubts with that concept_id). No doubt is
                                      saved until they pick.
Only photos of pages already inside the student's linked, processed books get an answer; an unseen page is `not_in_book`
(the existing "ask your teacher to add a chapter" route), never processed on the fly."""
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.doubts import service
from app.doubts.retrieval import GROUNDED, RetrievalResult, concepts_on_page, retrieve
from app.models import Assignment, Chapter, Concept, User
from app.ocr import get_ocr_provider

logger = logging.getLogger(__name__)

FAKE_OCR_MARKER = "[fake-ocr]"  # the development stand-in does no real OCR on images: never treat its placeholder as a doubt
TEXT_CAP = 1000  # same as a typed doubt


class PhotoUnreadable(Exception):
    """The OCR service failed or is switched off. The student is told to try again later, nothing is saved."""


def read_photo(data: bytes, ext: str) -> str:
    try:
        text = get_ocr_provider().extract(data, ext).text or ""
    except Exception as exc:  # a provider that is down, misconfigured or rejects the image reads as "unavailable", never a 500
        logger.warning("Doubt photo could not be read", exc_info=True)
        raise PhotoUnreadable(str(exc)) from exc
    if text.lstrip().startswith(FAKE_OCR_MARKER):
        raise PhotoUnreadable("OCR_PROVIDER is 'fake': images are not really read")
    return " ".join(text.split())


@dataclass
class PagePick:
    result: RetrievalResult
    page_id: Optional[str] = None
    concepts: list[Concept] = field(default_factory=list)


def match_page(db: Session, student: User, text: str, assignment: Optional[Assignment], chapter: Optional[Chapter] = None) -> PagePick:
    """A whole photographed page: find the page in the student's books and list the concepts on it that the student can pick.
    Same scope and tenancy rules as any doubt (the student's own linked books; the assignment's scope when there is one)."""
    scope = service.assignment_scope(db, assignment) if assignment is not None else service.chapter_scope(chapter) if chapter is not None else None
    embedder, store = service._providers()
    result = retrieve(db, text, embedder=embedder, store=store, book_ids=service.linked_book_ids(db, student), scope=scope)
    if result.status != GROUNDED or not result.pages:
        return PagePick(result)
    page = result.pages[0]
    concepts = concepts_on_page(db, uuid.UUID(page.page_id))
    if scope is not None:  # a narrow assignment: only the concepts it covers can be picked
        concepts = [c for c in concepts if scope.has_concept(str(c.id), page.chapter_id)]
    return PagePick(result, page.page_id, concepts)
