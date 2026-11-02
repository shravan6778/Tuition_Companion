"""Shared pieces of a written or spoken answer, used by `QuizResponse` (tests) and `CheckQuestion` (assignment checks).

  * `input_method`  : how the text got into the answer box: `typed`, or `voice` (the transcript, after the student reviewed it).
                      Typing is the baseline; voice only fills the same box, so grading, rubrics and the teacher view do not change.
  * `transcript_language` : the language the student picked for the mic (en-IN / hi-IN / te-IN); NULL for typed answers.
  * AUDIO IS NEVER STORED. Browser mode never sends it to the server; server mode holds it in memory only until it has been
    transcribed (speech/service.py). Only the text, the language and `input_method` are kept.
  * `score_source`  : who produced `score`. `ai` = the model's SUGGESTION from the rubric; `teacher` = the teacher's override.
                      NULL = graded in code (multiple choice) or not graded yet.
  * `ai_score`      : the model's own score, kept when a teacher overrides so the two can be compared later.
  * `points_hit` / `points_missed` : indexes into the question's `key_points` (the rubric), set by the grader.
  * `needs_confirm` : a spoken answer in a "confirm before grading" language (SPEECH_HOLD_LANGUAGES): not graded until the teacher
                      has confirmed the transcript.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, String, Text, Uuid, false
from sqlalchemy.orm import Mapped, mapped_column


class InputMethod:
    TYPED = "typed"
    VOICE = "voice"
    ALL = (TYPED, VOICE)


class ScoreSource:
    AI = "ai"
    TEACHER = "teacher"
    ALL = (AI, TEACHER)


class WrittenAnswerMixin:
    input_method: Mapped[str] = mapped_column(String(8), default=InputMethod.TYPED, server_default=InputMethod.TYPED, nullable=False)
    transcript_language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    points_hit: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    points_missed: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    score_source: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    ai_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    needs_confirm: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
    teacher_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
