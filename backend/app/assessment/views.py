"""How a written or spoken answer is shown, for a student (after submitting) and for a teacher. Shared by checks and quizzes.

Before submission a student gets the question, its answer format and whether the mic is allowed: never the rubric, the model
answer or the expected points. After submission they see their own text, which key points they hit and missed, the score and
who gave it: an AI score is labelled a SUGGESTION until a teacher has looked."""
from typing import Optional

from pydantic import BaseModel

from app.assessment import rubric

AI_LABEL = "AI suggestion. Your teacher may change it."
TEACHER_LABEL = "Marked by your teacher."
HELD_LABEL = "Waiting for your teacher to check what you said."


class RubricPointOut(BaseModel):
    point: str
    marks: int
    hit: Optional[bool] = None  # None when this answer was not marked against the rubric


class WrittenResultOut(BaseModel):
    """The fields a written / spoken answer adds to a question. All of them except `answer_format` and `voice_allowed` are
    only filled after submission (or for the teacher)."""
    answer_format: str = "mcq"  # mcq | short_answer | long_answer
    voice_allowed: bool = False  # false for a maths-type subject: the mic is hidden and the server refuses voice
    answer_text: Optional[str] = None
    input_method: Optional[str] = None  # typed | voice
    transcript_language: Optional[str] = None  # en-IN | hi-IN | te-IN, voice only
    score: Optional[float] = None
    score_source: Optional[str] = None  # ai | teacher | null (multiple choice, or not graded yet)
    score_label: Optional[str] = None  # the words to show beside an AI or teacher score
    needs_confirm: bool = False
    feedback: Optional[str] = None
    teacher_feedback: Optional[str] = None
    expected_answer: Optional[str] = None
    rubric: Optional[list[RubricPointOut]] = None
    marks_awarded: Optional[int] = None
    marks_available: Optional[int] = None


def score_label(score_source: Optional[str], needs_confirm: bool) -> Optional[str]:
    if needs_confirm:
        return HELD_LABEL
    return {"ai": AI_LABEL, "teacher": TEACHER_LABEL}.get(score_source or "")


def fill_written(item: WrittenResultOut, row, key_points: Optional[list], expected_answer: Optional[str], *, reveal: bool) -> None:
    """Sets the written-answer fields on `item` from a QuizResponse / CheckQuestion row (`row` may be None for a quiz question
    this student has not answered). With reveal=False nothing but what the student already knew is set."""
    if not reveal:
        return
    if row is None:  # the teacher's view of the question itself: the key, no answer yet
        item.expected_answer = expected_answer
        points = rubric.parse(key_points)
        if points:
            item.rubric = [RubricPointOut(point=p["point"], marks=p["marks"]) for p in points]
            item.marks_available = rubric.total_marks(points)
        return
    item.answer_text, item.input_method, item.transcript_language = row.answer_text, row.input_method, row.transcript_language
    item.score, item.score_source, item.needs_confirm = row.score, row.score_source, bool(row.needs_confirm)
    item.score_label = score_label(row.score_source, bool(row.needs_confirm))
    item.feedback, item.teacher_feedback, item.expected_answer = row.feedback, row.teacher_feedback, expected_answer
    points = rubric.parse(key_points)
    if points:
        hit = set(row.points_hit or [])
        marked = row.points_hit is not None or row.points_missed is not None
        item.rubric = [RubricPointOut(point=p["point"], marks=p["marks"], hit=(i in hit) if marked else None) for i, p in enumerate(points)]
        item.marks_available = rubric.total_marks(points)
        if marked:
            item.marks_awarded = rubric.marks_for(points, row.points_hit or [])
