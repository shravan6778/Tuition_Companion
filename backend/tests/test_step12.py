"""Layer 4: embeddings as a second similarity signal (pipeline/embedmatch.py)."""
import uuid

import pytest

from app.core.config import settings
from app.embeddings.vectors import to_bytes
from app.models import Book, Chapter, ChapterStatus, ContentEmbedding, Page
from app.models.user import Role, User
from app.pipeline.embedmatch import compute, embedmatch_after, embedmatch_chapter

MODEL = "test-embedding"
LONG = "word " * 40


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")
    monkeypatch.setattr(settings, "embed_match_similarity", 0.85)


def make_teacher(db, name):
    teacher = User(supertokens_user_id=f"st-{name}", name=name, username=name, phone="9" + name[-3:].rjust(3, "0"), role=Role.teacher)
    db.add(teacher)
    db.flush()
    return teacher


def make_book(db, owner=None, publisher="X"):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher=publisher,
                is_reference=owner is None, owner_teacher_id=owner.id if owner else None)
    db.add(book)
    db.flush()
    return book


def add_chapter(db, book, seq, vectors, model=MODEL, status=ChapterStatus.READY):
    ch = Chapter(book_id=book.id, title=f"Chapter {seq}", sequence_num=seq, status=status)
    db.add(ch)
    db.flush()
    for i, vec in enumerate(vectors, 1):
        page = Page(chapter_id=ch.id, page_number=i, content_text=LONG)
        db.add(page)
        db.flush()
        db.add(ContentEmbedding(chapter_id=ch.id, page_id=page.id, model=model, dim=3, text_sha256=str(uuid.uuid4()), vector=to_bytes(vec)))
    db.flush()
    return ch


A, B, C = [1, 0, 0], [0, 1, 0], [0, 0, 1]
A2 = [0.98, 0.1, 0]  # ~0.99 with A


def test_reworded_chapter_is_suggested_when_most_pages_are_close_in_meaning(session_factory):
    with session_factory() as db:
        official = make_book(db)
        add_chapter(db, official, 1, [A, B, C])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B, [0.5, 0.5, 0.7]])
        found, info = compute(db, mine)
        assert len(found) == 1 and found[0]["signal"] == "embedding" and found[0]["kind"] == "variant"
        assert found[0]["matched_pages"] == 2 and found[0]["pages_checked"] == 3 and info["status"] == "done"


def test_too_few_matching_pages_is_no_suggestion_but_shows_up_as_closest(session_factory):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B, C])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, [0.5, 0.5, 0.7], [0.4, 0.4, 0.8]])
        found, info = compute(db, mine)
        assert found == [] and info["closest"][0]["matched_pages"] == 1


def test_another_teachers_private_book_is_never_searched(session_factory):
    with session_factory() as db:
        t1, t2 = make_teacher(db, "t1"), make_teacher(db, "t2")
        add_chapter(db, make_book(db, t2), 1, [A, B])  # t2's private upload
        mine = add_chapter(db, make_book(db, t1), 1, [A, B])
        found, info = compute(db, mine)
        assert found == [] and info["status"] == "no_candidates"


def test_the_teachers_own_other_book_is_searched(session_factory):
    with session_factory() as db:
        t1 = make_teacher(db, "t1")
        add_chapter(db, make_book(db, t1, "Old"), 1, [A, B])
        mine = add_chapter(db, make_book(db, t1, "New"), 1, [A2, B])
        assert len(compute(db, mine)[0]) == 1


def test_an_official_chapter_is_only_compared_with_official_books(session_factory):
    with session_factory() as db:
        t1 = make_teacher(db, "t1")
        add_chapter(db, make_book(db, t1), 1, [A, B])
        ref = add_chapter(db, make_book(db), 1, [A, B])
        assert compute(db, ref)[1]["status"] == "no_candidates"


def test_other_models_unready_chapters_and_the_same_book_are_ignored(session_factory):
    with session_factory() as db:
        official = make_book(db)
        add_chapter(db, official, 1, [A, B], model="other-model")
        add_chapter(db, official, 2, [A, B], status=ChapterStatus.FAILED)
        teacher = make_teacher(db, "t1")
        own = make_book(db, teacher)
        add_chapter(db, own, 1, [A, B])
        mine = add_chapter(db, own, 2, [A, B])
        assert compute(db, mine)[1]["status"] == "no_candidates"


def test_fingerprint_suggestions_stay_first_and_a_book_is_not_suggested_twice(session_factory):
    with session_factory() as db:
        official = make_book(db)
        other = make_book(db, publisher="Y")
        add_chapter(db, official, 1, [A, B])
        add_chapter(db, other, 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        # the fingerprint already suggested `official`; only `other` is new (and visible: it is official too)
        mine.match_report = {"pages_checked": 2, "suggestions": [{"book_id": str(official.id), "chapter_id": None, "chapter_title": None,
                                                                    "kind": "same", "matched_pages": 2, "pages_checked": 2, "avg_similarity": 0.99}]}
        embedmatch_chapter(db, mine)
        ids = [s["book_id"] for s in mine.match_report["suggestions"]]
        assert ids == [str(official.id), str(other.id)] and mine.match_report["suggestions"][1]["signal"] == "embedding"
        embedmatch_chapter(db, mine)  # running again replaces its own suggestions, never doubles them
        assert [s["book_id"] for s in mine.match_report["suggestions"]] == ids
        assert mine.match_report["pages_checked"] == 2  # the rest of the report is untouched


def test_disabled_switch_and_missing_vectors(session_factory, monkeypatch):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A])
        monkeypatch.setattr(settings, "embed_match_enabled", False)
        assert embedmatch_chapter(db, mine)["status"] == "disabled" and "embedding_match" not in (mine.match_report or {})
        monkeypatch.setattr(settings, "embed_match_enabled", True)
        empty = add_chapter(db, make_book(db, teacher), 1, [])
        assert compute(db, empty)[1]["status"] == "no_vectors"


def test_after_hook_saves_and_never_raises(session_factory, monkeypatch):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        chapter_id = mine.id
        db.commit()
    assert "+1" in embedmatch_after(session_factory, chapter_id)
    with session_factory() as db:
        assert db.get(Chapter, chapter_id).match_report["suggestions"][0]["signal"] == "embedding"
    monkeypatch.setattr("app.pipeline.embedmatch.compute", lambda *a, **k: 1 / 0)
    assert embedmatch_after(session_factory, chapter_id) == "failed"


def test_teacher_route_exposes_the_signal(session_factory):
    from app.schemas import ChapterMatchOut
    assert ChapterMatchOut.model_fields["signal"].default == "fingerprint"


def test_a_suggestion_that_no_longer_holds_is_removed_on_the_next_run(session_factory):
    with session_factory() as db:
        add_chapter(db, make_book(db), 1, [A, B])
        teacher = make_teacher(db, "t1")
        mine = add_chapter(db, make_book(db, teacher), 1, [A2, B])
        embedmatch_chapter(db, mine)
        assert len(mine.match_report["suggestions"]) == 1
        for row in db.query(ContentEmbedding).filter(ContentEmbedding.chapter_id == mine.id):
            row.vector = to_bytes(C)  # e.g. the chapter was re-uploaded with different content
        db.flush()
        embedmatch_chapter(db, mine)
        assert mine.match_report["suggestions"] == [] and mine.match_report["embedding_match"]["added"] == 0
