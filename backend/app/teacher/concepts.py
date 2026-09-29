import json
import re

from pydantic import BaseModel, Field, ValidationError, model_validator

from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You extract a concept graph from textbook chapter text. Reply with JSON only, shaped exactly as: "
    '{"concepts":[{"name":str,"summary":str,"prerequisites":[str]}]}. '
    "Use 5-25 concepts a student must understand. Names must be unique. Each prerequisite must be the "
    "exact name of another concept in the list. No cycles. Use only what the text supports; do not add "
    "outside knowledge."
)


class ConceptExtractionError(ProcessingError):
    pass


class Concept(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    summary: str = Field(min_length=5, max_length=400)
    prerequisites: list[str] = Field(default_factory=list)


class ConceptGraph(BaseModel):
    concepts: list[Concept] = Field(min_length=1, max_length=60)

    @model_validator(mode="after")
    def _check_graph(self):
        key = lambda s: s.strip().lower()
        names = [key(c.name) for c in self.concepts]
        if len(set(names)) != len(names):
            raise ValueError("concept names must be unique")
        known = set(names)
        deps = {}
        for c in self.concepts:
            for p in c.prerequisites:
                if key(p) not in known:
                    raise ValueError(f"unknown prerequisite '{p}' on concept '{c.name}'")
                if key(p) == key(c.name):
                    raise ValueError(f"concept '{c.name}' lists itself as a prerequisite")
            deps[key(c.name)] = {key(p) for p in c.prerequisites}
        # Kahn's algorithm: anything left over is part of a cycle.
        remaining = dict(deps)
        while True:
            free = [n for n, d in remaining.items() if not d]
            if not free:
                break
            for n in free:
                del remaining[n]
            for d in remaining.values():
                d.difference_update(free)
        if remaining:
            raise ValueError("prerequisites contain a cycle")
        return self


def _strip_fences(raw: str) -> str:
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())


def extract_concepts(provider, text: str, max_chars: int) -> tuple[dict, bool, str | None]:
    """Returns (graph_dict, needs_review, review_note). Raises ConceptExtractionError."""
    truncated = len(text) > max_chars
    user = f"CHAPTER TEXT:\n{text[:max_chars]}"

    last_error = ""
    graph = None
    for attempt in range(MAX_RETRIES + 1):
        prompt = user
        if attempt:
            prompt += (
                f"\n\nYour previous reply was invalid: {last_error}\n"
                "Return valid JSON only, matching the schema exactly."
            )
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            graph = ConceptGraph.model_validate_json(_strip_fences(raw))
            break
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]

    if graph is None:
        raise ConceptExtractionError(
            "Couldn't build the concept map for this chapter. Please retry, or re-upload a clearer file."
        )

    notes = []
    if truncated:
        notes.append("Chapter was very long; only the first part was analysed.")
    if len(text.strip()) < 200 or text.startswith("[fake-ocr]"):
        notes.append("Very little text was extracted; concepts may be unreliable.")
    note = " ".join(notes) or None
    return graph.model_dump(), bool(notes), note