"""Layer 1: read the cover + publisher/edition pages and propose the Book's metadata.
The teacher always confirms or edits the result before a Book exists (Rules.md: never auto-create)."""
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
    "'is_customized' is true only if the pages say the book was made for a specific school, and 'school' is then its name."
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


def extract_book_metadata(provider, text: str) -> BookMetadata:
    user = f"FRONT PAGES TEXT:\n{text[:6000]}"
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        prompt = user if not attempt else (
            f"{user}\n\nYour previous reply was invalid: {last_error}\nReturn valid JSON only, matching the schema exactly."
        )
        raw = provider.complete_json(SYSTEM, prompt).strip()
        if raw.startswith("```"):
            raw = raw.strip("`").removeprefix("json").strip()
        try:
            return BookMetadata.model_validate_json(raw)
        except ValidationError as exc:
            last_error = "; ".join(e["msg"] for e in exc.errors())[:300]
    raise FrontMatterError("Couldn't read the book's details from these pages. You can enter them by hand instead.")
