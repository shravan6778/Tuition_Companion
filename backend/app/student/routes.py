from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.db.session import get_db
from app.models import Room, RoomMember
from app.schemas import JoinRoomIn, RoomOut

router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}


@router.post("/rooms/join", response_model=RoomOut)
def join_room(body: JoinRoomIn, student=Depends(require_student), db: Session = Depends(get_db)):
    room = db.scalar(select(Room).where(Room.join_code == body.join_code))
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid join code")
    already = db.scalar(
        select(RoomMember.id).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id)
    )
    if already:
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    try:
        db.add(RoomMember(room_id=room.id, user_id=student.id))
        db.commit()
    except IntegrityError:  # double-tap race, caught by the unique constraint
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    return room


@router.get("/rooms", response_model=list[RoomOut])
def my_rooms(student=Depends(require_student), db: Session = Depends(get_db)):
    return db.scalars(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
        .order_by(RoomMember.joined_at.desc())
    ).all()