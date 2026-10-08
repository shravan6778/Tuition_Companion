"""Page-level concept extraction: LLM call + schema validation + correction retries (Rules.md §3)."""
import re
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You are an educational curriculum parser. From one textbook page, extract the concepts a student must "
    "understand. Reply with JSON only, shaped exactly as: "
    '{"concepts":[{"name":str,"description":str,"learning_objectives":[str],"prerequisites":[str]}]}. '
    "Use 0-10 concepts (an empty list is fine for a cover, index or blank page). Concept names must be unique "
    "on the page. 'prerequisites' are names of earlier concepts a student needs first, only if the text "
    "mentions or clearly implies them. Use only what the page supports; add no outside knowledge. "
    "A concept is an IDEA a student must understand (a definition, law, process, structure, term). Hands-on "
    "activities, experiments, figures, exercises, questions and boxed trivia are NOT concepts: if you list one, "
    "set its \"kind\" to \"activity\" or \"exercise\"; boxed side notes (biographies, trivia, 'Threads of Curiosity', "
    "ethics or career notes) get \"sidebar\"; otherwise use \"idea\". Name each idea in its plain, "
    "standard textbook form (e.g. 'Cell membrane', not 'Cell Membrane Structure and Function Overview'). "
    "Also set the top-level \"page_kind\": \"content\" for pages that teach, \"recap\" for chapter "
    "summaries / 'At a Glance' pages, \"exercise\" for question and exercise pages, \"other\" for covers, "
    "indexes and blanks. Full shape: "
    '{"page_kind":str,"concepts":[{"name":str,"kind":str,"description":str,"learning_objectives":[str],"prerequisites":[str]}]}.'
)

DROPPED_KINDS = {"activity", "exercise", "figure", "question", "sidebar"}
NON_TEACHING_PAGES = {"recap", "exercise"}  # their concepts only repeat or test earlier ones
_ACTIVITY_NAME = re.compile(r"\b(experiments?|activity|activities|exercises?)\b|^\s*(fig(ure)?\.?|question|let'?s)\b", re.I)
_RECAP_HEADING = re.compile(
    r"^\W*(at a glance|chapter summary|summary|key points|points to remember|let'?s recall|"
    r"exercises?|review questions|questions)\b", re.I | re.M,
)


def looks_like_activity(name: str) -> bool:
    """Deterministic backstop for the prompt rule: an experiment or exercise title is not an idea."""
    return bool(_ACTIVITY_NAME.search(name or ""))


def looks_like_recap_page(text: str) -> bool:
    """A page that STARTS (first 250 chars, at a line start) with a summary / exercise heading."""
    return bool(_RECAP_HEADING.search((text or "")[:250]))


class ConceptExtractionError(ProcessingError):
    pass


class ExtractedConcept(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    kind: str = Field(default="idea", max_length=20)
    description: str = Field(default="", max_length=600)
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class PageConcepts(BaseModel):
    page_kind: str = Field(default="content", max_length=20)
    concepts: list[ExtractedConcept] = Field(default_factory=list, max_length=25)


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


@dataclass
class PageExtraction:
    concepts: list[ExtractedConcept] = field(default_factory=list)
    dropped: int = 0  # activities / exercises / recap concepts left out on purpose
    page_kind: str = "content"


def _filter(result: PageConcepts, page_text: str) -> PageExtraction:
    kind = (result.page_kind or "content").strip().lower()
    if kind in NON_TEACHING_PAGES or looks_like_recap_page(page_text):
        return PageExtraction([], len(result.concepts), kind if kind in NON_TEACHING_PAGES else "recap")
    kept = [
        c for c in result.concepts
        if (c.kind or "idea").strip().lower() not in DROPPED_KINDS and not looks_like_activity(c.name)
    ]
    return PageExtraction(kept, len(result.concepts) - len(kept), kind)


def extract_page_concepts(provider, page_text: str) -> list[ExtractedConcept]:
    return extract_page(provider, page_text).concepts


def extract_page(provider, page_text: str) -> PageExtraction:
    """Raises ConceptExtractionError after MAX_RETRIES failed corrections. Never returns a silent [] on failure.
    Activities, exercises and the concepts of recap/exercise pages are filtered out (counted in `dropped`)."""
    if not page_text.strip():
        return PageExtraction()
    user = f"PAGE TEXT:\n{page_text[: settings.concept_max_chars]}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            return _filter(PageConcepts.model_validate_json(_strip_fences(raw)), page_text)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
    raise ConceptExtractionError("Couldn't build the concept map for a page. Please retry, or re-upload a clearer file.")
