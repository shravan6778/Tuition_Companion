"""Quiz generation, assignment linking, hybrid grading, and unified mastery updates (Phase 4 Steps 2–5)."""
import logging
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.assessment import checks, llm_grader, mastery, quiz_agent
from app.assignments import service as assignment_service
from app.assignments.scope import chapter_concepts
from app.content_library import access
from app.core.config import settings
from app.core.errors import ProcessingError
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import (
    AnswerFormat, Assignment, AssignmentConcept, AssignmentLevel, Book, Chapter, ChapterStatus, Concept, Page, Quiz,
    QuizKind, QuizQuestion, QuizResponse, User, student_book,
)

logger = logging.getLogger(__name__)

OPEN, SUBMITTED = "open", "submitted"

LENGTH_MAP = {
    "short": settings.quiz_short_questions,
    "medium": settings.quiz_medium_questions,
    "long": settings.quiz_long_questions,
}
ALLOWED_TEACHER_COUNTS = {
    settings.quiz_short_questions,
    settings.quiz_medium_questions,
    settings.quiz_long_questions,
}


def _404(what: str = "Quiz") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{what} not found")


def resolve_teacher_question_count(length: Optional[str], question_count: Optional[int]) -> int:
    if length is not None:
        key = length.strip().lower()
        if key not in LENGTH_MAP:
            raise HTTPException(422, "Length must be 'short' (10), 'medium' (20), or 'long' (30)")
        count = LENGTH_MAP[key]
        if question_count is not None and question_count != count:
            raise HTTPException(422, f"Length '{key}' corresponds to {count} questions, not {question_count}")
        return count
    if question_count is not None:
        if question_count not in ALLOWED_TEACHER_COUNTS:
            raise HTTPException(422, f"Teacher test question_count must be one of {sorted(ALLOWED_TEACHER_COUNTS)}")
        return question_count
    return settings.quiz_short_questions


def _llm():
    try:
        return get_llm_provider()
    except Exception:
        logger.warning("Quiz LLM provider could not start", exc_info=True)
        return None


def _store():
    try:
        return get_graph_store()
    except Exception:
        logger.warning("Quiz graph store could not start", exc_info=True)
        return None


def _fill_quiz_questions(
    db: Session,
    quiz: Quiz,
    contexts: dict[uuid.UUID, quiz_agent.ConceptContext],
) -> None:
    """Generates each planned question from its grounded textbook page(s), committing as each question is ready."""
    llm = _llm()
    asked: dict[uuid.UUID, list[str]] = {}
    for q in quiz.questions:
        if q.status == "ready":
            if q.concept_id and q.question:
                asked.setdefault(q.concept_id, []).append(q.question)
            continue
        primary = contexts.get(q.concept_id) if q.concept_id else None
        related = contexts.get(q.related_concept_id) if q.related_concept_id else None
        if llm is None or primary is None or not primary.page_text.strip():
            q.status = "failed"
            db.commit()
            continue
        item = quiz_agent.PlannedQuizItem(
            position=q.position,
            concept_id=q.concept_id,
            related_concept_id=q.related_concept_id,
            question_type=q.question_type,
            answer_format=q.answer_format,
        )
        try:
            made = quiz_agent.generate_quiz_question(
                llm, item, primary, related, already_asked=asked.get(q.concept_id, ()), seed=str(q.id)
            )
            q.question = made.question
            q.options = made.options
            q.correct_index = made.correct_index
            q.expected_answer = made.expected_answer
            q.explanation = made.explanation
            q.status = "ready"
            asked.setdefault(q.concept_id, []).append(made.question)
        except (ProcessingError, RuntimeError):
            logger.warning("Quiz question could not be generated", exc_info=True)
            q.status = "failed"
        db.commit()


@dataclass
class TeacherQuizSpec:
    book_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    concept_ids: Optional[list[uuid.UUID]] = None
    length: Optional[str] = None  # short | medium | long
    question_count: Optional[int] = None
    title: Optional[str] = None
    assignment_id: Optional[uuid.UUID] = None
    room_id: Optional[uuid.UUID] = None
    student_id: Optional[uuid.UUID] = None
    due_date: Optional[date] = None


def _resolve_teacher_concepts(
    db: Session,
    book: Book,
    chapter_id: Optional[uuid.UUID],
    concept_ids: Optional[list[uuid.UUID]],
) -> tuple[Optional[Chapter], list[Concept]]:
    chapter: Optional[Chapter] = None
    if chapter_id is not None:
        chapter = assignment_service.ready_chapter(db, book, chapter_id)
    if concept_ids:
        concepts = assignment_service._valid_concepts(db, book, concept_ids, chapter)
        return chapter, concepts
    if chapter is not None:
        concepts = chapter_concepts(db, chapter.id)
        if not concepts:
            raise HTTPException(status.HTTP_409_CONFLICT, "This chapter has no concepts to generate a quiz from yet")
        return chapter, concepts
    raise HTTPException(422, "Provide a chapter_id, concept_ids, or both")


def _link_or_create_assignment(
    db: Session,
    teacher: User,
    book: Book,
    chapter: Optional[Chapter],
    concepts: list[Concept],
    title: str,
    assignment_id: Optional[uuid.UUID],
    room_id: Optional[uuid.UUID],
    student_id: Optional[uuid.UUID],
    due_date: Optional[date],
) -> Optional[Assignment]:
    if assignment_id is not None and (room_id is not None or student_id is not None):
        raise HTTPException(422, "Provide either an existing assignment_id or a target room_id/student_id, not both")

    if assignment_id is not None:
        assignment = assignment_service.get_teacher_assignment(db, teacher, assignment_id)
        if assignment.subject.casefold() != (book.subject or "").casefold():
            raise HTTPException(422, "The assignment belongs to a different subject")
        return assignment

    if room_id is not None or student_id is not None:
        target_room, target_student = assignment_service._target(db, teacher, room_id, student_id)
        level = AssignmentLevel.CHAPTER if (chapter is not None and not concepts) else (
            AssignmentLevel.CHAPTER if chapter is not None and len(concepts) == len(chapter_concepts(db, chapter.id))
            else AssignmentLevel.CONCEPT
        )
        assignment = Assignment(
            teacher_id=teacher.id,
            room_id=target_room,
            student_id=target_student,
            subject=book.subject,
            chapter_title=chapter.title if chapter else None,
            level=level,
            title=title[:200],
            due_date=due_date,
        )
        assignment.concepts = [AssignmentConcept(concept_id=c.id, concept_name=c.name, concept_key=assignment_service.loose_key(c.name), position=i) for i, c in enumerate(concepts)]
        db.add(assignment)
        db.flush()
        return assignment

    return None


def generate_teacher_quiz(db: Session, teacher: User, spec: TeacherQuizSpec) -> Quiz:
    """Validates tenancy + scope, creates the Quiz (and optional Assignment), plans mixed-difficulty questions,
    and invokes the Quiz Agent to generate each question."""
    book = access.get_book_visible_to_teacher(db, teacher, spec.book_id)
    # Teacher-generated quiz text may only be grounded in the platform reference corpus.
    # Private student books are never turned into teacher-visible question text.
    count = resolve_teacher_question_count(spec.length, spec.question_count)
    chapter, concepts = _resolve_teacher_concepts(db, book, spec.chapter_id, spec.concept_ids)

    default_title = (
        f"{chapter.title} Quiz" if chapter is not None
        else f"{concepts[0].name} Quiz" if len(concepts) == 1
        else f"{book.subject or 'Subject'} Quiz ({len(concepts)} concepts)"
    )
    title = (spec.title or default_title).strip()[:200]

    assignment = _link_or_create_assignment(
        db, teacher, book, chapter, concepts, title,
        spec.assignment_id, spec.room_id, spec.student_id, spec.due_date,
    )

    cids = [c.id for c in concepts]
    contexts, related_map = quiz_agent.load_concept_contexts(db, cids, book_ids=[book.id], store=_store())
    primary_cids = [cid for cid in cids if cid in contexts]
    plan = quiz_agent.plan_quiz_questions(primary_cids, count, related_map)
    if not plan:
        raise HTTPException(status.HTTP_409_CONFLICT, "No ready concepts found to generate a quiz")

    quiz = Quiz(
        kind=QuizKind.TEACHER,
        teacher_id=teacher.id,
        book_id=book.id,
        chapter_id=chapter.id if chapter else None,
        assignment_id=assignment.id if assignment else None,
        title=title,
        question_count=count,
        status=OPEN,
    )
    quiz.questions = [
        QuizQuestion(
            position=item.position,
            concept_id=item.concept_id,
            related_concept_id=item.related_concept_id,
            question_type=item.question_type,
            answer_format=item.answer_format,
            status="pending",
        )
        for item in plan
    ]
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    _fill_quiz_questions(db, quiz, contexts)
    db.refresh(quiz)
    return quiz


def assign_teacher_quiz(
    db: Session,
    teacher: User,
    quiz_id: uuid.UUID,
    room_id: Optional[uuid.UUID] = None,
    student_id: Optional[uuid.UUID] = None,
    assignment_id: Optional[uuid.UUID] = None,
    due_date: Optional[date] = None,
) -> Quiz:
    """Links an existing teacher quiz to a room/student (creating an Assignment) or to an existing Assignment."""
    quiz = get_teacher_quiz(db, teacher, quiz_id)
    book = access.get_book_visible_to_teacher(db, teacher, quiz.book_id)
    chapter = db.get(Chapter, quiz.chapter_id) if quiz.chapter_id else None
    concept_ids = list(dict.fromkeys(q.concept_id for q in quiz.questions if q.concept_id))
    concepts = list(db.scalars(select(Concept).where(Concept.id.in_(concept_ids)))) if concept_ids else []
    order = {c.id: c for c in concepts}
    ordered_concepts = [order[cid] for cid in concept_ids if cid in order]

    if assignment_id is None and room_id is None and student_id is None:
        raise HTTPException(422, "Provide room_id, student_id, or assignment_id")

    assignment = _link_or_create_assignment(
        db, teacher, book, chapter, ordered_concepts, quiz.title,
        assignment_id, room_id, student_id, due_date,
    )
    quiz.assignment_id = assignment.id if assignment else None
    db.commit()
    db.refresh(quiz)
    return quiz


def get_teacher_quiz(db: Session, teacher: User, quiz_id: uuid.UUID) -> Quiz:
    quiz = db.scalar(select(Quiz).where(Quiz.id == quiz_id, Quiz.teacher_id == teacher.id, Quiz.kind == QuizKind.TEACHER))
    if quiz is None:
        raise _404("Quiz")
    return quiz


def list_teacher_quizzes(
    db: Session,
    teacher: User,
    book_id: Optional[uuid.UUID] = None,
    chapter_id: Optional[uuid.UUID] = None,
    assignment_id: Optional[uuid.UUID] = None,
) -> list[Quiz]:
    query = select(Quiz).where(Quiz.teacher_id == teacher.id, Quiz.kind == QuizKind.TEACHER)
    if book_id is not None:
        query = query.where(Quiz.book_id == book_id)
    if chapter_id is not None:
        query = query.where(Quiz.chapter_id == chapter_id)
    if assignment_id is not None:
        query = query.where(Quiz.assignment_id == assignment_id)
    return list(db.scalars(query.order_by(Quiz.created_at.desc()).limit(50)))


def student_visible_quizzes_query(student: User):
    """A student can see:
      1. Their own self-triggered practice quizzes (`kind='practice'` and `student_id == student.id`) on linked books, OR
      2. Teacher-generated quizzes (`kind='teacher'`) linked to an assignment visible to this student (same room or
         assigned directly to this student, on a book the student has currently linked)."""
    visible_assignments = assignment_service.student_assignments_query(student).with_only_columns(Assignment.id)
    return select(Quiz).where(
        or_(
            (Quiz.kind == QuizKind.PRACTICE) & (Quiz.student_id == student.id),
            (Quiz.kind == QuizKind.TEACHER) & (Quiz.assignment_id.in_(visible_assignments)),
        ),
    )


def get_student_quiz(db: Session, student: User, quiz_id: uuid.UUID) -> Quiz:
    quiz = db.scalar(student_visible_quizzes_query(student).where(Quiz.id == quiz_id))
    if quiz is None:
        raise _404("Quiz")
    if quiz.kind == QuizKind.TEACHER and quiz.assignment_id is not None:
        assignment = assignment_service.get_student_assignment(db, student, quiz.assignment_id)
        book, chapter = assignment_service.resolve_student_target(db, student, assignment)
        if assignment.chapter_title and chapter is None:
            raise HTTPException(409, "Upload this chapter to see this task.")
        if book is not None:
            # The quiz response layer resolves the target to this student's own copy.
            quiz._resolved_student_book_id = book.id
    return quiz


def list_student_quizzes(db: Session, student: User, assignment_id: Optional[uuid.UUID] = None) -> list[Quiz]:
    query = student_visible_quizzes_query(student)
    if assignment_id is not None:
        query = query.where(Quiz.assignment_id == assignment_id)
    return list(db.scalars(query.order_by(Quiz.created_at.desc()).limit(50)))


@dataclass
class StudentPracticeSpec:
    book_id: Optional[uuid.UUID] = None
    chapter_id: Optional[uuid.UUID] = None
    question_count: Optional[int] = None
    title: Optional[str] = None


def _resolve_student_practice_pool(
    db: Session,
    student: User,
    book_id: Optional[uuid.UUID],
    chapter_id: Optional[uuid.UUID],
) -> tuple[Book, Optional[Chapter], list[Concept], list[uuid.UUID]]:
    """Returns `(primary_book, optional_chapter, candidate_concepts, allowed_book_ids)` for a student's practice quiz.
    Strictly enforces that any requested `book_id` or `chapter_id` belongs to a book the student has LINKED (404 otherwise)."""
    linked_ids = list(db.scalars(select(Book.id).where(Book.owner_student_id == student.id)))
    linked_ids += list(db.scalars(select(student_book.c.book_id).where(student_book.c.student_id == student.id)))
    linked_ids = list(dict.fromkeys(linked_ids))
    if book_id is not None and book_id not in set(linked_ids):
        raise _404("Book")

    chapter: Optional[Chapter] = None
    if chapter_id is not None:
        chapter = db.get(Chapter, chapter_id)
        if chapter is None or chapter.status != ChapterStatus.READY or chapter.book_id not in set(linked_ids):
            raise _404("Chapter")
        if book_id is not None and chapter.book_id != book_id:
            raise _404("Chapter")
        book = db.get(Book, chapter.book_id)
        concepts = chapter_concepts(db, chapter.id)
        if not concepts:
            raise HTTPException(status.HTTP_409_CONFLICT, "This chapter has no concepts ready for practice yet")
        return book, chapter, concepts, [book.id]

    if book_id is not None:
        book = access.get_linked_book(db, student, book_id)
        concepts = list(
            db.scalars(
                select(Concept)
                .join(Page, Page.id == Concept.page_id)
                .join(Chapter, Chapter.id == Page.chapter_id)
                .where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY, Concept.is_canonical.is_(True))
                .order_by(Chapter.sequence_num, Page.page_number, Concept.position)
            )
        )
        if not concepts:
            raise HTTPException(status.HTTP_409_CONFLICT, "This book has no ready concepts for practice yet")
        return book, None, concepts, [book.id]

    if not linked_ids:
        raise HTTPException(status.HTTP_409_CONFLICT, "Link a book first before starting a practice quiz")

    concepts = list(
        db.scalars(
            select(Concept)
            .join(Page, Page.id == Concept.page_id)
            .join(Chapter, Chapter.id == Page.chapter_id)
            .where(Chapter.book_id.in_(linked_ids), Chapter.status == ChapterStatus.READY, Concept.is_canonical.is_(True))
            .order_by(Chapter.book_id, Chapter.sequence_num, Page.page_number, Concept.position)
        )
    )
    if not concepts:
        raise HTTPException(status.HTTP_409_CONFLICT, "No ready chapters found in your linked books yet")

    first_page = db.get(Page, concepts[0].page_id)
    first_chapter = db.get(Chapter, first_page.chapter_id)
    book = db.get(Book, first_chapter.book_id)
    return book, None, concepts, linked_ids


def generate_student_practice_quiz(db: Session, student: User, spec: StudentPracticeSpec) -> Quiz:
    """Builds a student self-triggered practice quiz (default 10 questions) weighted 60% toward weak concepts,
    20% toward at-risk concepts, and 20% toward general revision."""
    count = spec.question_count or settings.quiz_practice_questions
    if count < 1 or count > 30:
        raise HTTPException(422, "Practice quiz question_count must be between 1 and 30")

    book, chapter, candidates, allowed_book_ids = _resolve_student_practice_pool(
        db, student, spec.book_id, spec.chapter_id
    )
    candidate_ids = [c.id for c in candidates]

    states = mastery.current_state(db, student.id, candidate_ids)
    weak_states = sorted(
        (s for s in states.values() if s.status == mastery.WEAK),
        key=lambda s: (s.score if s.score is not None else 0.0, s.name),
    )
    at_risk_states = sorted(
        (s for s in states.values() if s.status == mastery.AT_RISK),
        key=lambda s: s.name,
    )
    weak_ids = [s.concept_id for s in weak_states]
    at_risk_ids = [s.concept_id for s in at_risk_states]
    doubted_ids = mastery.doubted_concept_ids(db, student.id)

    focus_ids = weak_ids or at_risk_ids
    if spec.book_id is None and focus_ids:
        focus_concept = db.get(Concept, focus_ids[0])
        focus_page = db.get(Page, focus_concept.page_id) if focus_concept else None
        focus_ch = db.get(Chapter, focus_page.chapter_id) if focus_page else None
        if focus_ch is not None:
            book = db.get(Book, focus_ch.book_id)

    weighted_slots = quiz_agent.plan_practice_concepts(
        candidate_ids=candidate_ids,
        weak_ids=weak_ids,
        at_risk_ids=at_risk_ids,
        total_questions=count,
        doubted_ids=doubted_ids,
        seed=str(student.id),
    )
    contexts, related_map = quiz_agent.load_concept_contexts(
        db, weighted_slots, book_ids=allowed_book_ids, store=_store()
    )
    valid_slots = [cid for cid in weighted_slots if cid in contexts]
    plan = quiz_agent.plan_quiz_questions(
        valid_slots, count, related_map, preserve_slots=True
    )
    if not plan:
        raise HTTPException(status.HTTP_409_CONFLICT, "No ready concepts found to generate a practice quiz")

    default_title = (
        f"Practice: {chapter.title}" if chapter is not None
        else f"Practice: {book.subject or 'Revision'} (Weak Areas)" if (weak_ids or at_risk_ids)
        else f"Practice: {book.subject or 'Revision'}"
    )
    title = (spec.title or default_title).strip()[:200]

    quiz = Quiz(
        kind=QuizKind.PRACTICE,
        student_id=student.id,
        book_id=book.id,
        chapter_id=chapter.id if chapter else None,
        title=title,
        question_count=count,
        status=OPEN,
    )
    quiz.questions = [
        QuizQuestion(
            position=item.position,
            concept_id=item.concept_id,
            related_concept_id=item.related_concept_id,
            question_type=item.question_type,
            answer_format=item.answer_format,
            status="pending",
        )
        for item in plan
    ]
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    _fill_quiz_questions(db, quiz, contexts)
    db.refresh(quiz)
    return quiz


# ---- Phase 4 Step 4 & Step 5: Hybrid Grading & Unified Mastery Integration ------------------------------------

@dataclass
class QuizAnswerInput:
    question_id: uuid.UUID
    chosen_index: Optional[int] = None
    answer_text: Optional[str] = None


def can_submit_quiz(quiz: Quiz) -> bool:
    ready = sum(1 for q in quiz.questions if q.status == "ready")
    return not any(q.status == "pending" for q in quiz.questions) and ready >= min(
        settings.check_min_questions, len(quiz.questions)
    )


def has_student_submitted(db: Session, quiz: Quiz, student_id: uuid.UUID) -> bool:
    if quiz.kind == QuizKind.PRACTICE and quiz.status == SUBMITTED:
        return True
    existing = db.scalar(
        select(func.count())
        .select_from(QuizResponse)
        .where(QuizResponse.quiz_id == quiz.id, QuizResponse.student_id == student_id)
    )
    return bool(existing and existing > 0)


def submit_quiz(db: Session, student: User, quiz: Quiz, answers: dict[uuid.UUID, QuizAnswerInput]) -> Quiz:
    """Grades a quiz using the hybrid engine (code for MCQ, LLM for short-answer) and writes atomic `quiz`
    and `propagated` events to `mastery_events` in ONE transaction."""
    if has_student_submitted(db, quiz, student.id):
        raise HTTPException(status.HTTP_409_CONFLICT, "This quiz was already submitted")
    if not can_submit_quiz(quiz):
        raise HTTPException(status.HTTP_409_CONFLICT, "Some questions aren't ready yet. Please try again in a moment.")

    by_id = {q.id: q for q in quiz.questions}
    unknown = [qid for qid in answers if qid not in by_id or by_id[qid].status != "ready"]
    if unknown:
        raise HTTPException(422, "An answer doesn't match a ready question of this quiz")

    cids = {q.concept_id for q in quiz.questions if q.concept_id}
    concept_names = {c.id: c.name for c in db.scalars(select(Concept).where(Concept.id.in_(cids)))} if cids else {}

    llm = _llm()
    ready_questions = [q for q in quiz.questions if q.status == "ready"]
    graded_rows: list[QuizResponse] = []
    per_concept: dict[uuid.UUID, tuple[int, int]] = {}

    for q in ready_questions:
        ans = answers.get(q.id)
        if q.answer_format == AnswerFormat.MCQ:
            chosen = (
                ans.chosen_index
                if ans is not None and isinstance(ans.chosen_index, int) and not isinstance(ans.chosen_index, bool)
                else None
            )
            g = checks.grade(
                checks.Question(str(q.concept_id), q.question or "", list(q.options or []), q.correct_index or 0, q.explanation),
                chosen,
            )
            q_score = 1.0 if g.correct else 0.0
            q_correct = g.correct
            q_feedback = q.explanation
            resp = QuizResponse(
                quiz_id=quiz.id,
                question_id=q.id,
                student_id=student.id,
                chosen_index=chosen,
                answer_text=None,
                score=q_score,
                correct=q_correct,
                feedback=q_feedback,
            )
        else:
            raw_text = ans.answer_text if ans is not None else None
            try:
                sa_grade = llm_grader.grade_short_answer(
                    llm,
                    question=q.question or "",
                    expected_answer=q.expected_answer or "",
                    student_answer=raw_text,
                    concept_name=concept_names.get(q.concept_id, ""),
                )
            except llm_grader.ShortAnswerGradeError as exc:
                db.rollback()
                raise HTTPException(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    str(exc),
                ) from exc
            q_score = sa_grade.score
            q_correct = sa_grade.correct
            q_feedback = sa_grade.feedback
            resp = QuizResponse(
                quiz_id=quiz.id,
                question_id=q.id,
                student_id=student.id,
                chosen_index=None,
                answer_text=" ".join((raw_text or "").split()) or None,
                score=q_score,
                correct=q_correct,
                feedback=q_feedback,
            )

        graded_rows.append(resp)
        if q.concept_id is not None:
            asked, right = per_concept.get(q.concept_id, (0, 0))
            per_concept[q.concept_id] = (asked + 1, right + (1 if q_correct else 0))

    overall_score = round(sum(r.score for r in graded_rows) / len(graded_rows), 4) if graded_rows else 0.0
    now = datetime.now(timezone.utc)

    try:
        db.add_all(graded_rows)
        quiz.score = overall_score
        quiz.status = SUBMITTED
        quiz.submitted_at = now
        mastery.record_quiz(db, student.id, quiz.id, quiz.assignment_id, per_concept)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(quiz)
    return quiz