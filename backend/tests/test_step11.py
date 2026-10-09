"""Step 11: cross-chapter prerequisites (pipeline/crosslink.py)."""
import json

import pytest
from sqlalchemy import select, text

from app.content_library.graph_view import chapter_graph
from app.core.config import settings
from app.embeddings.vectors import to_bytes
from app.graph_store import FAKE_STORE
from app.llm.fake_provider import FakeLLMProvider
from app.models import Book, Chapter, ChapterStatus, Concept, ContentEmbedding, CrossChapterEdge, Page
from app.pipeline.crosslink import CrossLinkError, crosslink_after, crosslink_chapter, earlier_chapters, explain_chapter
from app.pipeline.indexing import sync_cross_edges

MODEL = "test-embedding"


@pytest.fixture(autouse=True)
def small_vectors(monkeypatch):
    monkeypatch.setattr(settings, "embedding_dim", 3)
    monkeypatch.setattr(settings, "embedding_provider", "openai_compat")  # so MODEL vectors count as usable (not fake)
    monkeypatch.setattr(settings, "crosslink_min_similarity", 0.4)
    FAKE_STORE.clear()


class Scripted:
    """Links every offered candidate list's FIRST number unless told otherwise; counts calls."""
    model_name = "scripted"

    def __init__(self, pick=None):
        self.calls, self.pick = 0, pick

    def complete_json(self, system, user):
        self.calls += 1
        if self.pick is not None:
            return json.dumps(self.pick(user))
        return FakeLLMProvider().complete_json(system, user)


def make_book(db, owner=None):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher="X", is_reference=owner is None)
    db.add(book)
    db.flush()
    return book


def add_chapter(db, book, seq, concepts, title=None):
    """concepts: [(name, vector)]; one page per concept, all canonical, READY, with stored vectors."""
    ch = Chapter(book_id=book.id, title=title or f"Chapter {seq}", sequence_num=seq, status=ChapterStatus.READY)
    db.add(ch)
    db.flush()
    made = {}
    for i, (name, vec) in enumerate(concepts, 1):
        page = Page(chapter_id=ch.id, page_number=i, content_text=name)
        db.add(page)
        db.flush()
        c = Concept(page_id=page.id, name=name, description=f"about {name}", position=0, name_key=name.lower(), is_canonical=True)
        db.add(c)
        db.flush()
        db.add(ContentEmbedding(chapter_id=ch.id, concept_id=c.id, model=MODEL, dim=3, text_sha256=name, vector=to_bytes(vec)))
        made[name] = c
    db.flush()
    return ch, made


def edges(db, chapter):
    names = {c.id: c.name for c in db.scalars(select(Concept))}
    return {(names[e.prerequisite_id], names[e.concept_id]) for e in db.scalars(select(CrossChapterEdge).where(CrossChapterEdge.chapter_id == chapter.id))}


def test_similar_earlier_concept_becomes_a_prerequisite_and_unrelated_ones_are_never_offered(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("River", [0, 1, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [0.9, 0.1, 0])])
        llm = Scripted()
        report = crosslink_chapter(db, ch2, llm)
        assert edges(db, ch2) == {("Atom", "Molecule")}  # River (similarity ~0.11) was not even a candidate
        assert report["status"] == "done" and report["edges"] == 1 and llm.calls == 1
        assert ch2.graph_report["cross_chapter"]["edges"] == 1


def test_nothing_points_forward_and_the_first_chapter_has_no_cross_links(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        assert earlier_chapters(db, ch1) == [] and [c.id for c in earlier_chapters(db, ch2)] == [ch1.id]
        assert crosslink_chapter(db, ch1, Scripted())["status"] == "no_candidates"
        assert edges(db, ch1) == set()


def test_only_the_same_book_is_searched(session_factory):
    with session_factory() as db:
        a, b = make_book(db), make_book(db)
        add_chapter(db, b, 1, [("Atom", [1, 0, 0])])  # another book (could be another teacher's)
        ch2, _ = add_chapter(db, a, 2, [("Molecule", [1, 0, 0])])
        assert crosslink_chapter(db, ch2, Scripted())["status"] == "no_candidates"


def test_unchanged_candidates_do_not_ask_the_model_again(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        llm = Scripted()
        crosslink_chapter(db, ch2, llm)
        assert crosslink_chapter(db, ch2, llm)["status"] == "unchanged" and llm.calls == 1
        assert edges(db, ch2) == {("Atom", "Molecule")}


def test_model_may_not_pick_a_concept_it_was_not_offered_and_old_edges_survive_a_failed_run(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.95, 0.3, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        before = edges(db, ch2)
        bad = Scripted(pick=lambda user: {"links": [{"concept": 1, "prerequisites": [99]}]})
        ch2.graph_report = {**ch2.graph_report, "cross_chapter": {}}  # force a re-ask
        with pytest.raises(CrossLinkError):
            crosslink_chapter(db, ch2, bad)
        assert bad.calls == 3 and edges(db, ch2) == before  # 1 try + 2 correction retries; nothing was replaced


def test_per_concept_cap(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_max_per_concept", 1)
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.95, 0.3, 0]), ("Electron", [0.9, 0.4, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2, 3]}]}))
        assert len(edges(db, ch2)) == 1


def test_edges_follow_their_concepts_when_an_earlier_chapter_is_processed_again(session_factory):
    with session_factory() as db:
        if db.bind.dialect.name == "sqlite":
            db.execute(text("PRAGMA foreign_keys=ON"))  # SQLite ignores ON DELETE CASCADE unless asked
        book = make_book(db)
        ch1, made = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        db.commit()
        db.delete(db.get(Concept, made["Atom"].id))  # what re-processing chapter 1 does to its old concepts
        db.commit()
        assert db.scalars(select(CrossChapterEdge)).all() == []


def test_chapter_processed_after_a_later_one_relinks_the_later_one(session_factory, monkeypatch):
    with session_factory() as db:
        book = make_book(db)
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ids = (ch1.id, ch2.id)
        db.commit()
    lines = crosslink_after(session_factory, ids[0], Scripted())
    assert len(lines) == 2 and "done" in lines[1]  # chapter 1 itself, then chapter 2 gained its link
    with session_factory() as db:
        assert edges(db, db.get(Chapter, ids[1])) == {("Atom", "Molecule")}


def test_graph_view_lists_cross_chapter_links_and_hides_those_into_unready_chapters(session_factory):
    with session_factory() as db:
        book = make_book(db)
        ch1, _ = add_chapter(db, book, 1, [("Atom", [1, 0, 0])], title="Matter")
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        view = chapter_graph(db, ch2)
        assert [(x.prerequisite_name, x.prerequisite_chapter_title) for x in view.cross_chapter] == [("Atom", "Matter")]
        ch1.status = ChapterStatus.FAILED  # e.g. a failed re-upload: students must not see it, nor links into it
        db.flush()
        assert chapter_graph(db, ch2).cross_chapter == []


def test_graph_store_gets_the_cross_edges_and_traversal_follows_them(session_factory, monkeypatch):
    from app.graph_store.base import ChapterGraph, ConceptNode

    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    with session_factory() as db:
        book = make_book(db)
        ch1, c1 = add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, c2 = add_chapter(db, book, 2, [("Molecule", [1, 0.1, 0])])
        crosslink_chapter(db, ch2, Scripted())
        db.commit()
        for ch, made in ((ch1, c1), (ch2, c2)):
            FAKE_STORE.replace_chapter(ChapterGraph(
                str(book.id), str(ch.id), ch.title, ch.sequence_num, True, None, MODEL,
                concepts=[ConceptNode(str(c.id), c.name, "", 0, [1, 0, 0]) for c in made.values()],
            ))
        assert sync_cross_edges(db, book.id) is True
        molecule, atom = str(c2["Molecule"].id), str(c1["Atom"].id)
        assert [(e.concept_id, e.prerequisite_id) for e in FAKE_STORE.cross_edges(str(book.id))] == [(molecule, atom)]
        assert [(r.name, r.depth) for r in FAKE_STORE.prerequisites(molecule, [str(book.id)])] == [("Atom", 1)]
        assert FAKE_STORE.prerequisites(molecule, ["some-other-book"]) == []  # tenant filter still applies


def test_disabled_switch(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_enabled", False)
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0, 0])])
        assert crosslink_chapter(db, ch2, Scripted())["status"] == "disabled"


def test_only_the_nearest_few_candidates_are_offered(session_factory, monkeypatch):
    monkeypatch.setattr(settings, "crosslink_candidates", 1)
    seen = []

    def pick(user):
        seen.append(user)
        return {"links": []}

    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Ion", [0.9, 0.4, 0])])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        crosslink_chapter(db, ch2, Scripted(pick=pick))
    assert "Atom" in seen[0] and "Ion" not in seen[0]


WEAK = [0.45, 0.893, 0]  # cosine similarity ~0.45 with [1, 0, 0]: offered (floor 0.4) but below the keep floor (0.5)


def test_a_link_the_model_chose_is_dropped_when_the_match_is_too_weak(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})  # takes everything offered
        report = crosslink_chapter(db, ch2, llm)
        assert edges(db, ch2) == {("Atom", "Molecule")}  # the 0.45 one was offered and chosen, but not kept
        assert report["edges"] == 1 and report["dropped_weak"] == 1


def test_changing_the_keep_floor_asks_the_model_again(session_factory, monkeypatch):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})
        crosslink_chapter(db, ch2, llm)
        monkeypatch.setattr(settings, "crosslink_keep_similarity", 0.4)
        assert crosslink_chapter(db, ch2, llm)["status"] == "done" and llm.calls == 2
        assert edges(db, ch2) == {("Atom", "Molecule"), ("Symbols", "Molecule")}


def test_explain_shows_candidates_and_writes_nothing(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, 1, [("Atom", [1, 0, 0]), ("Symbols", WEAK)])
        ch2, _ = add_chapter(db, book, 2, [("Molecule", [1, 0.05, 0])])
        llm = Scripted(pick=lambda u: {"links": [{"concept": 1, "prerequisites": [1, 2]}]})
        text_out = "\n".join(explain_chapter(db, ch2, llm))
        assert "Atom" in text_out and "CHOSEN, kept" in text_out and "CHOSEN, dropped (weak)" in text_out
        assert db.scalars(select(CrossChapterEdge)).all() == [] and "cross_chapter" not in (ch2.graph_report or {})
