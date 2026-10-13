"""Creating and listing assignments (Phase 3 step 1). All the rules live here so the routes stay thin.

Tenancy: a teacher can only assign from a book they can see, to a room they own or a student who sits in one of
their rooms. A student only ever sees assignments of their own teacher(s), on books they have LINKED. Anything
else looks like it doesn't exist (404)."""
import uuid
from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.assignments.scope import chapter_concepts, propose_exercise_concepts, subject_concepts
from app.content_library import access
from app.models import Assignment, AssignmentConcept, AssignmentLevel, Book, Chapter, ChapterStatus, Concept, Page, Room, RoomMember, User, student_book


def _404(what: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{what} not found")


def ready_chapter(db: Session, book: Book, chapter_id: uuid.UUID | None) -> Chapter:
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id)) if chapter_id else None
    if chapter is None:
        raise _404("Chapter")
    if chapter.status != ChapterStatus.READY:
        raise HTTPException(status.HTTP_409_CONFLICT, "That chapter isn't ready yet, so it can't be assigned")
    return chapter


def _target(db: Session, teacher: User, room_id: uuid.UUID | None, student_id: uuid.UUID | None):
    """Exactly one of room / student; both must belong to this teacher's world."""
    if (room_id is None) == (student_id is None):
        raise HTTPException(422, "Give either a room or a student, not both")
    if room_id is not None:
        if db.scalar(select(Room.id).where(Room.id == room_id, Room.teacher_id == teacher.id)) is None:
            raise _404("Room")
        return room_id, None
    in_my_room = db.scalar(
        select(RoomMember.id).join(Room, Room.id == RoomMember.room_id)
        .where(RoomMember.user_id == student_id, Room.teacher_id == teacher.id)
    )
    if in_my_room is None:
        raise _404("Student")
    return None, student_id


def _valid_concepts(db: Session, book: Book, concept_ids: list[uuid.UUID], chapter: Chapter | None = None) -> list[Concept]:
    """The picked concepts, in the order given, each one a canonical concept of a READY chapter of this book
    (and of `chapter` when one is given). A concept from anywhere else is a 404, never silently dropped."""
    unique = list(dict.fromkeys(concept_ids))
    query = (
        select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(Concept.id.in_(unique), Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY,
               Concept.is_canonical.is_(True))
    )
    if chapter is not None:
        query = query.where(Chapter.id == chapter.id)
    found = {c.id: c for c in db.scalars(query)}
    if len(found) != len(unique):
        raise _404("Concept")
    return [found[i] for i in unique]


@dataclass
class NewAssignment:
    level: str
    book_id: uuid.UUID
    room_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    concept_ids: list[uuid.UUID] | None = None
    page_numbers: list[int] | None = None
    title: str | None = None
    due_date: date | None = None


def create_assignment(db: Session, teacher: User, new: NewAssignment) -> Assignment:
    room_id, student_id = _target(db, teacher, new.room_id, new.student_id)
    book = access.get_book_visible_to_teacher(db, teacher, new.book_id)
    chapter, pages, title = None, None, new.title
    if new.level == AssignmentLevel.SUBJECT:
        concepts = subject_concepts(db, [book.id], book.subject or "")
        title = title or f"{book.subject}: whole book"
    elif new.level == AssignmentLevel.CHAPTER:
        chapter = ready_chapter(db, book, new.chapter_id)
        concepts = chapter_concepts(db, chapter.id)
        title = title or chapter.title
    elif new.level == AssignmentLevel.CONCEPT:
        if not new.concept_ids:
            raise HTTPException(422, "Pick at least one concept")
        concepts = _valid_concepts(db, book, new.concept_ids)
        title = title or (concepts[0].name if len(concepts) == 1 else f"{len(concepts)} concepts")
    elif new.level == AssignmentLevel.EXERCISE:
        # The teacher saw the PROPOSED list and sends back the one they confirmed: nothing is decided silently.
        chapter = ready_chapter(db, book, new.chapter_id)
        if not new.concept_ids:
            raise HTTPException(422, "Confirm at least one concept for this exercise")
        concepts = _valid_concepts(db, book, new.concept_ids, chapter)
        pages = sorted(set(new.page_numbers or []))
        if pages:
            existing = set(db.scalars(select(Page.page_number).where(Page.chapter_id == chapter.id, Page.page_number.in_(pages))))
            if existing != set(pages):
                raise _404("Page")
        title = title or f"{chapter.title}: exercise" + (f" (pages {pages[0]}-{pages[-1]})" if pages else "")
    else:
        raise HTTPException(422, "Unknown level")

    if not concepts:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nothing to assign yet: no concepts were found for that choice")
    assignment = Assignment(
        teacher_id=teacher.id, room_id=room_id, student_id=student_id, book_id=book.id,
        chapter_id=chapter.id if chapter else None, level=new.level, title=(title or "Assignment")[:200],
        exercise_pages=pages or None, due_date=new.due_date,
    )
    assignment.concepts = [AssignmentConcept(concept_id=c.id, position=i) for i, c in enumerate(concepts)]
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def exercise_proposal(db: Session, teacher: User, book_id: uuid.UUID, chapter_id: uuid.UUID, page_numbers: list[int] | None):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = ready_chapter(db, book, chapter_id)
    return chapter, propose_exercise_concepts(db, chapter, page_numbers or None)


def get_teacher_assignment(db: Session, teacher: User, assignment_id: uuid.UUID) -> Assignment:
    found = db.scalar(select(Assignment).where(Assignment.id == assignment_id, Assignment.teacher_id == teacher.id))
    if found is None:
        raise _404("Assignment")
    return found


def list_teacher_assignments(db: Session, teacher: User, room_id: uuid.UUID | None = None, student_id: uuid.UUID | None = None):
    query = select(Assignment).where(Assignment.teacher_id == teacher.id)
    if room_id is not None:
        query = query.where(Assignment.room_id == room_id)
    if student_id is not None:
        # that student's own assignments plus the ones given to a room of this teacher the student is in
        my_rooms = select(RoomMember.room_id).join(Room, Room.id == RoomMember.room_id).where(
            RoomMember.user_id == student_id, Room.teacher_id == teacher.id)
        query = query.where(or_(Assignment.student_id == student_id, Assignment.room_id.in_(my_rooms)))
    return list(db.scalars(query.order_by(Assignment.created_at.desc())))


def student_assignments_query(student: User):
    """Assignments this student may see: given to them or to a room they sit in, AND on a book they have linked."""
    my_rooms = select(RoomMember.room_id).where(RoomMember.user_id == student.id)
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    return select(Assignment).where(
        or_(Assignment.student_id == student.id, Assignment.room_id.in_(my_rooms)),
        Assignment.book_id.in_(linked),
    )


def list_student_assignments(db: Session, student: User) -> list[Assignment]:
    # Soonest due date first, then newest; assignments without a due date go after the dated ones.
    items = list(db.scalars(student_assignments_query(student).order_by(Assignment.created_at.desc())))
    return sorted(items, key=lambda a: (a.due_date is None, a.due_date or date.max))


def get_student_assignment(db: Session, student: User, assignment_id: uuid.UUID) -> Assignment:
    found = db.scalar(student_assignments_query(student).where(Assignment.id == assignment_id))
    if found is None:
        raise _404("Assignment")
    return found
