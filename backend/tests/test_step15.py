"""Phase 2 exit check, Layer 4 probe and chapter removal (db/phase2_check.py, pipeline/embedprobe.py, db/drop_chapter.py)."""
import json
import uuid

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db import drop_chapter, phase2_check as pc
from app.embeddings.vectors import to_bytes
from app.models import Book, Chapter, ChapterStatus, ContentEmbedding, CrossChapterEdge, Concept, MatchFeedback, Page, User
from app.pipeline.embedprobe import kept_phrases, probe

MODEL = "test-embedding"
TEXT = "the cell is the basic unit of life and every living thing is made of cells " * 3
OFFICIAL = ["Exploration and Entering", "The Building Block of Life", "Matter in Our Surroundings"]
GOOD = {"model": "gpt-x", "concepts": 12, "edges": 9, "unresolved_prerequisites": [], "llm_linking": "done", "review_pages": []}


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embed_match_similarity", 0.85)
    monkeypatch.setattr(settings, "graph_store_provider", "none")


def official_book(db, titles=OFFICIAL, report=None, status=ChapterStatus.READY, cross="done"):
    book = Book(board="CBSE", class_name="9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()
    for i, t in enumerate(titles, 1):
        rep = dict(GOOD if report is None else report)
        if i > 1 and cross:
            rep["cross_chapter"] = {"status": cross}
        ch = Chapter(book_id=book.id, title=t, sequence_num=i, status=status, graph_report=rep, embedding_status="done", graph_sync_status="done")
        db.add(ch)
        db.flush()
        db.add(Page(chapter_id=ch.id, page_number=1, content_text=TEXT))
    db.flush()
    return book


def with_vectors(db, book, vectors_by_chapter):
    chapters = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)))
    for ch, vectors in zip(chapters, vectors_by_chapter):
        for n, vec in enumerate(vectors, 1):
            page = db.scalar(select(Page).where(Page.chapter_id == ch.id, Page.page_number == n))
            if page is None:
                page = Page(chapter_id=ch.id, page_number=n, content_text=TEXT)
                db.add(page)
                db.flush()
            db.add(ContentEmbedding(chapter_id=ch.id, page_id=page.id, model=MODEL, dim=3, text_sha256=str(uuid.uuid4()), vector=to_bytes(vec)))
    db.flush()


class Reworder:
    def complete_json(self, system, user):
        return json.dumps({"text": "a different wording of the page " + user[-20:]})


class Embedder:
    model_name, dim = MODEL, 3

    def __init__(self, vectors):
        self.vectors = vectors

    def embed(self, texts):
        return self.vectors[: len(texts)]


CH1 = [[1, 0, 0], [0.95, 0.05, 0], [0.9, 0.1, 0], [0.97, 0.02, 0]]
CH2 = [[0, 1, 0], [0.05, 0.95, 0], [0.1, 0.9, 0], [0.02, 0.97, 0]]


def test_probe_passes_when_reworded_pages_stay_close_and_different_pages_do_not(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[1, 0.02, 0]] * 4 + [[0.02, 1, 0]] * 4), pages=8)
        assert r["status"] == "done" and r["pages"] == 8 and r["pass"] and r["separable"]
        assert r["same_min"] > 0.99 and r["other_max"] < 0.3 and r["recall"] == 1.0 and r["false_rate"] == 0


def test_probe_fails_with_a_recommendation_when_the_threshold_is_too_high(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "embed_match_similarity", 0.995)
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[1, 0.3, 0]] * 4 + [[0.3, 1, 0]] * 4), pages=8)
        assert not r["pass"] and r["separable"] and r["recall"] < 0.9 and 0.2 < r["recommended"] < 0.99


def test_probe_reports_when_embeddings_cannot_tell_the_pages_apart(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2])
        with_vectors(db, book, [CH1, CH2])
        r = probe(db, Reworder(), Embedder([[0, 0, 1]] * 8), pages=8)  # rewordings land somewhere unrelated
        assert not r["pass"] and not r["separable"] and r["recommended"] is None


def test_probe_needs_pages_and_working_rewording(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:1])
        with_vectors(db, book, [[[1, 0, 0]]])
        assert probe(db, Reworder(), Embedder([]), 8)["status"] == "not_enough_pages"
        with_vectors(db, official_book(db, OFFICIAL[:2]), [CH1, CH2])

        class Broken:
            def complete_json(self, s, u):
                return "not json"
        assert probe(db, Broken(), Embedder([]), 8)["status"] == "rewording_failed"


def test_kept_phrases_measures_how_much_of_the_original_survives():
    a = "one two three four five six seven eight"
    assert kept_phrases(a, a) == 1.0 and kept_phrases(a, "completely different words in another order entirely") == 0.0


def test_official_books_check_passes_a_healthy_book_and_flags_a_test_leftover(session_factory):
    with session_factory() as db:
        official_book(db)
        res = pc.check_official_books(db)
        assert not [r for r in res if r[0] == "FAIL"] and res[0][0] == "PASS"
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        book = official_book(db, OFFICIAL[:2])
        leftover = Chapter(book_id=book.id, title="Matter in Our Surroundings", sequence_num=3, status=ChapterStatus.READY,
                           graph_report={**GOOD, "concepts": 2}, embedding_status="done", graph_sync_status="done")
        db.add(leftover)
        db.flush()
        fails = [m for s, t, m in pc.check_official_books(db) if s == "FAIL"]
        assert any("only 2 concepts" in m and "drop_chapter" in m for m in fails)


def test_official_books_check_fails_on_too_few_chapters_pending_embeddings_and_fake_models(session_factory):
    with session_factory() as db:
        book = official_book(db, OFFICIAL[:2], report={**GOOD, "model": "fake"})
        db.query(Chapter).filter(Chapter.book_id == book.id, Chapter.sequence_num == 2).update({"embedding_status": "failed", "index_error": "boom"})
        fails = " | ".join(m for s, t, m in pc.check_official_books(db) if s == "FAIL")
        assert "need at least 3" in fails and "fake LLM" in fails and "embeddings failed (boom)" in fails


def test_cross_chapter_check_requires_the_step_and_lists_links_to_judge(session_factory):
    with session_factory() as db:
        official_book(db, cross=None)
        assert pc.check_cross_chapter(db)[0][0] == "FAIL"
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        book = official_book(db)
        assert [r[0] for r in pc.check_cross_chapter(db)] == ["PASS", "REVIEW"]  # done, zero links: someone must judge
        ch1, ch2 = [db.scalar(select(Chapter).where(Chapter.book_id == book.id, Chapter.sequence_num == n)) for n in (1, 2)]
        p1, p2 = [db.scalar(select(Page).where(Page.chapter_id == c.id)) for c in (ch1, ch2)]
        a, b = Concept(page_id=p1.id, name="Scientific units"), Concept(page_id=p2.id, name="Estimating cell size")
        db.add_all([a, b])
        db.flush()
        db.add(CrossChapterEdge(chapter_id=ch2.id, concept_id=b.id, prerequisite_id=a.id, similarity=0.61))
        db.flush()
        text = " ".join(m for s, t, m in pc.check_cross_chapter(db))
        assert "'Estimating cell size'" in text and "'Scientific units'" in text and "0.61" in text


def test_structure_check_uses_the_real_titles_and_leaves_nothing_behind(session_factory):
    with session_factory() as db:
        official_book(db)
        db.commit()
        before = (db.scalar(select(func.count()).select_from(Book)), db.scalar(select(func.count()).select_from(User)))
        res = pc.check_structure(db)
        assert [r[0] for r in res if r[1] in ("S1", "S2")] == ["PASS"] * 3
        db.rollback()
        assert (db.scalar(select(func.count()).select_from(Book)), db.scalar(select(func.count()).select_from(User))) == before
    with session_factory() as db:
        db.query(Chapter).delete()
        db.query(Book).delete()
        official_book(db, OFFICIAL[:1])
        assert pc.check_structure(db)[0][0] == "FAIL"


def test_feedback_round_trip_passes_and_leaves_nothing_behind(session_factory):
    with session_factory() as db:
        official_book(db)
        res = pc.check_feedback(db)
        assert [r[0] for r in res if r[1] == "F1"] == ["PASS"] * 3, res
        db.rollback()
        assert db.scalar(select(func.count()).select_from(MatchFeedback)) == 0 and db.scalar(select(func.count()).select_from(User)) == 0


def test_embedding_check_refuses_fake_providers_and_can_be_skipped(session_factory, monkeypatch):
    with session_factory() as db:
        assert pc.check_embedding(db, skip_probe=True)[0][0] == "REVIEW"
        monkeypatch.setattr(settings, "llm_provider", "fake")
        assert pc.check_embedding(db, skip_probe=False)[0][0] == "FAIL"


def test_front_pages_check(session_factory):
    with session_factory() as db:
        assert pc.check_front_pages(db)[0][0] == "FAIL"  # nothing ever confirmed from front pages
        db.add(Book(board="CBSE", class_name="9", subject="Science", publisher="NCERT", is_reference=True, extracted_metadata={"board": "CBSE", "class_name": "Class 9", "subject": "Science", "publisher": "N C E R T"}))
        db.flush()
        res = pc.check_front_pages(db)
        reviews = [m for s, t, m in res if s == "REVIEW"]
        assert res[0][0] == "PASS" and len(reviews) == 1 and "'publisher': read 'N C E R T', teacher confirmed 'NCERT'" in reviews[0]
        assert not any("class_name" in m for s, t, m in res)  # 'Class 9' and '9' are the same class


def test_run_prints_a_verdict_and_never_keeps_anything(session_factory):
    with session_factory() as db:
        official_book(db)
        db.commit()
    lines, fails = pc.run(session_factory, skip_probe=True)
    text = "\n".join(lines)
    assert "RESULT:" in text and fails >= 1 and "Phase 2 is NOT finished" in text  # at least: no migration table, no front-page book
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == 0 and db.scalar(select(func.count()).select_from(MatchFeedback)) == 0


def test_drop_chapter_dry_run_refusals_and_real_delete(session_factory, monkeypatch):
    class Store:
        deleted = []

        def delete_chapter(self, cid):
            self.deleted.append(cid)
    store = Store()
    monkeypatch.setattr(drop_chapter, "get_graph_store", lambda: store)
    with session_factory() as db:
        book = official_book(db)
        teacher_book = Book(board="X", class_name="9", subject="S", publisher="P", is_reference=False, owner_teacher_id=pc._throwaway_teacher(db).id)
        db.add(teacher_book)
        db.flush()
        db.add(Chapter(book_id=teacher_book.id, title="Mine", sequence_num=1, status=ChapterStatus.READY))
        db.commit()
        book_id, teacher_id = book.id, teacher_book.id
    assert "dry run" in "\n".join(drop_chapter.run(session_factory, book_id, 3, confirm=False)) and store.deleted == []
    assert drop_chapter.run(session_factory, teacher_id, 1, True)[0].startswith("Refused")
    assert drop_chapter.run(session_factory, book_id, 9, True)[0].startswith("No chapter number 9")
    out = drop_chapter.run(session_factory, book_id, 3, confirm=True)
    assert out[0].startswith("deleted chapter 3") and "crosslink" in out[1] and len(store.deleted) == 1
    with session_factory() as db:
        assert [c.sequence_num for c in db.scalars(select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sequence_num))] == [1, 2]
