import uuid

import pytest
from sqlalchemy import select

from app.core.errors import ProcessingError
from app.models import Book, Chapter, Concept, Page, Role, User
from app.pipeline.orchestrator import PipelineOrchestrator


def _teacher(session_factory):
    with session_factory() as db:
        u = User(supertokens_user_id="st-t1", name="T", username="teach1", phone="1", role=Role.teacher)
        db.add(u)
        db.commit()
        db.refresh(u)
        db.expunge(u)
    return u, {"Authorization": "Bearer st-t1"}


def _book_and_chapter(db):
    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="Test")
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="Matter", sequence_num=1)
    db.add(ch)
    db.commit()
    return book.id, ch.id


def _text_pdf(*page_texts: str) -> bytes:
    """Smallest valid-enough text PDF (pypdf rebuilds the xref table)."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>"]
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(len(page_texts)))
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_texts)} >>")
    for i, t in enumerate(page_texts):
        content_id = 4 + i * 2
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents {content_id} 0 R "
            f"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>"
        )
        stream = f"BT /F1 12 Tf 10 100 Td ({t}) Tj ET"
        objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    out = "%PDF-1.4\n" + "".join(f"{n + 1} 0 obj\n{o}\nendobj\n" for n, o in enumerate(objs))
    out += f"trailer\n<< /Root 1 0 R /Size {len(objs) + 1} >>\nstartxref\n0\n%%EOF"
    return out.encode()


class CountingLLM:
    model_name = "counting"

    def __init__(self, reply=None):
        self.calls = 0
        self.reply = reply

    def complete_json(self, system, user):
        self.calls += 1
        return self.reply or '{"concepts":[{"name":"Matter","description":"d","learning_objectives":[],"prerequisites":[]}]}'


def test_app_boots(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_teacher_upload_end_to_end_with_fake_providers(client, session_factory):
    _, th = _teacher(session_factory)
    with session_factory() as db:
        book_id, ch_id = _book_and_chapter(db)
    res = client.post(
        f"/teacher/books/{book_id}/chapters/{ch_id}/pages/upload",
        files={"file": ("p.pdf", _text_pdf("Matter is anything with mass", "Particles of matter attract"), "application/pdf")},
        headers=th,
    )
    assert res.status_code == 200, res.text
    pages = res.json()
    assert [p["page_number"] for p in pages] == [1, 2]
    assert all(p["concepts"] for p in pages)


def test_identical_page_reuses_concepts_without_llm_call(session_factory):
    pdf = _text_pdf("Matter is anything that occupies space and has mass in our surroundings")
    with session_factory() as db:
        _, ch_id = _book_and_chapter(db)
        llm = CountingLLM()
        orch = PipelineOrchestrator(db, llm_provider=llm)
        orch.process_upload(pdf, "pdf", {"chapter_id": ch_id}, None, True)
        assert llm.calls == 1
        pages = orch.process_upload(pdf, "pdf", {"chapter_id": ch_id}, None, True)
        assert llm.calls == 1  # second upload matched the first: zero LLM cost
        assert pages[0].concepts[0].name == "Matter"


def test_invalid_llm_json_fails_loudly_and_rolls_back(session_factory):
    pdf = _text_pdf("page one text here", "page two text here")
    with session_factory() as db:
        _, ch_id = _book_and_chapter(db)
        llm = CountingLLM(reply="not json at all")
        with pytest.raises(ProcessingError):
            PipelineOrchestrator(db, llm_provider=llm).process_upload(pdf, "pdf", {"chapter_id": ch_id}, None, True)
        assert llm.calls == 3  # first try + 2 correction retries
        assert db.scalars(select(Page)).all() == []  # no half-processed chapter
