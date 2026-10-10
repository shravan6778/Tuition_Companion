"""Layer 3: chapter-title sequence (pipeline/structure.py)."""
import pytest

from app.core.config import settings
from app.models import Book, Chapter, ChapterStatus, Role
from app.pipeline import structure
from app.pipeline.structure import ordered_matches, title_overlap, title_words
from tests.test_book_access import make_user, new_book

OFFICIAL = ["Exploration and Entering", "The Building Block of Life", "Matter in Our Surroundings", "Tissues"]


def titles_book(db, titles, owner_id=None, status=ChapterStatus.READY, subject="S"):
    book = Book(board="B", class_name="9", subject=subject, publisher="P", is_reference=owner_id is None, owner_teacher_id=owner_id)
    db.add(book)
    db.flush()
    for i, t in enumerate(titles, 1):
        db.add(Chapter(book_id=book.id, title=t, sequence_num=i, status=status))
    db.flush()
    return book


def test_title_words_drop_filler_and_numbering():
    assert title_words("Chapter 2: The Building Block of Life") == {"building", "block", "life"}
    assert title_words("Chapter 3") == frozenset() and title_overlap(title_words("Chapter 3"), title_words("Chapter 3")) == 0.0


def test_a_shorter_edition_title_matches_the_longer_one():
    a, b = title_words("Exploration: Entering the World of Secondary Science"), title_words("Exploration and Entering")
    assert title_overlap(a, b) == 1.0
    assert title_overlap(title_words("Tissues"), title_words("Atoms and Molecules")) == 0.0


def test_only_matches_in_the_same_order_count():
    assert ordered_matches(["Tissues", "Exploration and Entering"], OFFICIAL) == (1, 1.0)  # reversed: only one can be in order
    n, avg = ordered_matches(["Exploration: Entering the World", "Cells: The Building Block of Life", "Tissues"], OFFICIAL)
    assert n == 3 and avg == 1.0


def test_book_level_suggestion_by_titles_before_any_page_is_processed(session_factory):
    with session_factory() as db:
        titles_book(db, OFFICIAL)
        db.commit()
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        mine = titles_book(db, ["Exploration: Entering the World of Secondary Science", "The Building Block of Life", "Our own extra chapter"],
                           owner_id=t.id, status=ChapterStatus.EMPTY)  # nothing uploaded yet
        [hit] = structure.suggest(db, mine, t.id)
        assert hit["book"].id != mine.id and hit["matched_chapters"] == 2 and hit["chapters_checked"] == 3
        assert hit["coverage"] == 0.667 and hit["candidate_chapters_loaded"] == 4


def test_one_matching_title_or_a_low_share_is_not_enough(session_factory):
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        titles_book(db, OFFICIAL)
        one = titles_book(db, ["Tissues", "Something else", "Another"], owner_id=t.id)
        low = titles_book(db, ["Exploration and Entering", "The Building Block of Life", "X", "Y", "Z"], owner_id=t.id)
        half = titles_book(db, ["Tissues", "Unrelated topic"], owner_id=t.id)
        assert structure.suggest(db, half, t.id) == []  # 1 of 2 = 0.5 passes the share rule; only the 2-chapter minimum stops it
        assert structure.suggest(db, one, t.id) == []  # one match
        assert structure.suggest(db, low, t.id) == []  # 2 of 5 = 0.4 < 0.5


def test_other_teachers_books_are_not_compared_but_own_and_official_are(session_factory):
    a = make_user(session_factory, Role.teacher, "teachera")[0]
    b = make_user(session_factory, Role.teacher, "teacherb")[0]
    with session_factory() as db:
        a_book = titles_book(db, OFFICIAL, owner_id=a.id)
        b_book = titles_book(db, OFFICIAL, owner_id=b.id)
        assert structure.suggest(db, b_book, b.id) == []  # A's private copy is invisible to B
        mine2 = titles_book(db, OFFICIAL, owner_id=a.id, subject="Other")
        assert [h["book"].id for h in structure.suggest(db, mine2, a.id)] == [a_book.id]
        assert structure.suggest(db, mine2, a.id, exclude={a_book.id}) == []  # already found by the page evidence


def test_unprocessed_chapters_of_the_other_book_are_ignored_and_switch_off(session_factory, monkeypatch):
    t = make_user(session_factory, Role.teacher, "teachera")[0]
    with session_factory() as db:
        titles_book(db, OFFICIAL, status=ChapterStatus.PROCESSING)  # nothing finished yet
        mine = titles_book(db, OFFICIAL, owner_id=t.id)
        assert structure.suggest(db, mine, t.id) == []
        titles_book(db, OFFICIAL)
        assert len(structure.suggest(db, mine, t.id)) == 1
        monkeypatch.setattr(settings, "structure_enabled", False)
        assert structure.suggest(db, mine, t.id) == []


def test_route_returns_the_structure_suggestion_with_its_signal(client, session_factory):
    t, th = make_user(session_factory, Role.teacher, "teachera")
    with session_factory() as db:
        ref = titles_book(db, OFFICIAL)
        ref_id = str(ref.id)
        db.commit()
    book = new_book(client, th)
    with session_factory() as db:
        import uuid
        for i, title in enumerate(["Exploration: Entering the World of Secondary Science", "The Building Block of Life"], 1):
            db.add(Chapter(book_id=uuid.UUID(book["id"]), title=title, sequence_num=i))
        db.commit()
    res = client.get(f"/teacher/books/{book['id']}/variant-suggestions", headers=th)
    assert res.status_code == 200, res.text
    [s] = res.json()
    assert s["book"]["id"] == ref_id and s["signal"] == "structure" and s["matched_chapters"] == 2 and s["matched_pages"] == 0
    client.post(f"/teacher/books/{book['id']}/variant-of", json={"base_book_id": ref_id}, headers=th)
    assert client.get(f"/teacher/books/{book['id']}/variant-suggestions", headers=th).json() == []  # confirmed: no longer suggested
