import uuid
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import require_teacher
from app.content_library import access
from app.content_library import feedback
from app.content_library import upload as uploads
from app.content_library.graph_view import chapter_graph
from app.content_library.search import search_books
from app.core.config import settings
from app.core.storage import save_by_hash
from app.db.session import get_db, get_session_factory
from app.models.content import Book, Chapter, ChapterStatus, MatchFeedback, Page, student_book
from app.models.room import RoomMember, RoomType
from app.pipeline import structure
from app.pipeline.jobs import is_actively_processing, mark_processing, run_chapter_job
from app.schemas import BulkLinkOut, ChapterMatchesOut, ChapterMatchOut, BookBrief, BookCreate, BookOut, ChapterCreate, ChapterGraphOut, ChapterOut, VariantOfIn, VariantSuggestionOut, MemberOut, PageOut, RoomCreate, RoomOut
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


@router.post("/rooms/{room_id}/books/{book_id}/link", response_model=BulkLinkOut)
def bulk_link_book(room_id: uuid.UUID, book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Convenience: link a book to every student currently in a single-class room. The links stay per-student
    (the room itself holds no content), and students who join later still link for themselves."""
    room = svc.get_owned_room(db, teacher, room_id)
    if room.room_type != RoomType.single_class:
        raise HTTPException(409, "Bulk linking is for single-class rooms, where everyone uses the same book. "
                                 "In a mixed room, students link their own books.")
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    members = set(db.scalars(select(RoomMember.user_id).where(RoomMember.room_id == room.id)).all())
    already = set(db.scalars(
        select(student_book.c.student_id).where(student_book.c.book_id == book.id, student_book.c.student_id.in_(members))
    ).all()) if members else set()
    new = members - already
    if new:
        db.execute(student_book.insert(), [{"student_id": sid, "book_id": book.id} for sid in new])
        db.commit()
    return BulkLinkOut(linked=len(new), already_linked=len(already), total_students=len(members))


# ---- books (reference corpus + this teacher's own uploads only) ------------------

@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(body: BookCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    if body.variant_of_id is not None:
        # A variant may only point at a book this teacher can already see (never someone else's private book).
        access.get_book_visible_to_teacher(db, teacher, body.variant_of_id)
    draft = None
    if body.draft_id is not None:
        draft = uploads.get_draft(db, teacher, body.draft_id, "front_pages")
    elif settings.require_front_pages:
        raise HTTPException(422, "Upload the book's cover and publisher/edition pages first")
    book = Book(
        board=body.board.strip(),
        class_name=body.class_name.strip(),
        subject=body.subject.strip(),
        publisher=body.publisher.strip(),
        edition=body.edition,
        is_customized=body.is_customized,
        school=body.school,
        variant_of_id=body.variant_of_id,
        is_reference=False,  # reference books are created only by the seed/ingest scripts
        owner_teacher_id=teacher.id,
        metadata_source="front_pages" if draft else "manual",
        extracted_metadata=(draft.payload or {}).get("metadata") if draft else None,
        front_pages_file=draft.source_file if draft else None,
    )
    db.add(book)
    if draft:
        db.delete(draft)  # consumed: the teacher has confirmed the metadata
    db.commit()
    db.refresh(book)
    return book


@router.get("/books", response_model=list[BookOut])
def list_books(
    scope: Literal["all", "mine", "reference"] = "all",
    q: Optional[str] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    subject: Optional[str] = None,
    publisher: Optional[str] = None,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """Search the library: official books + your own. Filters are case-insensitive 'contains';
    `q` matches any of board/class/subject/publisher/edition/school; class 'IX' and 'Class 9' are the same."""
    query = search_books(db, teacher, q=q, board=board, class_name=class_name, subject=subject,
                         publisher=publisher, scope=scope)
    return db.scalars(query).all()


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    return access.get_book_visible_to_teacher(db, teacher, book_id)


@router.post("/books/{book_id}/chapters", response_model=ChapterOut, status_code=status.HTTP_201_CREATED)
def create_chapter(book_id: uuid.UUID, body: ChapterCreate, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, teacher, book_id)
    chapter = Chapter(book_id=book.id, title=body.title, sequence_num=body.sequence_num)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/books/{book_id}/chapters", response_model=list[ChapterOut])
def list_chapters(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    return db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)).all()


def _owned_chapter(db: Session, teacher, book_id: uuid.UUID, chapter_id: uuid.UUID) -> Chapter:
    book = access.get_owned_book(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/pages/upload",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def teacher_upload_pages(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    response: Response,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Saves the file and starts processing in the background. Poll the chapter's `status`.
    Uploading again REPLACES the chapter's pages (one file per chapter)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed. Please wait for it to finish.")

    upload = uploads.read_validated_upload(file, settings.max_upload_mb)
    data, ext, digest = upload.data, upload.ext, upload.sha256
    if chapter.status == ChapterStatus.READY and chapter.source_sha256 == digest:
        response.status_code = status.HTTP_200_OK  # same file as last time: nothing to redo
        return chapter

    chapter.source_file = save_by_hash(data, digest, ext)
    chapter.source_sha256 = digest
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.post(
    "/books/{book_id}/chapters/{chapter_id}/retry",
    response_model=ChapterOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def retry_chapter(
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    teacher=Depends(require_teacher),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    """Re-runs processing on the file already uploaded, after a failure (or a stuck job)."""
    chapter = _owned_chapter(db, teacher, book_id, chapter_id)
    if is_actively_processing(chapter):
        raise HTTPException(status.HTTP_409_CONFLICT, "This chapter is still being processed.")
    if chapter.status not in (ChapterStatus.FAILED, ChapterStatus.PROCESSING) or not chapter.source_file:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nothing to retry for this chapter")
    mark_processing(chapter)
    db.commit()
    db.refresh(chapter)
    background_tasks.add_task(run_chapter_job, chapter.id, teacher.id, session_factory)
    return chapter


@router.get("/books/{book_id}/chapters/{chapter_id}/pages", response_model=list[PageOut])
def list_chapter_pages(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return db.scalars(select(Page).where(Page.chapter_id == chapter.id).order_by(Page.page_number)).all()


@router.get("/books/{book_id}/chapters/{chapter_id}/graph", response_model=ChapterGraphOut)
def get_chapter_graph(book_id: uuid.UUID, chapter_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_book_visible_to_teacher(db, teacher, book_id)
    chapter = db.scalar(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book.id))
    if not chapter:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chapter not found in this book")
    return chapter_graph(db, chapter)


# ---- variants: "this looks like an edition of book X" ---------------------------------------

def _chapter_matches(db: Session, teacher, book: Book) -> list[ChapterMatchesOut]:
    """Per finished chapter of this book: which chapters of OTHER books (official, or the teacher's own) it
    matches. Visibility is re-checked now, because the stored report may be old."""
    chapters = db.scalars(
        select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)
    ).all()
    visible: dict[str, Book | None] = {}
    out = []
    for chapter in chapters:
        matches = []
        for s in (chapter.match_report or {}).get("suggestions", []):
            if s["book_id"] not in visible:
                try:
                    visible[s["book_id"]] = access.get_book_visible_to_teacher(db, teacher, uuid.UUID(s["book_id"]))
                except HTTPException:
                    visible[s["book_id"]] = None
            base = visible[s["book_id"]]
            if base is None:
                continue
            matches.append(ChapterMatchOut(
                book=BookBrief.model_validate(base),
                chapter_id=uuid.UUID(s["chapter_id"]) if s.get("chapter_id") else None,
                chapter_title=s.get("chapter_title"),
                kind=s["kind"], matched_pages=s["matched_pages"], pages_checked=s["pages_checked"],
                avg_similarity=s["avg_similarity"], signal=s.get("signal", "fingerprint"),
            ))
        out.append(ChapterMatchesOut(chapter_id=chapter.id, chapter_title=chapter.title, matches=matches))
    return out


@router.get("/books/{book_id}/chapter-matches", response_model=list[ChapterMatchesOut])
def chapter_matches(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Chapter by chapter: 'your chapter X is identical to / an edition of chapter Y in book Z'.
    Never includes other teachers' private books."""
    return _chapter_matches(db, teacher, access.get_owned_book(db, teacher, book_id))


@router.get("/books/{book_id}/variant-suggestions", response_model=list[VariantSuggestionOut])
def variant_suggestions(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Books that look like the base of this one, judged CHAPTER by chapter: a book is suggested when at least
    half of your finished chapters each match a chapter of it. (Counting pages across the whole book would let
    one long chapter swamp the result, and a partly loaded official book would look like a poor match.)
    Suggestions the teacher dismissed are not offered again."""
    return _variant_suggestions(db, teacher, access.get_owned_book(db, teacher, book_id))


def _variant_suggestions(db: Session, teacher, book: Book) -> list[VariantSuggestionOut]:
    per_chapter = [c for c in _chapter_matches(db, teacher, book)]
    checked = [
        c for c in per_chapter
        if (db.get(Chapter, c.chapter_id).match_report or {}).get("pages_checked", 0) > 0
    ]
    pooled: dict[uuid.UUID, dict] = {}
    for chapter in checked:
        for m in chapter.matches:
            agg = pooled.setdefault(m.book.id, {"book": m.book, "chapters": 0, "pages": 0, "sim_sum": 0.0, "checked": 0})
            agg["chapters"] += 1
            agg["pages"] += m.matched_pages
            agg["sim_sum"] += m.avg_similarity * m.matched_pages
    pages_total = sum((db.get(Chapter, c.chapter_id).match_report or {}).get("pages_checked", 0) for c in checked)

    out = []
    for base_id, agg in pooled.items():
        coverage = agg["chapters"] / len(checked)
        if coverage < settings.variant_min_coverage or base_id == book.variant_of_id:
            continue
        avg = agg["sim_sum"] / agg["pages"]
        loaded = db.scalar(select(func.count()).select_from(Chapter).where(
            Chapter.book_id == base_id, Chapter.status == ChapterStatus.READY)) or 0
        out.append(VariantSuggestionOut(
            book=agg["book"], kind="same" if avg >= settings.reuse_similarity else "variant",
            coverage=round(coverage, 3), matched_chapters=agg["chapters"], chapters_checked=len(checked),
            candidate_chapters_loaded=loaded, avg_similarity=round(avg, 3),
            matched_pages=agg["pages"], pages_checked=pages_total,
        ))
    dismissed = feedback.dismissed_ids(db, book.id)
    out = sorted((v for v in out if v.book.id not in dismissed), key=lambda v: (v.coverage, v.avg_similarity), reverse=True)[:3]
    # Layer 3: books whose chapter titles follow the same order. Only for books the page evidence did not already
    # find, after it and only while there is room; works before a single page has been processed.
    seen = {v.book.id for v in out} | dismissed | ({book.variant_of_id} if book.variant_of_id else set())
    for hit in structure.suggest(db, book, teacher.id, exclude=seen)[: max(0, 3 - len(out))]:
        out.append(VariantSuggestionOut(
            book=BookBrief.model_validate(hit["book"]), kind="variant", coverage=hit["coverage"],
            matched_chapters=hit["matched_chapters"], chapters_checked=hit["chapters_checked"],
            candidate_chapters_loaded=hit["candidate_chapters_loaded"], avg_similarity=hit["avg_overlap"],
            matched_pages=0, pages_checked=0, signal="structure",
        ))
    return out


@router.post("/books/{book_id}/variant-of", response_model=BookOut)
def confirm_variant(book_id: uuid.UUID, body: VariantOfIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """The teacher confirms 'my book is a variant of that one'."""
    book = access.get_owned_book(db, teacher, book_id)
    base = access.get_book_visible_to_teacher(db, teacher, body.base_book_id)
    if base.id == book.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A book can't be a variant of itself")
    ancestor, hops = base, 0
    while ancestor is not None and hops < 50:  # refuse loops: base must not already descend from this book
        if ancestor.variant_of_id == book.id:
            raise HTTPException(status.HTTP_409_CONFLICT, "That book is already a variant of this one")
        ancestor = db.get(Book, ancestor.variant_of_id) if ancestor.variant_of_id else None
        hops += 1
    shown = next((v for v in _variant_suggestions(db, teacher, book) if v.book.id == base.id), None)  # what the teacher was shown
    if book.variant_of_id is not None and book.variant_of_id != base.id:
        feedback.record(db, book.id, book.variant_of_id, "retracted")  # switched to a different base
    feedback.record(db, book.id, base.id, "confirmed", shown.model_dump(mode="json", exclude={"book"}) if shown else None)
    book.variant_of_id = base.id
    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}/variant-of", status_code=status.HTTP_204_NO_CONTENT)
def clear_variant(book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    book = access.get_owned_book(db, teacher, book_id)
    if book.variant_of_id is not None:
        feedback.record(db, book.id, book.variant_of_id, "retracted")  # a correction; the suggestion may be offered again
    book.variant_of_id = None
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/books/{book_id}/variant-suggestions/dismiss", status_code=status.HTTP_204_NO_CONTENT)
def dismiss_variant_suggestion(book_id: uuid.UUID, body: VariantOfIn, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """'No, that is not the base of my book': the suggestion is not offered again for this book."""
    book = access.get_owned_book(db, teacher, book_id)
    base = access.get_book_visible_to_teacher(db, teacher, body.base_book_id)
    if base.id == book.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "A book can't be a variant of itself")
    if base.id == book.variant_of_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "You confirmed this book as the base; clear that first")
    shown = next((v for v in _variant_suggestions(db, teacher, book) if v.book.id == base.id), None)
    feedback.record(db, book.id, base.id, "dismissed", shown.model_dump(mode="json", exclude={"book"}) if shown else None)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/books/{book_id}/variant-suggestions/dismiss/{base_book_id}", status_code=status.HTTP_204_NO_CONTENT)
def undo_dismiss(book_id: uuid.UUID, base_book_id: uuid.UUID, teacher=Depends(require_teacher), db: Session = Depends(get_db)):
    """Offer a dismissed suggestion again (idempotent)."""
    book = access.get_owned_book(db, teacher, book_id)
    row = db.scalar(select(MatchFeedback).where(
        MatchFeedback.book_id == book.id, MatchFeedback.base_book_id == base_book_id, MatchFeedback.decision == "dismissed"))
    if row is not None:
        db.delete(row)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# front-pages drafts, whole-textbook upload, and student chapter requests live in their own modules
from app.teacher.request_routes import router as _request_router  # noqa: E402
from app.teacher.upload_routes import router as _upload_router  # noqa: E402

router.include_router(_upload_router)
router.include_router(_request_router)
