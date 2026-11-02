"""Written and spoken answers: validating what a student sends, grading it, and what a teacher may change afterwards.

Typing is the baseline. A spoken answer is just text that arrived through the microphone: it lands in the SAME answer box,
the student reviews or edits it, and what is sent is that text. So grading, rubrics and the teacher view are the same for both.
This module is shared by tests (`quiz_service`) and assignment checks (`service`).

Rules enforced here (never only in the UI):
  * never grade straight from speech: a voice answer must come with `transcript_confirmed=true`, the student's tick that they
    read it and it says what they meant;
  * voice is only for the languages in SPEECH_LANGUAGES and never for a maths-type subject (`subject_policy`);
  * AUDIO IS NEVER HANDLED HERE. Only text, the language and `input_method` reach this module and the database;
  * a spoken answer in a SPEECH_HOLD_LANGUAGES language ("confirm before grading") is saved but NOT graded: the teacher
    confirms the transcript first (`confirm_and_grade`), or marks it directly (`override`);
  * the model's score is a SUGGESTION (`score_source='ai'`); a teacher's change is `score_source='teacher'`, and the model's
    original number is kept in `ai_score`.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import HTTPException

from app.assessment import llm_grader, rubric
from app.assessment.subject_policy import csv_list, speech_languages
from app.core.config import settings
from app.models import AnswerFormat, InputMethod, ScoreSource

logger = logging.getLogger(__name__)

WRITTEN = AnswerFormat.WRITTEN  # short_answer, long_answer


@dataclass
class AnswerInput:
    """What a student sent for one question."""
    chosen_index: Optional[int] = None
    answer_text: Optional[str] = None
    input_method: str = InputMethod.TYPED
    language: Optional[str] = None
    transcript_confirmed: bool = False


@dataclass
class Outcome:
    score: Optional[float]
    correct: Optional[bool]
    feedback: Optional[str]
    points_hit: Optional[list[int]] = None
    points_missed: Optional[list[int]] = None
    score_source: Optional[str] = None  # ai | None
    needs_confirm: bool = False


def max_chars(fmt: str) -> int:
    return settings.long_answer_max_chars if fmt == AnswerFormat.LONG_ANSWER else settings.short_answer_max_chars


def clean_text(text: Optional[str], fmt: str) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) > max_chars(fmt):
        raise HTTPException(422, f"Please keep your answer under {max_chars(fmt)} characters")
    return cleaned


def validate(fmt: str, raw: AnswerInput, *, voice_allowed: bool) -> AnswerInput:
    """Returns the cleaned input or raises 422. Multiple choice takes no text and no voice."""
    method = raw.input_method or InputMethod.TYPED
    if method not in InputMethod.ALL:
        raise HTTPException(422, "input_method must be 'typed' or 'voice'")
    if fmt not in WRITTEN:
        if method == InputMethod.VOICE:
            raise HTTPException(422, "A multiple-choice answer can't be spoken")
        return AnswerInput(chosen_index=raw.chosen_index)
    text = clean_text(raw.answer_text, fmt)
    if method == InputMethod.TYPED:
        return AnswerInput(answer_text=text)
    if not voice_allowed:
        raise HTTPException(422, "Spoken answers are turned off for this subject. Please type your answer.")
    if raw.language not in speech_languages():
        raise HTTPException(422, "Choose English, Hindi or Telugu for a spoken answer")
    if text and not raw.transcript_confirmed:
        raise HTTPException(422, "Please read your spoken answer and tick that it says what you meant before you submit.")
    return AnswerInput(answer_text=text, input_method=InputMethod.VOICE, language=raw.language, transcript_confirmed=True)


def is_held(inp: AnswerInput) -> bool:
    """A spoken answer in a 'confirm before grading' language waits for the teacher's confirmation of the transcript."""
    return bool(inp.input_method == InputMethod.VOICE and inp.answer_text and inp.language in csv_list(settings.speech_hold_languages))


def grade(llm, *, question: str, key_points: Optional[list], expected_answer: Optional[str], text: str, concept_name: str,
          input_method: str, fmt: str) -> Outcome:
    """The model's SUGGESTION. A question with a rubric is marked key point by key point; an older short answer without one is
    graded as a single score against its expected answer. Blank answers score 0 without a model call.
    Raises HTTPException 503 when the model can't be used."""
    try:
        if rubric.parse(key_points):
            g = llm_grader.grade_written_answer(llm, question, key_points, text, concept_name, input_method, max_chars(fmt))
            return Outcome(g.score, g.correct, g.feedback, g.points_hit, g.points_missed, ScoreSource.AI)
        s = llm_grader.grade_short_answer(llm, question=question, expected_answer=expected_answer or "", student_answer=text,
                                          concept_name=concept_name)
        return Outcome(s.score, s.correct, s.feedback, None, None, ScoreSource.AI)
    except (llm_grader.WrittenGradeError, llm_grader.ShortAnswerGradeError) as exc:
        raise HTTPException(503, str(exc)) from exc


def grade_input(llm, inp: AnswerInput, *, question: str, key_points, expected_answer, concept_name: str, fmt: str) -> Outcome:
    if is_held(inp):
        return Outcome(None, None, "Your teacher will check what you said before this is marked.", needs_confirm=True)
    return grade(llm, question=question, key_points=key_points, expected_answer=expected_answer, text=inp.answer_text or "",
                 concept_name=concept_name, input_method=inp.input_method, fmt=fmt)


def apply(row, inp: AnswerInput, out: Outcome) -> None:
    """Writes the answer and its grade onto a QuizResponse or a CheckQuestion (they share these columns)."""
    row.answer_text = inp.answer_text or None
    row.input_method = inp.input_method
    row.transcript_language = inp.language if inp.input_method == InputMethod.VOICE else None
    row.score, row.correct, row.feedback = out.score, out.correct, out.feedback
    row.points_hit, row.points_missed = out.points_hit, out.points_missed
    row.score_source = out.score_source
    row.ai_score = out.score if out.score_source == ScoreSource.AI else None
    row.needs_confirm = out.needs_confirm


# ---- the teacher's side -----------------------------------------------------------------------------------------------

def _pass(score: float) -> bool:
    return score >= settings.quiz_short_answer_pass_score


def _stamp(row, teacher_id) -> None:
    row.reviewed_by, row.reviewed_at = teacher_id, datetime.now(timezone.utc)


def override(row, fmt: str, key_points: Optional[list], teacher_id, *, points_hit: Optional[Sequence[int]] = None,
             score: Optional[float] = None, feedback: Optional[str] = None) -> None:
    """The teacher's mark replaces the AI suggestion (the suggestion is kept in `ai_score`). Give the key points the answer hit
    (the score follows from their marks) or, for an answer without a rubric, a score between 0 and 1."""
    if fmt not in WRITTEN:
        raise HTTPException(409, "Multiple-choice answers are marked in code and can't be overridden")
    points = rubric.parse(key_points)
    if points_hit is not None:
        if not points:
            raise HTTPException(422, "This question has no key points to pick from; give a score instead")
        if any(not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(points) for i in points_hit):
            raise HTTPException(422, "points_hit has a number that isn't one of this question's key points")
        hit = rubric.clean_indexes(points_hit, len(points))
        new_score = rubric.score_from_hits(points, hit)
        row.points_hit, row.points_missed = hit, rubric.missed_from_hits(points, hit)
    elif score is not None:
        if not 0.0 <= score <= 1.0:
            raise HTTPException(422, "score must be between 0 and 1")
        new_score = round(float(score), 4)
        row.points_hit = row.points_missed = None  # a score typed in by hand no longer matches any list of points
    else:
        raise HTTPException(422, "Give points_hit or a score")
    if row.ai_score is None and row.score is not None and row.score_source == ScoreSource.AI:
        row.ai_score = row.score
    row.score, row.correct, row.score_source, row.needs_confirm = new_score, _pass(new_score), ScoreSource.TEACHER, False
    if feedback is not None:
        row.teacher_feedback = feedback.strip() or None
    _stamp(row, teacher_id)


def confirm_and_grade(llm, row, fmt: str, question: str, key_points, expected_answer, concept_name: str, teacher_id,
                      transcript: Optional[str] = None) -> None:
    """For a held spoken answer: the teacher confirms (or corrects) the transcript, then the model gives its suggestion."""
    if fmt not in WRITTEN or row.input_method != InputMethod.VOICE:
        raise HTTPException(409, "Only a spoken written answer needs its transcript confirmed")
    if transcript is not None:
        row.answer_text = clean_text(transcript, fmt) or None
    out = grade(llm, question=question, key_points=key_points, expected_answer=expected_answer, text=row.answer_text or "",
                concept_name=concept_name, input_method=InputMethod.VOICE, fmt=fmt)
    row.score, row.correct, row.feedback = out.score, out.correct, out.feedback
    row.points_hit, row.points_missed, row.score_source, row.ai_score = out.points_hit, out.points_missed, out.score_source, out.score
    row.needs_confirm = False
    _stamp(row, teacher_id)


@dataclass
class ConceptTally:
    """asked / correct per concept over the graded questions of one student's check or quiz."""
    per_concept: dict = field(default_factory=dict)

    def add(self, concept_id, correct: Optional[bool]) -> None:
        if concept_id is None or correct is None:
            return
        asked, right = self.per_concept.get(concept_id, (0, 0))
        self.per_concept[concept_id] = (asked + 1, right + (1 if correct else 0))
