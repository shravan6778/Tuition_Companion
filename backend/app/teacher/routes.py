import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.db.session import get_db
from app.schemas import ChapterOut, MemberOut, RoomCreate, RoomOut, SubjectCreate, SubjectOut
from app.teacher import chapters as chap
from app.teacher import library as lib
from app.teacher import rooms as svc

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


@router.get("/ping")
def ping(user=Depends(require_teacher)):
    return {"role": user.role}


@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(body: RoomCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.create_room(db, teacher, body.name, body.room_type)


@router.get("/rooms", response_model=list[RoomOut])
def list_rooms(teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return svc.list_rooms(db, teacher)


@router.get("/rooms/{room_id}/members", response_model=list[MemberOut])
def room_members(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    return svc.list_members(db, room)

@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(body: SubjectCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return SubjectOut.model_validate(lib.create_subject(db, teacher, body.name, body.grade))


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return lib.list_subjects(db, teacher)

@router.post(
    "/subjects/{subject_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED
)
def upload_chapter(
    subject_id: uuid.UUID,
    title: str = Form(min_length=2, max_length=200),
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    return chap.upload_chapter(db, subject, title.strip(), file)


@router.get("/subjects/{subject_id}/chapters", response_model=list[ChapterOut])
def list_chapters(subject_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    return chap.list_chapters(db, subject)