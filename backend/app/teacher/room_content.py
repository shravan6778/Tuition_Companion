import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Room, RoomSubject, Subject


def attach_subject(db: Session, room: Room, subject: Subject) -> None:
    """Both room and subject must already be ownership-checked by the caller."""
    db.add(RoomSubject(room_id=room.id, subject_id=subject.id))
    try:
        db.commit()
    except IntegrityError:  # unique (room_id, subject_id)
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "This subject is already in the room")


def detach_subject(db: Session, room: Room, subject_id: uuid.UUID) -> None:
    """Removes only the link. The subject and its chapters stay in the library."""
    found = db.scalar(
        select(RoomSubject.id).where(RoomSubject.room_id == room.id, RoomSubject.subject_id == subject_id)
    )
    if found is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Subject is not in this room")
    db.execute(delete(RoomSubject).where(RoomSubject.id == found))
    db.commit()