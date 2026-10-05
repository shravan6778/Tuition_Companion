from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_parent
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models import ParentStudentLink, Role, Room, RoomMember, User
from app.schemas import ChildOut, LinkStudentIn, RoomBrief

router = APIRouter(prefix="/parent", tags=["parent"], dependencies=[Depends(require_parent)])


@router.get("/ping")
def ping(user=Depends(require_parent)):
    return {"role": user.role}


@router.post("/link", response_model=ChildOut)
def link_student(body: LinkStudentIn, parent=Depends(require_parent), db: Session = Depends(get_db)):
    limiter.check("parent-link", str(parent.id), settings.rate_parent_link_per_min, 60)
    student = db.scalar(select(User).where(User.link_code == body.link_code, User.role == Role.student))
    if student is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid link code")
    exists = db.scalar(
        select(ParentStudentLink.id).where(
            ParentStudentLink.parent_id == parent.id, ParentStudentLink.student_id == student.id
        )
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already linked")
    try:
        db.add(ParentStudentLink(parent_id=parent.id, student_id=student.id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Already linked")
    return _child(db, student)


@router.get("/children", response_model=list[ChildOut])
def children(parent=Depends(require_parent), db: Session = Depends(get_db)):
    # Scoped query: only students linked to THIS parent are ever returned.
    students = db.scalars(
        select(User)
        .join(ParentStudentLink, ParentStudentLink.student_id == User.id)
        .where(ParentStudentLink.parent_id == parent.id)
    ).all()
    return [_child(db, s) for s in students]


def _child(db: Session, student: User) -> ChildOut:
    rooms = db.scalars(
        select(Room).join(RoomMember, RoomMember.room_id == Room.id).where(RoomMember.user_id == student.id)
    ).all()
    return ChildOut(id=student.id, name=student.name, rooms=[RoomBrief(id=r.id, name=r.name) for r in rooms])