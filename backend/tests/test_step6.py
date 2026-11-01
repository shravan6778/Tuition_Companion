"""Front-pages-first upload, library search, whole-textbook upload: all done by the student who owns the book.

Teachers no longer upload books, so the bulk "link this book to the room" route and the chapter-request flow are gone
(a student who lacks a chapter uploads it themselves)."""
import io
import uuid

import pypdf
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models import Book, Chapter, Role, UploadDraft
from app.content_library.search import normalize_class
from tests.test_book_access import make_user, new_book, new_chapter, reference_book
from tests.test_chapter_jobs import chapter_status, page_count, upload
from tests.test_pipeline import _text_pdf

FRONT = ["Board: CBSE", "Class: IX", "Subject: Science", "Publisher: NCERT", "Edition: First edition 2025"]


def front_pdf(lines=FRONT):
    return _text_pdf(*lines)


def post_front(client, headers, data=None, name="front.pdf"):
    return client.post("/student/book-drafts/front-pages", files={"file": (name, data or front_pdf(), "application/pdf")}, headers=headers)


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
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
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


def test_book_is_created_only_when_the_student_confirms_the_draft(client, session_factory):
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
    draft = post_front(client, ah).json()
    with session_factory() as db:
        assert db.scalars(select(Book)).all() == []  # nothing created yet

    body = {"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "NCERT", "draft_id": draft["draft_id"]}
    assert client.post("/student/books", json=body, headers=bh).status_code == 404  # B can't use A's draft
    res = client.post("/student/books", json={**body, "edition": "edited by student"}, headers=ah)
    assert res.status_code == 201 and res.json()["metadata_source"] == "front_pages"
    with session_factory() as db:
        book = db.get(Book, uuid.UUID(res.json()["id"]))
        assert book.extracted_metadata["class_name"] == "IX"  # what was read, kept next to what was confirmed
        assert book.class_name == "Class 9" and book.front_pages_file
        assert db.scalars(select(UploadDraft)).all() == []
    assert client.post("/student/books", json=body, headers=ah).status_code == 404  # draft is single-use


def test_manual_entry_still_works_unless_front_pages_are_required(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.student, "studenta")
    body = {"board": "ICSE", "class_name": "Class 9", "subject": "Math", "publisher": "Selina"}
    assert client.post("/student/books", json=body, headers=ah).json()["metadata_source"] == "manual"
    monkeypatch.setattr(settings, "require_front_pages", True)
    assert client.post("/student/books", json=body, headers=ah).status_code == 422
    draft = post_front(client, ah).json()
    assert client.post("/student/books", json={**body, "draft_id": draft["draft_id"]}, headers=ah).status_code == 201


def test_front_pages_validation_and_failures_are_safe(client, session_factory, monkeypatch):
    _, ah = make_user(session_factory, Role.student, "studenta")
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


def test_library_search_finds_only_official_books(client, session_factory):
    """The teacher's book picker searches the official library only; a student's private books are nobody else's to find."""
    ref_id = ref_book(session_factory)
    ref10 = ref_book(session_factory, class_name="Class 10", subject="Maths")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, ah = make_user(session_factory, Role.student, "studenta")
    new_book(client, ah, subject="Science", publisher="Oxford", board="ICSE", class_name="Class 9")

    def ids(**params):
        return {b["id"] for b in client.get("/teacher/books", params=params, headers=th).json()}

    assert ids(class_name="IX", subject="science") == {ref_id}  # 'IX' == 'Class 9'; the student's own Science book is not listed
    assert ids(publisher="ncer") == {ref_id, ref10}
    assert ids(q="oxford icse") == set()  # a student's private book is not searchable by a teacher
    assert ids(q="science", scope="reference") == {ref_id}
    assert ids(q="%") == set() and ids(subject="_") == set()  # LIKE wildcards are not wildcards here


# ================= whole textbook =============================================================================

TEXTS = [f"page {i} of the textbook about topic {i}" for i in range(1, 7)]


def plan(client, headers, book_id, data, name="book.pdf"):
    return client.post(f"/student/books/{book_id}/whole-book/plan", files={"file": (name, data, "application/pdf")}, headers=headers)


def confirm(client, headers, book_id, draft_id, chapters):
    return client.post(f"/student/books/{book_id}/whole-book/confirm", json={"draft_id": draft_id, "chapters": chapters}, headers=headers)


def test_whole_book_is_split_by_bookmarks_and_processed_per_chapter(client, session_factory):
    _, th = make_user(session_factory, Role.student, "studenta")
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
    chapters = {c["title"]: c for c in client.get(f"/student/books/{book['id']}/chapters", headers=th).json()}
    assert chapters["Matter and Atoms"]["status"] == chapters["Energy"]["status"] == "ready"  # background jobs ran
    assert chapters[existing and "Ch 1"]["status"] == "empty"
    assert page_count(session_factory, chapters["Matter and Atoms"]["id"]) == 4 and page_count(session_factory, chapters["Energy"]["id"]) == 2

    texts = [pg["content_text"] for pg in client.get(
        f"/student/books/{book['id']}/chapters/{chapters['Energy']['id']}/pages", headers=th).json()]
    assert texts == [TEXTS[4], TEXTS[5]]  # the right slice of the PDF
    assert confirm(client, th, book["id"], p["draft_id"], edited).status_code == 404  # draft is single-use


def test_whole_book_without_bookmarks_proposes_nothing_and_accepts_manual_ranges(client, session_factory):
    _, th = make_user(session_factory, Role.student, "studenta")
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
    _, th = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    res = confirm(client, th, book["id"], p["draft_id"], chapters)
    assert res.status_code == 422 and message in res.text
    with session_factory() as db:
        assert db.scalars(select(Chapter)).all() == []  # nothing half-created


def test_whole_book_chapter_count_limit(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "max_whole_book_chapters", 2)
    _, th = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, th)
    p = plan(client, th, book["id"], _text_pdf(*TEXTS)).json()
    three = [{"title": f"C{i}", "start_page": i, "end_page": i} for i in (1, 2, 3)]
    assert confirm(client, th, book["id"], p["draft_id"], three).status_code == 422


def test_whole_book_access_and_file_checks(client, session_factory):
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
    _, th = make_user(session_factory, Role.teacher, "teachera")
    book, other = new_book(client, ah), new_book(client, ah, subject="Other")
    ref = reference_book(session_factory)
    pdf = _text_pdf(*TEXTS)

    assert plan(client, bh, book["id"], pdf).status_code == 404  # not B's book
    assert plan(client, ah, ref, pdf).status_code == 403  # reference is read-only
    assert plan(client, th, book["id"], pdf).status_code == 403  # teachers cannot upload books at all
    png = b"\x89PNG\r\n\x1a\n" + b"0" * 20
    assert plan(client, ah, book["id"], png).status_code == 415  # whole book must be a PDF
    assert plan(client, ah, book["id"], b"%PDF-1.4 this is junk").status_code == 422  # unreadable PDF
    assert plan(client, ah, book["id"], b"").status_code == 400

    p = plan(client, ah, book["id"], pdf).json()
    one = [{"title": "A", "start_page": 1, "end_page": 2}]
    assert confirm(client, bh, book["id"], p["draft_id"], one).status_code == 404  # B can't confirm A's draft
    assert confirm(client, ah, other["id"], p["draft_id"], one).status_code == 404  # draft belongs to a different book
    assert confirm(client, ah, book["id"], str(uuid.uuid4()), one).status_code == 404
