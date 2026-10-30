import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import require_student
from app.content_library import access
from app.content_library.graph_view import chapter_graph
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.session import get_db
from app.models.content import Book, Chapter, ChapterStatus, Page, student_book
from app.models.room import Room, RoomJoinRequest, RoomMember
from app.schemas import BookOut, ChapterGraphOut, JoinRoomIn, PageOut, RoomOut
from datetime import datetime, timezone
from app.models import ParentStudentLink, User
from app.models.links import ParentLinkStatus
from app.schemas import ParentLinkRequestOut

def _student_view(book: Book) -> BookOut:
    """Students only see chapters that finished processing."""
    out = BookOut.model_validate(book)
    out.chapters = [c for c in out.chapters if c.status == ChapterStatus.READY]
    return out


router = APIRouter(prefix="/student", tags=["student"], dependencies=[Depends(require_student)])


@router.get("/ping")
def ping(user=Depends(require_student)):
    return {"role": user.role}


# ---- rooms -----------------------------------------------------------------

@router.post("/rooms/join", response_model=RoomOut, status_code=status.HTTP_202_ACCEPTED)
def join_room(body: JoinRoomIn, student=Depends(require_student), db: Session = Depends(get_db)):
    limiter.check("join-room", str(student.id), settings.rate_join_per_min, 60)
    room = db.scalar(select(Room).where(func.lower(Room.join_code) == body.join_code.lower()))
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invalid join code")
    if db.scalar(select(RoomMember.id).where(RoomMember.room_id == room.id, RoomMember.user_id == student.id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "You are already in this room")
    existing = db.scalar(select(RoomJoinRequest).where(RoomJoinRequest.room_id == room.id, RoomJoinRequest.user_id == student.id))
    if existing and existing.status == "pending":
        raise HTTPException(status.HTTP_409_CONFLICT, "Your join request is already pending")
    if existing:
        existing.status = "pending"
        existing.created_at = datetime.now(timezone.utc)
    else:
        db.add(RoomJoinRequest(room_id=room.id, user_id=student.id, status="pending"))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A join request already exists")
    return room


@router.get("/rooms", response_model=list[RoomOut])
def my_rooms(student=Depends(require_student), db: Session = Depends(get_db)):
    """Return only rooms the student has been approved to join."""
    return db.scalars(
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == student.id)
        .order_by(RoomMember.joined_at.desc())
    ).all()


@router.get("/rooms/requests")
def my_room_requests(student=Depends(require_student), db: Session = Depends(get_db)):
    rows = db.execute(select(RoomJoinRequest, Room.name).join(Room, Room.id == RoomJoinRequest.room_id)
                      .where(RoomJoinRequest.user_id == student.id, RoomJoinRequest.status == "pending")
                      .order_by(RoomJoinRequest.created_at.desc())).all()
    return [{"id": req.id, "room_id": req.room_id, "room_name": name, "status": req.status,
             "created_at": req.created_at} for req, name in rows]


@router.delete("/rooms/{room_id}/join-request", status_code=status.HTTP_204_NO_CONTENT)
def cancel_room_request(room_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    req = db.scalar(select(RoomJoinRequest).where(RoomJoinRequest.room_id == room_id,
                       RoomJoinRequest.user_id == student.id, RoomJoinRequest.status == "pending"))
    if req is None:
        raise HTTPException(404, "Pending join request not found")
    db.delete(req)
    db.commit()


@router.delete("/rooms/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_room(room_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    member = db.scalar(select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == student.id))
    if member is None:
        raise HTTPException(404, "You are not a member of this room")
    db.delete(member)
    db.commit()


# ---- books -----------------------------------------------------------------

@router.get("/library", response_model=list[BookOut])
def library(student=Depends(require_student), db: Session = Depends(get_db)):
    """Reference books the student has not linked yet. Private books are automatically owned/visible."""
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    query = access.student_visible_books(student).where(Book.id.not_in(linked))
    books = db.scalars(query.order_by(Book.is_reference.desc(), Book.board, Book.class_name, Book.subject)).all()
    return [_student_view(b) for b in books]


@router.get("/books", response_model=list[BookOut])
def my_books(student=Depends(require_student), db: Session = Depends(get_db)):
    linked = select(student_book.c.book_id).where(student_book.c.student_id == student.id)
    books = db.scalars(
        select(Book).where(or_(Book.owner_student_id == student.id, Book.id.in_(linked)))
        .order_by(Book.is_reference.desc(), Book.subject, Book.class_name)
    ).all()
    return [_student_view(b) for b in books]


@router.get("/books/{book_id}", response_model=BookOut)
def get_book_details(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    return _student_view(access.get_book_visible_to_student(db, student, book_id))


@router.post("/books/{book_id}/link", status_code=status.HTTP_200_OK)
def link_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_student(db, student, book_id)
    if not book.is_reference:
        raise HTTPException(status.HTTP_409_CONFLICT, "Your own books are already available and do not need linking")
    existing = db.execute(
        select(student_book).where(student_book.c.student_id == student.id, student_book.c.book_id == book.id)
    ).first()
    if existing:
        return {"status": "already_linked", "book_id": book.id}
    db.execute(student_book.insert().values(student_id=student.id, book_id=book.id))
    db.commit()
    return {"status": "linked", "book_id": book.id}


@router.delete("/books/{book_id}/link", status_code=status.HTTP_204_NO_CONTENT)
def unlink_book(book_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    db.execute(student_book.delete().where(student_book.c.student_id == student.id, student_book.c.book_id == book_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def get_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_linked_book(db, student, book_id)  # page content only for books the student has linked
    chapter = db.scalar(
        select(Chapter).where(
            Chapter.id == chapter_id, Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY
        )
    )
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()


@router.get("/books/{book_id}/chapters/{chapter_id}/graph", response_model=ChapterGraphOut)
def get_chapter_graph(book_id: uuid.UUID, chapter_id: uuid.UUID, student=Depends(require_student), db: Session = Depends(get_db)):
    book = access.get_linked_book(db, student, book_id)
    chapter = db.scalar(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY)
    )
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found")
    return chapter_graph(db, chapter)



def _parent_link_out(link: ParentStudentLink, parent: User) -> ParentLinkRequestOut:
    return ParentLinkRequestOut(
        id=link.id,
        parent_id=parent.id,
        parent_name=parent.name,
        parent_username=parent.username,
        status=link.status,
        created_at=link.created_at,
        approved_at=link.approved_at,
    )


@router.get("/parent-links", response_model=list[ParentLinkRequestOut])
def list_parent_links(
    student: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(ParentStudentLink, User)
        .join(User, User.id == ParentStudentLink.parent_id)
        .where(ParentStudentLink.student_id == student.id)
        .order_by(ParentStudentLink.created_at.desc())
    ).all()
    return [_parent_link_out(link, parent) for link, parent in rows]


@router.post("/parent-links/{link_id}/approve", response_model=ParentLinkRequestOut)
def approve_parent_link(
    link_id: uuid.UUID,
    student: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    row = db.execute(
        select(ParentStudentLink, User)
        .join(User, User.id == ParentStudentLink.parent_id)
        .where(ParentStudentLink.id == link_id, ParentStudentLink.student_id == student.id)
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent link request not found")
    link, parent = row
    if link.status != ParentLinkStatus.APPROVED:
        link.status = ParentLinkStatus.APPROVED
        link.approved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(link)
    return _parent_link_out(link, parent)


@router.delete("/parent-links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def reject_or_remove_parent_link(
    link_id: uuid.UUID,
    student: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    link = db.scalar(
        select(ParentStudentLink).where(
            ParentStudentLink.id == link_id,
            ParentStudentLink.student_id == student.id,
        )
    )
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent link request not found")
    db.delete(link)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)