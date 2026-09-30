import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.codes import generate_unique_code
from app.models import Room, RoomMember, RoomType, User
from app.schemas import MemberOut, RoomOut


def create_room(db: Session, teacher: User, name: str, room_type: RoomType) -> Room:
    code = generate_unique_code(
        lambda c: db.scalar(select(Room.id).where(Room.join_code == c)) is not None, length=6
    )
    room = Room(teacher_id=teacher.id, name=name, room_type=room_type, join_code=code)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def list_rooms(db: Session, teacher: User) -> list[RoomOut]:
    rows = db.execute(
        select(Room, func.count(RoomMember.id))
        .outerjoin(RoomMember, RoomMember.room_id == Room.id)
        .where(Room.teacher_id == teacher.id)
        .group_by(Room.id)
        .order_by(Room.created_at.desc())
    ).all()
    return [RoomOut.model_validate(room).model_copy(update={"member_count": n}) for room, n in rows]


def get_owned_room(db: Session, teacher: User, room_id: uuid.UUID) -> Room:
    """Ownership check: another teacher's room looks like it doesn't exist."""
    room = db.scalar(select(Room).where(Room.id == room_id, Room.teacher_id == teacher.id))
    if room is None:
        raise HTTPException(404, "Room not found")
    return room


def list_members(db: Session, room: Room) -> list[MemberOut]:
    from app.schemas import MemberOut
    from app.models.user import User
    from app.models.room import RoomMember
    
    rows = db.execute(
        select(User.id, User.name, RoomMember.joined_at)
        .join(RoomMember, RoomMember.user_id == User.id)
        .where(RoomMember.room_id == room.id)
        .order_by(RoomMember.joined_at)
    ).all()
    
    # We now map the tuple (id, name, joined_at) directly to the schema
    return [MemberOut(id=row.id, name=row.name, joined_at=row.joined_at) for row in rows]