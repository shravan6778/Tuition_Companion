"""Assignment creation and per-student target resolution."""
import uuid
from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.assignments.scope import chapter_concepts, propose_exercise_concepts, subject_concepts
from app.content_library import access
from app.models import Assignment, AssignmentConcept, AssignmentLevel, Book, Chapter, ChapterStatus, Concept, Page, Room, RoomMember, User
from app.pipeline.concepts import extract_item_labels
from app.pipeline.graph import loose_key


def _404(what: str = "Assignment") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{what} not found")


def ready_chapter(db: Session, book: Book, chapter_id: uuid.UUID | None) -> Chapter:
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id)) if chapter_id else None
    if chapter is None:
        raise _404("Chapter")
    if chapter.status != ChapterStatus.READY:
        raise HTTPException(status.HTTP_409_CONFLICT, "That chapter isn't ready yet, so it can't be assigned")
    return chapter


def _target(db: Session, teacher: User, room_id: uuid.UUID | None, student_id: uuid.UUID | None):
    if (room_id is None) == (student_id is None):
        raise HTTPException(422, "Provide exactly one of room_id or student_id")
    if room_id is not None:
        room = db.scalar(select(Room).where(Room.id == room_id, Room.teacher_id == teacher.id))
        if room is None:
            raise _404("Room")
        return room, None
    member = db.scalar(
        select(RoomMember).join(Room, Room.id == RoomMember.room_id).where(
            Room.teacher_id == teacher.id, RoomMember.user_id == student_id
        )
    )
    if member is None:
        raise _404("Student")
    return None, db.get(User, student_id)


def _source_book(db: Session, teacher: User, book_id: uuid.UUID) -> Book:
    # A teacher may use a reference book or a private book belonging to a student in their room
    # purely as a metadata/template source. Page text/images are never returned by this function.
    return access.get_book_metadata_visible_to_teacher(db, teacher, book_id)


def _valid_concepts(db: Session, book: Book, concept_ids: list[uuid.UUID], chapter: Chapter | None = None) -> list[Concept]:
    unique = list(dict.fromkeys(concept_ids))
    if not unique:
        return []
    query = select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id).where(
        Concept.id.in_(unique), Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY,
        Concept.is_canonical.is_(True))
    if chapter is not None:
        query = query.where(Chapter.id == chapter.id)
    found = list(db.scalars(query))
    by_id = {c.id: c for c in found}
    if len(by_id) != len(unique):
        raise _404("Concept")
    return [by_id[cid] for cid in unique]


@dataclass
class NewAssignment:
    level: str
    book_id: uuid.UUID
    room_id: uuid.UUID | None = None
    student_id: uuid.UUID | None = None
    chapter_id: uuid.UUID | None = None
    concept_ids: list[uuid.UUID] | None = None
    concept_names: list[str] | None = None
    item_label: str | None = None
    title: str | None = None
    due_date: date | None = None


def _concept_rows(concepts: list[Concept]):
    return [AssignmentConcept(concept_id=c.id, concept_name=c.name, concept_key=loose_key(c.name), position=i)
            for i, c in enumerate(concepts)]


def create_assignment(db: Session, teacher: User, new: NewAssignment) -> Assignment:
    book = _source_book(db, teacher, new.book_id)
    room_id, student_id = _target(db, teacher, new.room_id, new.student_id)
    chapter, concepts = None, []
    item_label = (new.item_label or "").strip() or None

    if new.level == AssignmentLevel.SUBJECT:
        concepts = subject_concepts(db, [book.id], book.subject)
    elif new.level == AssignmentLevel.CHAPTER:
        chapter = ready_chapter(db, book, new.chapter_id)
        concepts = chapter_concepts(db, chapter.id)
    elif new.level == AssignmentLevel.CONCEPT:
        chapter = ready_chapter(db, book, new.chapter_id)
        if new.concept_names:
            wanted = {loose_key(n) for n in new.concept_names if n.strip()}
            concepts = [c for c in chapter_concepts(db, chapter.id) if loose_key(c.name) in wanted]
            if len(concepts) != len(wanted):
                raise HTTPException(422, "One or more selected concepts are not in this chapter")
        else:
            concepts = _valid_concepts(db, book, new.concept_ids or [], chapter)
        if not concepts:
            raise HTTPException(422, "Pick at least one concept")
    elif new.level == AssignmentLevel.EXERCISE:
        chapter = ready_chapter(db, book, new.chapter_id)
        if not item_label:
            raise HTTPException(422, "Provide an exercise/item label")
        pages = list(db.scalars(select(Page).where(Page.chapter_id == chapter.id, Page.page_kind == "exercise")))
        labels = {label.casefold() for p in pages for label in extract_item_labels(p.content_text)}
        if item_label.casefold() not in labels:
            raise HTTPException(404, "Exercise/item label not found")
        # The proposal may still use vectors, but the persisted target is only the compact label + concept names.
        concepts = chapter_concepts(db, chapter.id)
        if new.concept_names:
            wanted = {loose_key(n) for n in new.concept_names if n.strip()}
            concepts = [c for c in chapter_concepts(db, chapter.id) if loose_key(c.name) in wanted]
        elif new.concept_ids:
            concepts = _valid_concepts(db, book, new.concept_ids, chapter)

    if new.level != AssignmentLevel.SUBJECT and chapter is None:
        raise HTTPException(422, "A chapter is required for this assignment level")

    assignment = Assignment(
        teacher_id=teacher.id, room_id=room_id, student_id=student_id,
        subject=book.subject.strip(), chapter_title=chapter.title if chapter else None,
        item_label=item_label, level=new.level,
        title=(new.title or (chapter.title if chapter else f"{book.subject} work"))[:200], due_date=new.due_date,
    )
    assignment.concepts = _concept_rows(concepts)
    db.add(assignment); db.commit(); db.refresh(assignment)
    return assignment


def exercise_proposal(db: Session, teacher: User, book_id: uuid.UUID, chapter_id: uuid.UUID, page_numbers: list[int] | None):
    book = _source_book(db, teacher, book_id)
    chapter = ready_chapter(db, book, chapter_id)
    return chapter, propose_exercise_concepts(db, chapter, page_numbers or None)


def get_teacher_assignment(db: Session, teacher: User, assignment_id: uuid.UUID) -> Assignment:
    found = db.scalar(select(Assignment).where(Assignment.id == assignment_id, Assignment.teacher_id == teacher.id))
    if found is None:
        raise _404()
    return found


def list_teacher_assignments(db: Session, teacher: User, room_id=None, student_id=None):
    query = select(Assignment).where(Assignment.teacher_id == teacher.id)
    if room_id is not None: query = query.where(Assignment.room_id == room_id)
    if student_id is not None:
        my_rooms = select(RoomMember.room_id).join(Room, Room.id == RoomMember.room_id).where(
            Room.teacher_id == teacher.id, RoomMember.user_id == student_id)
        query = query.where(or_(Assignment.student_id == student_id, Assignment.room_id.in_(my_rooms)))
    return list(db.scalars(query.order_by(Assignment.created_at.desc())))


def student_assignments_query(student: User):
    my_rooms = select(RoomMember.room_id).where(RoomMember.user_id == student.id)
    return select(Assignment).where(or_(Assignment.student_id == student.id, Assignment.room_id.in_(my_rooms)))


def list_student_assignments(db: Session, student: User) -> list[Assignment]:
    items = list(db.scalars(student_assignments_query(student).order_by(Assignment.created_at.desc())))
    return sorted(items, key=lambda a: (a.due_date is None, a.due_date or date.max))


def resolve_student_target(db: Session, student: User, assignment: Assignment):
    """Resolve a metadata target against the student's own private book(s)."""
    books = list(db.scalars(select(Book).where(Book.owner_student_id == student.id, Book.subject.ilike(assignment.subject))))
    for book in books:
        chapter = None
        if assignment.chapter_title:
            chapters = db.scalars(select(Chapter).where(
                Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY,
            )).all()
            key = loose_key(assignment.chapter_title)
            chapter = next((c for c in chapters if loose_key(c.title) == key), None)
            if chapter is None:
                continue
        if assignment.item_label and chapter is not None:
            labels = {label.casefold() for p in db.scalars(select(Page).where(Page.chapter_id == chapter.id, Page.page_kind == "exercise"))
                      for label in extract_item_labels(p.content_text)}
            if assignment.item_label.casefold() not in labels:
                continue
        return book, chapter
    return None, None


def get_student_assignment(db: Session, student: User, assignment_id: uuid.UUID) -> Assignment:
    found = db.scalar(student_assignments_query(student).where(Assignment.id == assignment_id))
    if found is None:
        raise _404()
    return found
