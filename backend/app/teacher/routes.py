import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.db.session import get_db, get_session_factory
from app import content
from app.models import ChapterStatus
from app.schemas import AttachSubjectIn, ChapterOut, MemberOut, RoomCreate, RoomOut, SubjectCreate, SubjectOut
from app.teacher import chapters as chap
from app.teacher import processing
from app.teacher import library as lib
from app.teacher import room_content as rc
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
    background_tasks: BackgroundTasks,
    title: str = Form(min_length=2, max_length=200),
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    chapter = chap.upload_chapter(db, subject, title.strip(), file)
    background_tasks.add_task(processing.process_chapter, session_factory, chapter.id)
    return chapter

@router.get("/subjects/{subject_id}/chapters", response_model=list[ChapterOut])
def list_chapters(subject_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    return chap.list_chapters(db, subject)

@router.post("/rooms/{room_id}/subjects", response_model=list[SubjectOut], status_code=status.HTTP_201_CREATED)
def attach_subject(
    room_id: uuid.UUID, body: AttachSubjectIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)
):
    room = svc.get_owned_room(db, teacher, room_id)
    subject = lib.get_owned_subject(db, teacher, body.subject_id)
    rc.attach_subject(db, room, subject)
    return content.list_room_subjects(db, room.id)


@router.get("/rooms/{room_id}/subjects", response_model=list[SubjectOut])
def room_subjects(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    return content.list_room_subjects(db, room.id)


@router.delete("/rooms/{room_id}/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_subject(
    room_id: uuid.UUID, subject_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)
):
    room = svc.get_owned_room(db, teacher, room_id)
    rc.detach_subject(db, room, subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/subjects/{subject_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chapter(
    subject_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)
):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    chap.delete_chapter(db, subject, chapter_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    "/subjects/{subject_id}/chapters/{chapter_id}/retry",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_chapter(
    subject_id: uuid.UUID,
    chapter_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    subject = lib.get_owned_subject(db, teacher, subject_id)
    chapter = chap.get_owned_chapter(db, subject, chapter_id)
    if chapter.status != ChapterStatus.failed:
        raise HTTPException(status.HTTP_409_CONFLICT, "Only a failed chapter can be retried")
    # process_chapter itself flips uploaded/failed -> processing, so don't set it here.
    background_tasks.add_task(processing.process_chapter, session_factory, chapter.id)
    return chapter