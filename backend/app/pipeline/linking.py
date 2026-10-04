"""Chapter-level LLM linking pass: which concepts of one chapter are prerequisites of which.

The model only ever sees and returns NUMBERS from the list we give it, so it cannot invent concepts
or misspell names; anything out of range fails validation and is retried (Rules.md §3)."""
from pydantic import BaseModel, Field, ValidationError

from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You are a curriculum analyst. You get the numbered concepts of ONE textbook chapter, in the order they "
    "appear. For each concept, decide which OTHER listed concepts a student must understand first. "
    "Use only the given numbers. Include only direct, genuinely necessary prerequisites (usually 0-3 per "
    "concept); never list a concept as its own prerequisite. Reply with JSON only, shaped exactly as: "
    '{"edges":[{"concept":<number>,"prerequisites":[<number>,...]}]}. Omit concepts with no prerequisites.'
)


class LinkingError(ProcessingError):
    pass


class LinkItem(BaseModel):
    concept: int
    prerequisites: list[int] = Field(default_factory=list)


class LinkResult(BaseModel):
    edges: list[LinkItem]  # required: a reply without it is invalid, not "no edges"


def _clip(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _check_ranges(result: LinkResult, n: int) -> str:
    for item in result.edges:
        for number in [item.concept, *item.prerequisites]:
            if not 1 <= number <= n:
                return f"number {number} is not in the list (valid numbers are 1 to {n})"
    return ""


def propose_links(provider, concepts: list[tuple[str, str]]) -> list[tuple[int, int]]:
    """concepts: [(name, description)] in chapter order. Returns 0-based (concept_index, prerequisite_index)
    pairs, de-duplicated, with self-links dropped. Raises LinkingError after MAX_RETRIES failed corrections."""
    n = len(concepts)
    listing = "\n".join(f"{i}. {_clip(name, 80)} - {_clip(desc, 120)}" for i, (name, desc) in enumerate(concepts, 1))
    user = f"CONCEPTS:\n{listing}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += f"\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            text = raw.strip()
            if text.startswith("```"):
                text = text.strip("`").removeprefix("json").strip()
            result = LinkResult.model_validate_json(text)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        problem = _check_ranges(result, n)
        if problem:
            last_error = problem
            continue
        pairs: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        for item in result.edges:
            for prereq in item.prerequisites:
                pair = (item.concept - 1, prereq - 1)
                if pair[0] != pair[1] and pair not in seen:
                    seen.add(pair)
                    pairs.append(pair)
        return pairs
    raise LinkingError("Couldn't work out how the concepts in this chapter depend on each other. Please retry.")
