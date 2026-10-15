"""Quiz generation, assignment linking, and tenancy rules (Phase 4 Step 2)."""
import logging
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.assessment import quiz_agent
from app.assignments import service as assignment_service
from app.assignments.scope import chapter_concepts
from app.content_library import access
from app.core.config import settings
from app.core.errors import ProcessingError
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import (
    Assignment, AssignmentConcept, AssignmentLevel, Book, Chapter, Concept, Quiz, QuizKind, QuizQuestion, Room,
    RoomMember, User, student_book,
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
        if assignment.book_id != book.id:
            raise HTTPException(422, "The assignment belongs to a different book")
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
            book_id=book.id,
            chapter_id=chapter.id if chapter else None,
            level=level,
            title=title[:200],
            due_date=due_date,
        )
        assignment.concepts = [AssignmentConcept(concept_id=c.id, position=i) for i, c in enumerate(concepts)]
        db.add(assignment)
        db.flush()
        return assignment

    return None


def generate_teacher_quiz(db: Session, teacher: User, spec: TeacherQuizSpec) -> Quiz:
    """Validates tenancy + scope, creates the Quiz (and optional Assignment), plans mixed-difficulty questions,
    and invokes the Quiz Agent to generate each question."""
    book = access.get_book_visible_to_teacher(db, teacher, spec.book_id)
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
    plan = quiz_agent.plan_quiz_questions(list(contexts), count, related_map)
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
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    visible_assignments = assignment_service.student_assignments_query(student).with_only_columns(Assignment.id)
    return select(Quiz).where(
        Quiz.book_id.in_(linked),
        or_(
            (Quiz.kind == QuizKind.PRACTICE) & (Quiz.student_id == student.id),
            (Quiz.kind == QuizKind.TEACHER) & (Quiz.assignment_id.in_(visible_assignments)),
        ),
    )


def get_student_quiz(db: Session, student: User, quiz_id: uuid.UUID) -> Quiz:
    quiz = db.scalar(student_visible_quizzes_query(student).where(Quiz.id == quiz_id))
    if quiz is None:
        raise _404("Quiz")
    return quiz


def list_student_quizzes(db: Session, student: User, assignment_id: Optional[uuid.UUID] = None) -> list[Quiz]:
    query = student_visible_quizzes_query(student)
    if assignment_id is not None:
        query = query.where(Quiz.assignment_id == assignment_id)
    return list(db.scalars(query.order_by(Quiz.created_at.desc()).limit(50)))