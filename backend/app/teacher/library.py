import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Chapter, Subject, User
from app.schemas import SubjectOut


def create_subject(db: Session, teacher: User, name: str, grade: str | None) -> Subject:
    subject = Subject(teacher_id=teacher.id, name=name, grade=grade)
    db.add(subject)
    try:
        db.commit()
    except IntegrityError:  # unique (teacher_id, name)
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You already have a subject with this name")
    db.refresh(subject)
    return subject


def list_subjects(db: Session, teacher: User) -> list[SubjectOut]:
    rows = db.execute(
        select(Subject, func.count(Chapter.id))
        .outerjoin(Chapter, Chapter.subject_id == Subject.id)
        .where(Subject.teacher_id == teacher.id)
        .group_by(Subject.id)
        .order_by(Subject.created_at.desc())
    ).all()
    return [SubjectOut.model_validate(s).model_copy(update={"chapter_count": n}) for s, n in rows]


def get_owned_subject(db: Session, teacher: User, subject_id: uuid.UUID) -> Subject:
    """Ownership check: another teacher's subject looks like it doesn't exist."""
    subject = db.scalar(select(Subject).where(Subject.id == subject_id, Subject.teacher_id == teacher.id))
    if subject is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject not found")
    return subject