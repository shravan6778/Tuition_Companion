import uuid
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.content_library.search import search_books
from app.core.config import settings
from app.db.session import get_db
from app.models.content import Book, Chapter, ChapterStatus, Concept, MatchFeedback, Page, PageItem
from app.models.assignment import Assignment
from app.core.codes import generate_unique_code
from app.models.room import Room, RoomJoinRequest, RoomMember, RoomType
from app.models.user import User
from app.schemas import BookOut, ChapterOut, BookBrief, MemberOut, RoomCreate, RoomOut, RoomJoinRequestOut, RoomDeleteIn, RoomDeleteOut
from app.teacher import rooms as svc

router = APIRouter(prefix="/teacher", tags=["teacher"], dependencies=[Depends(require_teacher)])


@router.get("/ping")
def ping(user=Depends(require_teacher)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

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


@router.get("/rooms/{room_id}/join-requests", response_model=list[RoomJoinRequestOut])
def room_join_requests(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    rows = db.execute(
        select(RoomJoinRequest, User.name)
        .join(User, User.id == RoomJoinRequest.user_id)
        .where(RoomJoinRequest.room_id == room.id, RoomJoinRequest.status == "pending")
        .order_by(RoomJoinRequest.created_at)
    ).all()
    return [RoomJoinRequestOut(id=req.id, room_id=req.room_id, student_id=req.user_id,
                               student_name=name, status=req.status, created_at=req.created_at)
            for req, name in rows]


@router.post("/rooms/{room_id}/join-requests/{request_id}/approve", response_model=MemberOut)
def approve_room_join_request(room_id: uuid.UUID, request_id: uuid.UUID,
                              teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    req = db.scalar(select(RoomJoinRequest).where(
        RoomJoinRequest.id == request_id, RoomJoinRequest.room_id == room.id,
        RoomJoinRequest.status == "pending"))
    if req is None:
        raise HTTPException(404, "Pending join request not found")
    student = db.get(User, req.user_id)
    if student is None:
        raise HTTPException(404, "Student not found")
    member = db.scalar(select(RoomMember).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id))
    if member is None:
        member = RoomMember(room_id=room.id, user_id=student.id)
        db.add(member)
    req.status = "approved"
    db.commit()
    db.refresh(member)
    return MemberOut(id=student.id, name=student.name, joined_at=member.joined_at)


@router.post("/rooms/{room_id}/join-requests/{request_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
def reject_room_join_request(room_id: uuid.UUID, request_id: uuid.UUID,
                             teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    req = db.scalar(select(RoomJoinRequest).where(
        RoomJoinRequest.id == request_id, RoomJoinRequest.room_id == room.id,
        RoomJoinRequest.status == "pending"))
    if req is None:
        raise HTTPException(404, "Pending join request not found")
    req.status = "rejected"
    db.commit()


@router.delete("/rooms/{room_id}/members/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_room_member(room_id: uuid.UUID, student_id: uuid.UUID,
                       teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    member = db.scalar(select(RoomMember).where(RoomMember.room_id == room.id, RoomMember.user_id == student_id))
    if member is None:
        raise HTTPException(404, "Room member not found")
    db.delete(member)
    db.commit()


@router.post("/rooms/{room_id}/regenerate-join-code", response_model=RoomOut)
def regenerate_room_join_code(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    room.join_code = generate_unique_code(
        lambda code: db.scalar(select(Room.id).where(Room.join_code == code)) is not None, length=6)
    db.commit()
    db.refresh(room)
    return room


@router.get("/rooms/{room_id}/delete-preview")
def room_delete_preview(room_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    count = db.scalar(select(func.count(Assignment.id)).where(Assignment.room_id == room.id)) or 0
    return {"room_id": room.id, "room_name": room.name, "assignments_deleted": count}


@router.delete("/rooms/{room_id}", response_model=RoomDeleteOut)
def delete_room(room_id: uuid.UUID, body: RoomDeleteIn,
                teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    room = svc.get_owned_room(db, teacher, room_id)
    if body.confirm_name.strip() != room.name:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Typed room name does not match")
    count = db.scalar(select(func.count(Assignment.id)).where(Assignment.room_id == room.id)) or 0
    # Explicit deletion keeps this reliable on databases where FK cascade enforcement differs.
    db.query(Assignment).filter(Assignment.room_id == room.id).delete(synchronize_session=False)
    db.query(RoomJoinRequest).filter(RoomJoinRequest.room_id == room.id).delete(synchronize_session=False)
    db.query(RoomMember).filter(RoomMember.room_id == room.id).delete(synchronize_session=False)
    db.delete(room)
    db.commit()
    return RoomDeleteOut(deleted=True, assignments_deleted=count)




# ---- privacy-safe student book outlines ------------------------------------
from app.pipeline.concepts import extract_item_labels


@router.get("/students/{student_id}/books", response_model=list[dict])
def student_book_outlines(student_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Teacher-safe view: metadata, chapter titles, concept names and exercise/item labels only.

    No page text, images, stored PDFs or page layouts are returned.
    """
    member = db.scalar(
        select(RoomMember).join(Room, Room.id == RoomMember.room_id).where(
            Room.teacher_id == teacher.id, RoomMember.user_id == student_id
        )
    )
    if member is None:
        raise HTTPException(404, "Student not found in your rooms")

    books = db.scalars(
        select(Book).where(Book.owner_student_id == student_id).order_by(Book.subject, Book.class_name, Book.publisher)
    ).all()
    out = []
    for book in books:
        chapters_out = []
        chapters = db.scalars(
            select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)
        ).all()
        for chapter in chapters:
            concepts = db.scalars(
                select(Concept.name)
                .join(Page, Page.id == Concept.page_id)
                .where(Page.chapter_id == chapter.id, Concept.is_canonical.is_(True))
                .order_by(Page.page_number, Concept.position)
            ).all()
            labels = db.scalars(
                select(PageItem.label).join(Page, Page.id == PageItem.page_id)
                .where(Page.chapter_id == chapter.id, PageItem.label.is_not(None))
                .order_by(Page.page_number, PageItem.position)
            ).all()
            chapters_out.append({
                "id": chapter.id,
                "title": chapter.title,
                "sequence_num": chapter.sequence_num,
                "status": chapter.status,
                "concept_names": list(dict.fromkeys(concepts)),
                "item_labels": list(dict.fromkeys(labels)),
            })
        out.append({
            "id": book.id,
            "board": book.board,
            "class_name": book.class_name,
            "subject": book.subject,
            "publisher": book.publisher,
            "edition": book.edition,
            "is_customized": book.is_customized,
            "school": book.school,
            "chapters": chapters_out,
        })
    return out


@router.get("/books", response_model=list[BookOut])
def list_reference_books(
    scope: Literal["all", "reference"] = "reference",
    q: Optional[str] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    publisher: Optional[str] = None,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Teachers can search only the platform reference corpus."""
    query = search_books(db, teacher, q=q, board=board, class_name=class_name, subject=subject,
                         publisher=publisher, scope="reference")
    books = db.scalars(query).all()
    result = []
    for book in books:
        out = BookOut.model_validate(book)
        enriched = []
        for c in book.chapters:
            concepts = db.scalars(select(Concept.name).join(Page, Page.id == Concept.page_id).where(
                Page.chapter_id == c.id, Concept.is_canonical.is_(True)).order_by(Page.page_number, Concept.position)).all()
            labels = db.scalars(
                select(PageItem.label).join(Page, Page.id == PageItem.page_id)
                .where(Page.chapter_id == c.id, PageItem.label.is_not(None))
                .order_by(Page.page_number, PageItem.position)
            ).all()
            enriched.append(ChapterOut.model_validate({**c.__dict__, "concept_names": list(dict.fromkeys(concepts)), "item_labels": list(dict.fromkeys(labels))}))
        out.chapters = enriched
        result.append(out)
    return result


@router.get("/books/{book_id}", response_model=BookOut)
def get_reference_book(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return access.get_book_visible_to_teacher(db, teacher, book_id)
