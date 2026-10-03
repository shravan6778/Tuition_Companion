"""Page-level concept extraction: LLM call + schema validation + correction retries (Rules.md §3)."""
import re

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
    "mentions or clearly implies them. Use only what the page supports; add no outside knowledge."
)


class ConceptExtractionError(ProcessingError):
    pass


class ExtractedConcept(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=600)
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class PageConcepts(BaseModel):
    concepts: list[ExtractedConcept] = Field(default_factory=list, max_length=25)


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def extract_page_concepts(provider, page_text: str) -> list[ExtractedConcept]:
    """Raises ConceptExtractionError after MAX_RETRIES failed corrections. Never returns a silent [] on failure."""
    if not page_text.strip():
        return []
    user = f"PAGE TEXT:\n{page_text[: settings.concept_max_chars]}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            return PageConcepts.model_validate_json(_strip_fences(raw)).concepts
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
    raise ConceptExtractionError("Couldn't build the concept map for a page. Please retry, or re-upload a clearer file.")
