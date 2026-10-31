"""Page-level extraction of concepts plus mixed textbook items."""
import re
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

from app.core.config import settings
from app.core.errors import ProcessingError

MAX_RETRIES = 2

# Pages in the last SUMMARY_TAIL_FROM fraction of a chapter that look like a summary are
# treated as recap/exercise pages (used by backfill_page_kind and the orchestrator).
SUMMARY_TAIL_FROM = 0.6

SYSTEM = (
    "You are an educational textbook parser. Extract BOTH concepts and page items. Reply with JSON only. "
    'Shape: {"page_kind":"content|recap|exercise|other","concepts":[{"name":str,"description":str,'
    '"learning_objectives":[str],"prerequisites":[str]}],"items":[{"kind":"concept|example|exercise_question|diagram|activity|sidebar",'
    '"label":str|null,"text":str,"solution_text":str|null,"concept_names":[str]}]}. '
    "A page is mixed: page_kind is only its dominant type, never a reason to discard items. "
    "Concepts are ideas a student must understand. Items preserve examples, worked examples, exercises, questions, "
    "activities/experiments, figures/diagrams, and boxed sidebars. Do not discard non-concept material. "
    "For examples use labels such as 'Example 3'; for exercises use 'Exercise 9.5' or 'Ex 9.5 Q4'; "
    "for figures use 'Fig. 9.5'. Keep item text faithful and concise, and include a solution/explanation when "
    "the page provides one. concept_names must contain only concepts extracted on this page that the item explains/tests. "
    "Use only the page text; do not invent missing solutions. Empty arrays are valid for blank/index/cover pages."
)
_PAGE_KIND = ("content", "recap", "exercise", "other")
_ITEM_KINDS = ("concept", "example", "exercise_question", "diagram", "activity", "sidebar")

_EXAMPLE_RE = re.compile(r"\bExample\s+(\d+(?:\.\d+)*)\b", re.I)
_EXERCISE_RE = re.compile(r"\bExercise\s+(\d+(?:\.\d+)*)\b", re.I)
_FIGURE_RE = re.compile(r"\bFig(?:ure)?\.?\s*(\d+(?:\.\d+)*)\b", re.I)
_ACTIVITY_RE = re.compile(r"^\s*(experiment|activity|activities|investigate|try this|let'?s)\b", re.I)


class ExtractedItem(BaseModel):
    kind: str = Field(default="concept", max_length=24)
    label: str | None = Field(default=None, max_length=120)
    text: str = Field(default="", max_length=6000)
    solution_text: str | None = Field(default=None, max_length=6000)
    concept_names: list[str] = Field(default_factory=list, max_length=20)


class ExtractedConcept(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=600)
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class PageConcepts(BaseModel):
    page_kind: str = Field(default="content", max_length=20)
    concepts: list[ExtractedConcept] = Field(default_factory=list, max_length=25)
    items: list[ExtractedItem] = Field(default_factory=list, max_length=40)


class ConceptExtractionError(ProcessingError):
    pass


@dataclass
class PageExtraction:
    concepts: list[ExtractedConcept] = field(default_factory=list)
    items: list[ExtractedItem] = field(default_factory=list)
    dropped: int = 0  # retained for backwards-compatible pipeline counters
    page_kind: str = "content"


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def normalize_page_kind(kind: str | None) -> str:
    kind = (kind or "content").strip().lower()
    return kind if kind in _PAGE_KIND else "content"


def heading_page_kind(text: str) -> str | None:
    head = (text or "")[:250]
    if re.search(r"^\W*(exercises?|review questions|questions)\b", head, re.I | re.M):
        return "exercise"
    if re.search(r"^\W*(at a glance|chapter summary|summary|key points|points to remember)\b", head, re.I | re.M):
        return "recap"
    return None


def looks_like_summary_page(text: str) -> bool:
    return bool(re.search(r"^\W*(at a glance|chapter summary|summary|key points|points to remember)\b",
                          (text or "")[:250], re.I | re.M))


def looks_like_recap_page(text: str) -> bool:
    return bool(re.search(r"^\W*(at a glance|chapter summary|summary|key points|points to remember|"
                          r"let'?s recall|exercises?|review questions|questions)\b",
                          (text or "")[:250], re.I | re.M))


def looks_like_activity(name: str) -> bool:
    return bool(_ACTIVITY_RE.search(name or ""))


def extract_item_labels(text: str) -> list[str]:
    labels: list[str] = []
    for regex, prefix in ((_EXAMPLE_RE, "Example"), (_EXERCISE_RE, "Exercise"), (_FIGURE_RE, "Fig.")):
        for m in regex.finditer((text or "")[:4000]):
            label = f"{prefix} {m.group(1)}"
            if label not in labels:
                labels.append(label)
    return labels


def _regex_proposals(text: str) -> list[ExtractedItem]:
    """Deterministic proposal backstop. These are proposals, not replacements for model extraction."""
    out: list[ExtractedItem] = []
    for regex, kind, prefix in (
        (_EXAMPLE_RE, "example", "Example"),
        (_EXERCISE_RE, "exercise_question", "Exercise"),
        (_FIGURE_RE, "diagram", "Fig."),
    ):
        for m in regex.finditer(text or ""):
            label = f"{prefix} {m.group(1)}"
            if any((x.label or "").casefold() == label.casefold() for x in out):
                continue
            start = m.start()
            snippet = (text[max(0, start): start + 1200]).strip()
            out.append(ExtractedItem(kind=kind, label=label, text=snippet, concept_names=[]))
    return out[:20]


def _normalize_item(item: ExtractedItem) -> ExtractedItem:
    kind = (item.kind or "concept").strip().lower()
    if kind == "exercise":
        kind = "exercise_question"
    if kind == "figure":
        kind = "diagram"
    if kind == "question":
        kind = "exercise_question"
    if kind not in _ITEM_KINDS:
        kind = "sidebar"
    return item.model_copy(update={"kind": kind, "label": (item.label or "").strip() or None,
                                   "text": (item.text or "").strip()})


def _merge_proposals(items: list[ExtractedItem], text: str) -> list[ExtractedItem]:
    result = [_normalize_item(x) for x in items if (x.text or "").strip()]
    keys = {(x.kind, (x.label or "").casefold()) for x in result if x.label}
    for proposal in _regex_proposals(text):
        key = (proposal.kind, (proposal.label or "").casefold())
        if key not in keys:
            result.append(proposal)
            keys.add(key)
    return result[:40]


def _filter(result: PageConcepts, page_text: str) -> PageExtraction:
    kind = normalize_page_kind(result.page_kind)
    items = _merge_proposals(result.items, page_text)
    # Every concept is also represented as an item so pages always have a uniform item stream.
    for c in result.concepts:
        if not any(i.kind == "concept" and (i.label or "").casefold() == c.name.casefold() for i in items):
            items.insert(0, ExtractedItem(kind="concept", label=c.name, text=c.description, concept_names=[c.name]))
    return PageExtraction(result.concepts, items, 0, heading_page_kind(page_text) or kind)


def extract_page_concepts(provider, page_text: str) -> list[ExtractedConcept]:
    return extract_page(provider, page_text).concepts


def extract_page(provider, page_text: str) -> PageExtraction:
    if not (page_text or "").strip():
        return PageExtraction()
    user = f"PAGE TEXT:\n{page_text[:settings.concept_max_chars]}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            parsed = PageConcepts.model_validate_json(_strip_fences(raw))
            return _filter(parsed, page_text)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
    raise ConceptExtractionError("Couldn't build the concept/item map for a page. Please retry, or re-upload a clearer file.")
