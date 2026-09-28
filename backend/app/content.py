"""Read-side queries shared by teacher and student routes. Content is a library;
rooms only reference it through room_subjects (never copied)."""
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models import Chapter, ChapterStatus, Room, RoomMember, RoomSubject, Subject, User
from app.schemas import SubjectOut


def list_room_subjects(db: Session, room_id: uuid.UUID, ready_only: bool = False) -> list[SubjectOut]:
    """Subjects attached to a room. With ready_only, chapter_count only counts chapters students can see."""
    join_cond = Chapter.subject_id == Subject.id
    if ready_only:
        join_cond = and_(join_cond, Chapter.status == ChapterStatus.ready)
    rows = db.execute(
        select(Subject, func.count(Chapter.id))
        .join(RoomSubject, RoomSubject.subject_id == Subject.id)
        .outerjoin(Chapter, join_cond)
        .where(RoomSubject.room_id == room_id)
        .group_by(Subject.id, RoomSubject.created_at)
        .order_by(RoomSubject.created_at)
    ).all()
    return [SubjectOut.model_validate(s).model_copy(update={"chapter_count": n}) for s, n in rows]


def get_member_room(db: Session, student: User, room_id: uuid.UUID) -> Room | None:
    """The room, only if this student has joined it."""
    return db.scalar(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(Room.id == room_id, RoomMember.user_id == student.id)
    )