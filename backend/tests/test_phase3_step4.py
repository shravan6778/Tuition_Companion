"""Phase 3 step 4: photographed doubts (fake OCR; the real OCR is checked with `try_doubt_photo` on real photos)."""
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.doubts import photo
from app.models import Doubt, PageKind, Role
from app.pipeline.indexing import index_chapter
from tests.test_book_access import make_user
from tests.test_phase3_settle import TISSUE, add_chapter
from tests.test_phase3_step2 import TISSUE_Q, assign, world  # noqa: F401  (world is a fixture)
from tests.test_phase3_step3 import GOOD, Scripted, use_model
from app.models import Book

JPG = b"\xff\xd8\xff\xe0" + b"fake jpeg bytes" * 10
PNG = b"\x89PNG\r\n\x1a\n" + b"fake png bytes" * 10
WHOLE_PAGE = (TISSUE + " ") * 5  # well over 60 words


class StubOCR:
    calls = 0

    def __init__(self, text):
        self.text = text

    def extract(self, data, ext):
        StubOCR.calls += 1
        if isinstance(self.text, Exception):
            raise self.text
        from app.ocr.base import OCRResult
        return OCRResult(text=self.text, page_count=1)


def reads(monkeypatch, text):
    StubOCR.calls = 0
    monkeypatch.setattr(photo, "get_ocr_provider", lambda: StubOCR(text))


def snap(client, w, data=JPG, name="doubt.jpg", assignment=None, headers=None):
    return client.post("/student/doubts/photo", files={"file": (name, data, "image/jpeg")},
                       data={"assignment_id": assignment["id"]} if assignment else {}, headers=headers or w["sh"])


def doubt_rows(session_factory):
    with session_factory() as db:
        return db.scalars(select(Doubt)).all()


# ---- a clear photo of a doubt is just a typed doubt ---------------------------------------------------

def test_a_photographed_doubt_is_searched_and_answered_like_a_typed_one(client, session_factory, world, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "tutor_verify_below", 0.0)
    use_model(monkeypatch, Scripted(GOOD))
    reads(monkeypatch, "  " + TISSUE_Q + "\n")
    body = snap(client, world, assignment=assign(client, world)).json()
    assert body["kind"] == "doubt" and body["words"] == len(TISSUE_Q.split()) and body["text_read"] == TISSUE_Q
    assert body["doubt"]["status"] == "grounded" and body["doubt"]["answer_status"] == "answered"
    rows = doubt_rows(session_factory)
    assert len(rows) == 1 and rows[0].text == TISSUE_Q  # only the text read is kept
    assert not list((tmp_path / "storage").rglob("*.jpg"))  # the image itself is never stored


def test_a_png_is_accepted_too_and_a_standalone_photo_needs_no_assignment(client, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    body = snap(client, world, data=PNG, name="x.png").json()
    assert body["kind"] == "doubt" and body["doubt"]["assignment_id"] is None and body["doubt"]["status"] == "grounded"


# ---- unreadable photos never retrieve noise -------------------------------------------------------------

def test_a_photo_with_too_few_words_asks_for_a_retake_and_saves_nothing(client, session_factory, world, monkeypatch):
    reads(monkeypatch, "smudge ink")
    body = snap(client, world).json()
    assert body["kind"] == "too_short" and "retake" in body["message"].lower() and body["doubt"] is None
    assert doubt_rows(session_factory) == []


def test_a_down_ocr_service_reads_as_unavailable_not_a_500(client, session_factory, world, monkeypatch):
    reads(monkeypatch, RuntimeError("azure down"))
    res = snap(client, world)
    assert res.status_code == 200 and res.json()["kind"] == "unavailable" and doubt_rows(session_factory) == []


def test_the_development_placeholder_is_never_treated_as_a_doubt(client, session_factory, world, monkeypatch):
    # OCR_PROVIDER=fake returns a placeholder for images: that must not be searched as if a student had asked it
    monkeypatch.setattr(photo, "get_ocr_provider", lambda: __import__("app.ocr.fake_provider", fromlist=["x"]).FakeOCRProvider())
    assert snap(client, world).json()["kind"] == "unavailable" and doubt_rows(session_factory) == []


# ---- a whole page: pick the concept ------------------------------------------------------------------

def test_a_whole_page_lists_its_concepts_and_saves_no_doubt_until_one_is_picked(client, session_factory, world, monkeypatch):
    monkeypatch.setattr(settings, "tutor_verify_below", 0.0)
    llm = use_model(monkeypatch, Scripted(GOOD))
    reads(monkeypatch, WHOLE_PAGE)
    body = snap(client, world, assignment=assign(client, world)).json()
    assert body["kind"] == "page" and body["status"] == "grounded" and body["doubt"] is None
    assert body["page"]["page_number"] == 2 and body["page"]["chapter_title"] == "Cells"
    names = {c["name"]: c["concept_id"] for c in body["page"]["concepts"]}
    assert "Tissue" in names
    assert doubt_rows(session_factory) == [] and llm.prompts == []  # a page is not a question: nothing saved, the Tutor not asked
    picked = client.post("/student/doubts", json={"concept_id": names["Tissue"], "assignment_id": None}, headers=world["sh"])
    assert picked.status_code == 200, picked.text
    out = picked.json()
    assert out["status"] == "grounded" and out["answer_status"] == "answered" and len(llm.prompts) == 1
    assert "Tissue" in llm.prompts[0] and len(doubt_rows(session_factory)) == 1


def test_a_page_that_is_not_in_the_students_books_is_not_in_book(client, session_factory, world, monkeypatch):
    reads(monkeypatch, ("photosynthesis converts sunlight water and carbon dioxide into glucose and oxygen in the green leaves " * 5))
    body = snap(client, world, assignment=assign(client, world)).json()
    assert body["kind"] == "page" and body["status"] == "not_in_book" and body["page"] is None
    assert body["request_chapter"]["path"].endswith("/chapter-requests") and doubt_rows(session_factory) == []


def test_a_narrow_assignment_only_offers_its_own_concepts(client, world, monkeypatch):
    reads(monkeypatch, WHOLE_PAGE)
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Cell"]])
    body = snap(client, world, assignment=a).json()
    assert body["kind"] == "page" and body["status"] == "outside_assignment" and body["page"] is None  # the Tissue page is not part of a Cell-only assignment


# ---- the file, the limits and who may ask ----------------------------------------------------------------

@pytest.mark.parametrize("data,code", [(b"", 400), (b"%PDF-1.4 not a photo", 415), (b"just some text", 415)])
def test_the_file_is_checked_by_its_content_before_any_ocr_is_paid_for(client, world, monkeypatch, data, code):
    reads(monkeypatch, TISSUE_Q)
    assert snap(client, world, data=data, name="whatever.jpg").status_code == code
    assert StubOCR.calls == 0


def test_an_oversized_photo_is_refused_before_ocr(client, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    monkeypatch.setattr(settings, "max_doubt_photo_mb", 0)
    assert snap(client, world).status_code == 413 and StubOCR.calls == 0


def test_each_student_has_a_photo_limit_and_it_is_checked_before_ocr(client, session_factory, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    monkeypatch.setattr(settings, "rate_doubt_photos_per_hour", 2)
    assert [snap(client, world).status_code for _ in range(3)] == [200, 200, 429]
    assert StubOCR.calls == 2
    _, other = make_user(session_factory, Role.student, "studentb")
    assert snap(client, world, headers=other).status_code == 200  # one student's limit is not another's


def test_someone_elses_assignment_is_404_and_costs_no_ocr(client, session_factory, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    a = assign(client, world)
    _, other = make_user(session_factory, Role.student, "studentb")
    assert snap(client, world, assignment=a, headers=other).status_code == 404
    assert snap(client, world, assignment={"id": "00000000-0000-0000-0000-000000000000"}).status_code == 404
    assert StubOCR.calls == 0 and doubt_rows(session_factory) == []


def test_only_students_can_send_photos(client, world, monkeypatch):
    reads(monkeypatch, TISSUE_Q)
    assert snap(client, world, headers=world["th"]).status_code in (401, 403) and StubOCR.calls == 0


# ---- picking a concept never reaches another book ------------------------------------------------------------

def test_a_picked_concept_must_be_in_the_students_own_books(client, session_factory, world):
    owner, _ = make_user(session_factory, Role.teacher, "teacherc")
    with session_factory() as db:
        secret = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="X", owner_teacher_id=owner.id)
        db.add(secret)
        db.flush()
        ch = add_chapter(db, secret, "Secret", 1, [(1, "photosynthesis converts sunlight into glucose", PageKind.CONTENT)],
                         [(1, "Photosynthesis", "Plants make glucose from sunlight")])
        db.commit()
        from app.models import Concept
        concept_id = str(db.scalars(select(Concept).where(Concept.name == "Photosynthesis")).one().id)
    res = client.post("/student/doubts", json={"concept_id": concept_id}, headers=world["sh"])
    assert res.status_code == 404 and doubt_rows(session_factory) == []


def test_a_doubt_needs_text_or_a_concept(client, world):
    assert client.post("/student/doubts", json={}, headers=world["sh"]).status_code == 422
    assert client.post("/student/doubts", json={"text": "   "}, headers=world["sh"]).status_code == 422
