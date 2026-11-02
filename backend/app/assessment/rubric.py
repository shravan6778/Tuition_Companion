"""The rubric of a short or long answer: key points, each worth some marks.

  * the model WRITES the rubric together with the question (from the textbook page), the server stores it and never sends it
    to a student before they submit;
  * the grader says which points the answer hit and which it missed; the SCORE is then worked out here, in code, from the
    marks of the hit points. The model never gets to hand out a number that disagrees with its own point list.
  * a teacher override either picks the hit points again (score follows) or sets a score directly.
"""
from typing import Optional, Sequence

from pydantic import BaseModel, Field, field_validator

SHORT_POINTS = (1, 4)  # a short answer has 1 to 4 key points
LONG_POINTS = (3, 8)  # a long answer has 3 to 8
SHORT_MAX_MARKS = 6
LONG_MAX_MARKS = 15


class KeyPoint(BaseModel):
    point: str = Field(min_length=3, max_length=300)
    marks: int = Field(ge=1, le=3)

    @field_validator("point")
    @classmethod
    def _clean(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 3:
            raise ValueError("a key point cannot be blank")
        return cleaned


def check_rubric(points: Sequence[KeyPoint], fmt: str) -> list[KeyPoint]:
    """Raises ValueError (so pydantic reports it and the model is asked again) when the rubric is the wrong size."""
    lo, hi = LONG_POINTS if fmt == "long_answer" else SHORT_POINTS
    cap = LONG_MAX_MARKS if fmt == "long_answer" else SHORT_MAX_MARKS
    if not lo <= len(points) <= hi:
        raise ValueError(f"key_points must have {lo} to {hi} points")
    if len({p.point.casefold() for p in points}) != len(points):
        raise ValueError("key points must be different from each other")
    if sum(p.marks for p in points) > cap:
        raise ValueError(f"the marks add up to more than {cap}")
    return list(points)


def to_json(points: Sequence[KeyPoint]) -> list[dict]:
    return [{"point": p.point, "marks": p.marks} for p in points]


def parse(stored: Optional[list]) -> list[dict]:
    """The stored rubric, defensively: [{"point": str, "marks": int}], or [] for an older question that has none."""
    out = []
    for item in stored or []:
        if isinstance(item, dict) and isinstance(item.get("point"), str):
            marks = item.get("marks")
            out.append({"point": item["point"], "marks": marks if isinstance(marks, int) and not isinstance(marks, bool) and marks > 0 else 1})
    return out


def total_marks(points: Sequence[dict]) -> int:
    return sum(p["marks"] for p in points)


def clean_indexes(indexes: Sequence, n_points: int) -> list[int]:
    """Distinct, in-range integer indexes, sorted. Anything else is dropped."""
    return sorted({i for i in indexes if isinstance(i, int) and not isinstance(i, bool) and 0 <= i < n_points})


def marks_for(points: Sequence[dict], hit: Sequence[int]) -> int:
    return sum(points[i]["marks"] for i in clean_indexes(hit, len(points)))


def score_from_hits(points: Sequence[dict], hit: Sequence[int]) -> float:
    total = total_marks(points)
    return round(marks_for(points, hit) / total, 4) if total else 0.0


def missed_from_hits(points: Sequence[dict], hit: Sequence[int]) -> list[int]:
    got = set(clean_indexes(hit, len(points)))
    return [i for i in range(len(points)) if i not in got]
