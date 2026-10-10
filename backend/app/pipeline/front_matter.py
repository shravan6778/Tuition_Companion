"""Layer 1: read the cover + publisher/edition pages and propose the Book's metadata.
The teacher always confirms or edits the result before a Book exists (Rules.md: never auto-create)."""
import json
import re
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.core.errors import ProcessingError

MAX_RETRIES = 2

SYSTEM = (
    "You read the cover and the publisher/edition pages of a school textbook and report what they state. "
    "Reply with JSON only, shaped exactly as: "
    '{"board":str|null,"class_name":str|null,"subject":str|null,"publisher":str|null,"edition":str|null,'
    '"is_customized":bool,"school":str|null}. '
    "Use null for anything the pages do not state; never guess. 'board' is the exam board or authority "
    "(e.g. CBSE, ICSE, a state board). 'class_name' looks like 'Class 9'. 'edition' is the edition/year line. "
    "'is_customized' is true only if the pages say the book was made for a specific school, and 'school' is then its name. "
    "Write class_name as 'Class N' even if the pages say 'Grade 9', 'Std. IX' or 'Standard 9'. 'publisher' is the body that "
    "publishes the book (for example NCERT for the National Council of Educational Research and Training). "
    "Return null only for what the text really does not state."
)


class FrontMatterError(ProcessingError):
    pass


class BookMetadata(BaseModel):
    board: Optional[str] = Field(default=None, max_length=80)
    class_name: Optional[str] = Field(default=None, max_length=40)
    subject: Optional[str] = Field(default=None, max_length=80)
    publisher: Optional[str] = Field(default=None, max_length=120)
    edition: Optional[str] = Field(default=None, max_length=120)
    is_customized: bool = False
    school: Optional[str] = Field(default=None, max_length=120)

    @field_validator("board", "class_name", "subject", "publisher", "edition", "school", mode="before")
    @classmethod
    def _blank_to_none(cls, v):
        if isinstance(v, str):
            v = " ".join(v.split())
            return v or None
        return v


FIELDS = ("board", "class_name", "subject", "publisher", "edition", "school")
_ALIASES = {"class": "class_name", "classname": "class_name", "class_name": "class_name", "grade": "class_name", "standard": "class_name",
            "std": "class_name", "exam_board": "board", "publisher_name": "publisher", "publishers": "publisher"}


def is_empty(m: "BookMetadata") -> bool:
    """True when nothing at all was read (the teacher then fills the form by hand)."""
    return not any(getattr(m, f) for f in FIELDS)


def _clean_keys(obj) -> dict:
    """Models sometimes answer {"Board": ...}, {"class": ...} or wrap everything in {"metadata": {...}}; accept those."""
    if not isinstance(obj, dict):
        return {}
    keys = {re.sub(r"[^a-z0-9]+", "_", str(k).lower()).strip("_"): v for k, v in obj.items()}
    keys = {_ALIASES.get(k, k): v for k, v in keys.items()}
    if not any(f in keys for f in FIELDS):
        for v in keys.values():
            if isinstance(v, dict):
                inner = _clean_keys(v)
                if any(f in inner for f in FIELDS):
                    return inner
    return {k: v for k, v in keys.items() if k in FIELDS or k == "is_customized"}


def parse_reply(raw: str) -> "BookMetadata":
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise ValidationError.from_exception_data("BookMetadata", [{"type": "value_error", "loc": (), "input": raw, "ctx": {"error": exc}}]) from exc
    return BookMetadata.model_validate(_clean_keys(data))


def extract_book_metadata(provider, text: str) -> BookMetadata:
    user = f"FRONT PAGES TEXT:\n{text[:6000]}"
    last_error = ""
    result: Optional[BookMetadata] = None
    for attempt in range(MAX_RETRIES + 1):
        prompt = user if not attempt else (
            f"{user}\n\nYour previous reply was unusable: {last_error}\nRead the text again and return valid JSON only, matching the schema exactly."
        )
        raw = provider.complete_json(SYSTEM, prompt)
        try:
            result = parse_reply(raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
            continue
        if not is_empty(result):
            return result
        last_error = "every field was null, but the text may state some of them (class, subject, publisher...)"
    if result is not None:  # parsed fine but nothing was found, even after a second look: let the teacher fill it in
        return result
    raise FrontMatterError("Couldn't read the book's details from these pages. You can enter them by hand instead.")
