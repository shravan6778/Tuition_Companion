"""Front-pages-first upload, library search, whole-textbook upload, bulk link, chapter requests."""
import io
import uuid

import pypdf
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models import Book, Chapter, ChapterRequest, Role, UploadDraft
from app.content_library.search import normalize_class
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_chapter_jobs import chapter_status, page_count, upload
from tests.test_pipeline import _text_pdf

FRONT = ["Board: CBSE", "Class: IX", "Subject: Science", "Publisher: NCERT", "Edition: First edition 2025"]


def front_pdf(lines=FRONT):
    return _text_pdf(*lines)


def post_front(client, headers, data=None, name="front.pdf"):
    return client.post("/teacher/book-drafts/front-pages", files={"file": (name, data or front_pdf(), "application/pdf")}, headers=headers)


def ref_book(session_factory, **kw):
    fields = dict(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    fields.update(kw)
    with session_factory() as db:
        book = Book(**fields)
        db.add(book)
        db.commit()
        return str(book.id)


def pdf_with_outline(page_texts, outline):
    reader = pypdf.PdfReader(io.BytesIO(_text_pdf(*page_texts)))
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for title, index in outline:
        writer.add_outline_item(title, index)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


# ================= front pages =================================================================

def test_front_pages_return_metadata_and_matching_visible_books_only(client, session_factory):
    ref_id = ref_book(session_factory)
    ref_book(session_factory, subject="History")  # same board/class/publisher but another subject
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    b_private = new_book(client, bh, board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT")

    res = post_front(client, ah)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["metadata"] == {"board": "CBSE", "class_name": "IX", "subject": "Science", "publisher": "NCERT",
                                "edition": "First edition 2025", "is_customized": False, "school": None}
    assert [m["id"] for m in body["matches"]] == [ref_id]  # 'IX' == 'Class 9'; History book and B's private book excluded

    mine = new_book(client, ah, board="CBSE", class_name="9", subject="Science", publisher="NCERT")
    again = post_front(client, ah).json()["matches"]
    assert [m["id"] for m in again] == [ref_id, mine["id"]] and b_private["id"] not in str(again)  # official first


def test_book_is_created_only_when_the_teacher_confirms_the_draft(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    draft = post_front(client, ah).json()
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []  # nothing created yet

    body = {"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "NCERT", "draft_id": draft["draft_id"]}
    assert client.post("/teacher/books", json=body, headers=bh).status_code == 404  # B can't use A's draft
    res = client.post("/teacher/books", json={**body, "edition": "edited by teacher"}, headers=ah)
    assert res.status_code == 201 and res.json()["metadata_source"] == "front_pages"
    with session_factory() as db:
        book = db.get(Book, uuid.UUID(res.json()["id"]))
        assert book.extracted_metadata["class_name"] == "IX"  # what was read, kept next to what was confirmed
        assert book.class_name == "Class 9" and book.front_pages_file
        assert db.scalars(select(UploadDraft)).all() == []
    assert client.post("/teacher/books", json=body, headers=ah).status_code == 404  # draft is single-use


def test_manual_entry_still_works_unless_front_pages_are_required(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    body = {"board": "ICSE", "class_name": "Class 9", "subject": "Math", "publisher": "Selina"}
    assert client.post("/teacher/books", json=body, headers=ah).json()["metadata_source"] == "manual"
    monkeypatch.setattr(settings, "require_front_pages", True)
    assert client.post("/teacher/books", json=body, headers=ah).status_code == 422
    draft = post_front(client, ah).json()
    assert client.post("/teacher/books", json={**body, "draft_id": draft["draft_id"]}, headers=ah).status_code == 201


def test_front_pages_validation_and_failures_are_safe(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    assert post_front(client, ah, _text_pdf(*[f"p{i}" for i in range(settings.front_pages_max_pages + 1)])).status_code == 422
    assert post_front(client, ah, b"not a pdf at all").status_code == 415
    assert post_front(client, ah, b"%PDF-1.4 corrupt").status_code in (201, 422)  # fake OCR tolerates; real files are checked

    class BlankOCR:
        def extract_layout(self, data, ext):
            return {"pages": [{"page_number": 1, "text": "  ", "lines": []}], "page_count": 1}

    class BrokenOCR:
        def extract_layout(self, data, ext):
            raise RuntimeError("azure key abc123 rejected")

    monkeypatch.setattr("app.content_library.upload.get_ocr_provider", lambda: BlankOCR())
    assert post_front(client, ah).status_code == 422
    monkeypatch.setattr("app.content_library.upload.get_ocr_provider", lambda: BrokenOCR())
    res = post_front(client, ah)
    assert res.status_code == 422 and "abc123" not in res.text and "try again" in res.text.lower()

    monkeypatch.undo()

    class GarbageLLM:
        def complete_json(self, system, user):
            return "nope"

    monkeypatch.setattr("app.content_library.upload.get_llm_provider", lambda: GarbageLLM())
    res = post_front(client, ah)
    assert res.status_code == 422 and "by hand" in res.text
    with session_factory() as db:
        assert db.scalars(select(UploadDraft)).all() == []  # failed attempts leave nothing behind


# ================= search ==================================================================================

def test_normalize_class():
    assert [normalize_class(x) for x in ("Class 9", "IX", "9th", "Grade 9", "class ix", "")] == ["9", "9", "9", "9", "9", ""]


def test_library_search(client, session_factory):
    ref_id = ref_book(session_factory)
    ref10 = ref_book(session_factory, class_name="Class 10", subject="Maths")
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    mine = new_book(client, ah, subject="Science", publisher="Oxford", board="ICSE", class_name="Class 9")
    new_book(client, bh, subject="Science", publisher="Hidden Press")

    def ids(**params):
        return {b["id"] for b in client.get("/teacher/books", params=params, headers=ah).json()}

    assert ids(class_name="IX", subject="science") == {ref_id, mine["id"]}
    assert ids(publisher="ncer") == {ref_id, ref10}
    assert ids(q="oxford icse") == {mine["id"]}
    assert ids(q="science", scope="reference") == {ref_id}
    assert ids(q="hidden") == set()  # other teacher's private book
    assert ids(q="%") == set() and ids(subject="_") == set()  # LIKE wildcards are not wildcards here


# ================= whole textbook =============================================================================

TEXTS = [f"page {i} of the textbook about topic {i}" for i in range(1, 7)]


def plan(client, headers, book_id, data, name="book.pdf"):
    return client.post(f"/teacher/books/{book_id}/whole-book/plan", files={"file": (name, data, "application/pdf")}, headers=headers)


def confirm(client, headers, book_id, draft_id, chapters):
    return client.post(f"/teacher/books/{book_id}/whole-book/confirm", json={"draft_id": draft_id, "chapters": chapters}, headers=headers)


def test_whole_book_is_split_by_bookmarks_and_processed_per_chapter(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    existing = new_chapter(client, th, book["id"])  # sequence 1 already used

    res = plan(client, th, book["id"], pdf_with_outline(TEXTS, [("Matter", 0), ("Atoms", 2), ("Energy", 5)]))
    assert res.status_code == 201, res.text
    p = res.json()
    assert p["page_count"] == 6
    assert p["proposed_chapters"] == [
        {"title": "Matter", "start_page": 1, "end_page": 2},
        {"title": "Atoms", "start_page": 3, "end_page": 5},
        {"title": "Energy", "start_page": 6, "end_page": 6},
    ]
    with session_factory() as db:
        assert db.scalars(select(Chapter).where(Chapter.title == "Matter")).all() == []  # not created before confirm

    edited = [{"title": "Matter and Atoms", "start_page": 1, "end_page": 4}, {"title": "Energy", "start_page": 5, "end_page": 6}]
    res = confirm(client, th, book["id"], p["draft_id"], edited)
    assert res.status_code == 202, res.text
    assert [(c["title"], c["sequence_num"]) for c in res.json()] == [("Matter and Atoms", 2), ("Energy", 3)]
    chapters = {c["title"]: c for c in client.get(f"/teacher/books/{book['id']}/chapters", headers=th).json()}
    assert chapters["Matter and Atoms"]["status"] == chapters["Energy"]["status"] == "ready"  # background jobs ran
    assert chapters[existing and "Ch 1"]["status"] == "empty"
    assert page_count(session_factory, chapters["Matter and Atoms"]["id"]) == 4 and page_count(session_factory, chapters["Energy"]["id"]) == 2

    texts = [pg["content_text"] for pg in client.get(
        f"/teacher/books/{book['id']}/chapters/{chapters['Energy']['id']}/pages", headers=th).json()]
    assert texts == [TEXTS[4], TEXTS[5]]  # the right slice of the PDF
    assert confirm(client, th, book["id"], p["draft_id"], edited).status_code == 404  # draft is single-use


def test_whole_book_without_bookmarks_proposes_nothing_and_accepts_manual_ranges(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    assert p["proposed_chapters"] == [] and p["page_count"] == 6
    res = confirm(client, th, book["id"], p["draft_id"], [{"title": "All of it", "start_page": 1, "end_page": 6}])
    assert res.status_code == 202 and res.json()[0]["sequence_num"] == 1


@pytest.mark.parametrize("chapters,message", [
    ([], "at least one"),
    ([{"title": "A", "start_page": 1, "end_page": 3}, {"title": "B", "start_page": 3, "end_page": 5}], "overlaps"),
    ([{"title": "A", "start_page": 4, "end_page": 2}], "before the first"),
    ([{"title": "A", "start_page": 1, "end_page": 9}], "only has 6 pages"),
])
def test_whole_book_range_validation(client, session_factory, chapters, message):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    res = confirm(client, th, book["id"], p["draft_id"], chapters)
    assert res.status_code == 422 and message in res.text
    with session_factory() as db:
        assert db.scalars(select(Chapter)).all() == []  # nothing half-created


def test_whole_book_chapter_count_limit(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "max_whole_book_chapters", 2)
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    three = [{"title": f"C{i}", "start_page": i, "end_page": i} for i in (1, 2, 3)]
    assert confirm(client, th, book["id"], p["draft_id"], three).status_code == 422


def test_whole_book_access_and_file_checks(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    book, other = new_book(client, ah), new_book(client, ah, subject="Other")
    ref = reference_book(session_factory)
    pdf = _text_pdf(*TEXTS)

    assert plan(client, bh, book["id"], pdf).status_code == 404  # not B's book
    assert plan(client, ah, ref, pdf).status_code == 403  # reference is read-only
    assert plan(client, sh, book["id"], pdf).status_code == 403
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 20
    assert plan(client, ah, book["id"], png).status_code == 415  # whole book must be a PDF
    assert plan(client, ah, book["id"], b"%PDF-1.4 this is junk").status_code == 422  # unreadable PDF
    assert plan(client, ah, book["id"], b"").status_code == 400

    p = plan(client, ah, book["id"], pdf).json()
    one = [{"title": "A", "start_page": 1, "end_page": 2}]
    assert confirm(client, bh, book["id"], p["draft_id"], one).status_code == 404  # B can't confirm A's draft
    assert confirm(client, ah, other["id"], p["draft_id"], one).status_code == 404  # draft belongs to a different book
    assert confirm(client, ah, book["id"], str(uuid.uuid4()), one).status_code == 404


# ================= bulk link ====================================================================================

def make_room(client, headers, room_type="single_class"):
    return client.post("/teacher/rooms", json={"name": "Class 9A", "room_type": room_type}, headers=headers).json()


def join(client, room, headers):
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=headers).status_code == 200


def test_bulk_link_a_book_to_every_student_in_a_single_class_room(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    students = [make_user(session_factory, Role.student, f"student{i}")[1] for i in (1, 2, 3)]
    room = make_room(client, th)
    for h in students[:2]:
        join(client, room, h)
    ref_id, mine = reference_book(session_factory), new_book(client, th)

    url = lambda book: f"/teacher/rooms/{room['id']}/books/{book}/link"
    assert client.post(url(ref_id), headers=th).json() == {"linked": 2, "already_linked": 0, "total_students": 2}
    assert client.post(url(ref_id), headers=th).json() == {"linked": 0, "already_linked": 2, "total_students": 2}
    assert client.post(url(mine["id"]), headers=th).json()["linked"] == 2
    assert {b["id"] for b in client.get("/student/books", headers=students[0]).json()} == {ref_id, mine["id"]}
    assert client.get("/student/books", headers=students[2]).json() == []  # not in the room: untouched

    join(client, room, students[2])  # joins later: not auto-linked (links stay per-student)
    assert client.get("/student/books", headers=students[2]).json() == []
    assert client.post(url(ref_id), headers=th).json() == {"linked": 1, "already_linked": 2, "total_students": 3}


def test_bulk_link_rules(client, session_factory):
    _, ah = make_user(session_factory, Role.teacher, "teachera")
    _, bh = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    single, mixed = make_room(client, ah), make_room(client, ah, "mixed_class")
    a_book, b_book = new_book(client, ah), new_book(client, bh)

    assert client.post(f"/teacher/rooms/{mixed['id']}/books/{a_book['id']}/link", headers=ah).status_code == 409
    assert client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=bh).status_code == 404  # not B's room
    assert client.post(f"/teacher/rooms/{single['id']}/books/{b_book['id']}/link", headers=ah).status_code == 404  # B's private book
    assert client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=sh).status_code == 403
    empty = client.post(f"/teacher/rooms/{single['id']}/books/{a_book['id']}/link", headers=ah)
    assert empty.json() == {"linked": 0, "already_linked": 0, "total_students": 0}


# ================= chapter requests ===============================================================================

def setup_requests(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, sh = make_user(session_factory, Role.student, "student1")
    book = new_book(client, th)
    room = make_room(client, th)
    join(client, room, sh)
    client.post(f"/student/books/{book['id']}/link", headers=sh)
    return th, sh, book


def ask(client, headers, book_id, hint, chapter_id=None):
    body = {"chapter_hint": hint, **({"chapter_id": chapter_id} if chapter_id else {})}
    return client.post(f"/student/books/{book_id}/chapter-requests", json=body, headers=headers)


def test_student_requests_a_chapter_and_duplicates_are_merged(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    first = ask(client, sh, book["id"], "Chapter 9:  Force and Laws of Motion")
    assert first.status_code == 201 and first.json()["status"] == "open"
    again = ask(client, sh, book["id"], "chapter 9 force and laws of motion!")
    assert again.status_code == 200 and again.json()["id"] == first.json()["id"]
    assert ask(client, sh, book["id"], "Gravitation").status_code == 201
    assert len(client.get("/student/chapter-requests", headers=sh).json()) == 2


def test_request_rules(client, session_factory, monkeypatch):
    th, sh, book = setup_requests(client, session_factory)
    _, other_student = make_user(session_factory, Role.student, "student2")
    ref = reference_book(session_factory)
    client.post(f"/student/books/{ref}/link", headers=sh)
    ready_ch = new_chapter(client, th, book["id"])
    upload(client, th, book["id"], ready_ch, _text_pdf("a page"))

    assert ask(client, other_student, book["id"], "Gravitation").status_code == 404  # hasn't linked the book
    assert ask(client, sh, ref, "Gravitation").status_code == 409  # official books have no teacher to ask
    assert ask(client, sh, book["id"], "!!").status_code == 422
    assert ask(client, sh, book["id"], "x" * 201).status_code == 422
    assert ask(client, sh, book["id"], "Chapter 1", chapter_id=ready_ch).status_code == 409  # already available
    assert ask(client, sh, book["id"], "Chapter 1", chapter_id=str(uuid.uuid4())).status_code == 404

    monkeypatch.setattr(settings, "open_requests_per_student", 2)
    assert ask(client, sh, book["id"], "Gravitation").status_code == 201
    assert ask(client, sh, book["id"], "Sound").status_code == 201
    assert ask(client, sh, book["id"], "Light").status_code == 429
    assert ask(client, sh, book["id"], "Sound").status_code == 200  # an existing one is still just returned


def test_teacher_sees_only_their_students_requests_and_can_close_them(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    _, other_teacher = make_user(session_factory, Role.teacher, "teacherb")
    r1 = ask(client, sh, book["id"], "Gravitation").json()
    r2 = ask(client, sh, book["id"], "Sound").json()

    listed = client.get("/teacher/chapter-requests", headers=th).json()
    assert {r["chapter_hint"] for r in listed} == {"Gravitation", "Sound"}
    assert listed[0]["student_name"] == "student1" and listed[0]["book"]["id"] == book["id"]
    assert client.get("/teacher/chapter-requests", headers=other_teacher).json() == []
    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=other_teacher).status_code == 404

    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=th).json()["status"] == "dismissed"
    assert client.post(f"/teacher/chapter-requests/{r1['id']}/dismiss", headers=th).status_code == 409
    empty_ch = new_chapter(client, th, book["id"])
    assert client.post(f"/teacher/chapter-requests/{r2['id']}/fulfill", json={"chapter_id": empty_ch}, headers=th).status_code == 409  # not ready
    assert client.post(f"/teacher/chapter-requests/{r2['id']}/fulfill", json={}, headers=th).json()["status"] == "fulfilled"
    assert client.get("/teacher/chapter-requests", headers=th).json() == []
    assert len(client.get("/teacher/chapter-requests?status=all", headers=th).json()) == 2
    statuses = {r["chapter_hint"]: r["status"] for r in client.get("/student/chapter-requests", headers=sh).json()}
    assert statuses == {"Gravitation": "dismissed", "Sound": "fulfilled"}


def test_student_can_cancel_only_their_own_open_request(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    _, other_student = make_user(session_factory, Role.student, "student2")
    r = ask(client, sh, book["id"], "Gravitation").json()
    assert client.delete(f"/student/chapter-requests/{r['id']}", headers=other_student).status_code == 404
    assert client.delete(f"/student/chapter-requests/{r['id']}", headers=sh).status_code == 204
    assert client.get("/teacher/chapter-requests", headers=th).json() == []
    assert client.get("/student/chapter-requests", headers=sh).json()[0]["status"] == "cancelled"
    assert client.get("/student/chapter-requests", headers=other_student).json() == []


def test_requests_close_themselves_when_the_chapter_becomes_ready(client, session_factory):
    th, sh, book = setup_requests(client, session_factory)
    other_book = new_book(client, th, subject="Other")
    chapter = client.post(f"/teacher/books/{book['id']}/chapters", json={"title": "Chapter 9: Force and Laws of Motion", "sequence_num": 9}, headers=th).json()["id"]
    pending = new_chapter(client, th, book["id"])

    by_title = ask(client, sh, book["id"], "force and laws of motion").json()
    by_id = ask(client, sh, book["id"], "the second one please", chapter_id=pending).json()
    unrelated = ask(client, sh, book["id"], "Gravitation").json()
    client.post(f"/student/books/{other_book['id']}/link", headers=sh)
    elsewhere = ask(client, sh, other_book["id"], "force and laws of motion").json()

    upload(client, th, book["id"], chapter, _text_pdf("some page text"))
    upload(client, th, book["id"], pending, _text_pdf("another page"))
    status_of = {r["id"]: r["status"] for r in client.get("/student/chapter-requests", headers=sh).json()}
    assert status_of[by_title["id"]] == "fulfilled" and status_of[by_id["id"]] == "fulfilled"
    assert status_of[unrelated["id"]] == "open" and status_of[elsewhere["id"]] == "open"  # other chapter / other book
    with session_factory() as db:
        assert db.get(ChapterRequest, uuid.UUID(by_id["id"])).resolved_at is not None
