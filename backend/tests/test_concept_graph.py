"""Chapter concept graph: identity merging, name matching, LLM linking, cycle breaking (Rules.md §3)."""
import json
import uuid

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.errors import ProcessingError
from app.models import Book, Chapter, Concept, ConceptEdge, Page, Role
from app.pipeline.graph import build_chapter_graph, normalize_name
from app.pipeline.linking import propose_links
from tests.test_book_access import join_room_of, make_user
from tests.test_chapter_jobs import chapter_status, page_count, setup_chapter, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf


class NoLinksLLM:
    """Links nothing, so a test sees only the deterministic name-matching edges."""
    model_name = "nolinks"
    calls = 0

    def complete_json(self, system, user):
        self.calls += 1
        return json.dumps({"edges": []})


class ScriptedLLM:
    def __init__(self, edges):
        self.edges, self.calls = edges, 0

    def complete_json(self, system, user):
        self.calls += 1
        return json.dumps({"edges": self.edges})


def make_chapter(db):
    book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="Ch", sequence_num=1)
    db.add(ch)
    db.flush()
    return ch


def add_page(db, ch, number, *concepts):
    """concepts: (name, [raw prerequisite names]) tuples."""
    page = Page(chapter_id=ch.id, page_number=number, content_text=f"p{number}")
    db.add(page)
    db.flush()
    made = []
    for pos, (name, prereqs) in enumerate(concepts):
        c = Concept(page_id=page.id, name=name, description=f"about {name}", prerequisites=prereqs, position=pos)
        db.add(c)
        made.append(c)
    db.flush()
    return made


def edges_by_name(db, ch):
    names = {c.id: c.name for c in db.scalars(select(Concept)).all()}
    return {(names[e.prerequisite_id], names[e.concept_id], e.source) for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == ch.id))}


# ---- normalization -----------------------------------------------------------------

def test_normalize_name():
    assert normalize_name("  The Atom! ") == "atom"
    assert normalize_name("Law  of\tConservation") == "law of conservation"
    assert normalize_name("An Ion") == "ion"
    assert normalize_name("Atom") == normalize_name("atom.")
    assert normalize_name("Anode") == "anode"  # only a leading *word* 'a' is dropped


# ---- name matching + identity merging --------------------------------------------------

def test_prerequisite_names_resolve_to_concepts_and_unknown_ones_are_reported(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        add_page(db, ch, 2, ("Molecule", ["the atom", "Nuclear physics"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        db.commit()
        assert edges_by_name(db, ch) == {("Atom", "Molecule", "page")}
        assert report["edges"] == 1
        assert report["unresolved_prerequisites"] == [{"concept": "Molecule", "prerequisite": "Nuclear physics"}]


def test_same_named_concepts_merge_into_the_first_occurrence(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Matter", []))
        add_page(db, ch, 2, ("Atom", ["matter"]))
        add_page(db, ch, 3, ("matter.", ["Atom"]), ("Energy", ["Matter"]))  # 'matter.' is the same concept again
        report = build_chapter_graph(db, ch, NoLinksLLM())
        db.commit()
        concepts = db.execute(select(Concept, Page.page_number).join(Page).where(Page.chapter_id == ch.id)).all()
        canonical = {c.name: pn for c, pn in concepts if c.is_canonical}
        assert canonical == {"Matter": 1, "Atom": 2, "Energy": 3}
        assert report["duplicate_names_merged"] == 1
        # the page-3 duplicate's 'Atom' prerequisite would make Matter<->Atom a cycle, so it is dropped
        assert edges_by_name(db, ch) == {("Matter", "Atom", "page"), ("Matter", "Energy", "page")}
        assert report["dropped_cycle_edges"] == [{"prerequisite": "Atom", "concept": "Matter"}]
        assert all(e.concept_id != e.prerequisite_id for e in db.scalars(select(ConceptEdge)))


def test_self_prerequisite_is_ignored(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", ["Atom", "the atom"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert report["edges"] == 0 and report["dropped_cycle_edges"] == []


# ---- cycles ----------------------------------------------------------------------------

def test_two_cycle_keeps_the_forward_edge_and_drops_the_backward_one(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["B"]))
        add_page(db, ch, 2, ("B", ["A"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        # B (page 2) needing A (page 1) is the plausible direction; A needing B is the suspect one
        assert edges_by_name(db, ch) == {("A", "B", "page")}
        assert report["dropped_cycle_edges"] == [{"prerequisite": "B", "concept": "A"}]


def test_long_cycle_is_broken_and_result_is_acyclic(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["C"]))
        add_page(db, ch, 2, ("B", ["A"]))
        add_page(db, ch, 3, ("C", ["B"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert edges_by_name(db, ch) == {("A", "B", "page"), ("B", "C", "page")}
        assert len(report["dropped_cycle_edges"]) == 1

        # independent acyclicity check on what is actually stored
        names = {c.id: c.name for c in db.scalars(select(Concept))}
        deps = {}
        for e in db.scalars(select(ConceptEdge)):
            deps.setdefault(e.prerequisite_id, []).append(e.concept_id)
        state = {}

        def visit(n):
            if state.get(n) == 1:
                raise AssertionError("cycle in stored graph")
            if state.get(n) == 2:
                return
            state[n] = 1
            for m in deps.get(n, []):
                visit(m)
            state[n] = 2
        for n in names:
            visit(n)


def test_edge_order_is_deterministic_forward_first_then_earliest_dependent(session_factory):
    """A needs B, B needs C, C needs A. Only A->C (A on an earlier page than C) is a 'forward' edge, so it is
    kept first; of the two backward edges the one into the earliest page (B->A) wins, and C->B is dropped.
    The same input must always give the same graph, whatever order the rows come back in."""
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("A", ["B"]))
        add_page(db, ch, 2, ("B", ["C"]))
        add_page(db, ch, 3, ("C", ["A"]))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert edges_by_name(db, ch) == {("A", "C", "page"), ("B", "A", "page")}
        assert report["dropped_cycle_edges"] == [{"prerequisite": "C", "concept": "B"}]


# ---- LLM linking pass ---------------------------------------------------------------------

def test_llm_edges_are_added_with_source_llm_and_never_override_name_matches(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        add_page(db, ch, 2, ("Molecule", ["Atom"]))
        add_page(db, ch, 3, ("Compound", []))
        llm = ScriptedLLM([{"concept": 2, "prerequisites": [1]}, {"concept": 3, "prerequisites": [2, 3]}])
        report = build_chapter_graph(db, ch, llm)
        assert edges_by_name(db, ch) == {("Atom", "Molecule", "page"), ("Molecule", "Compound", "llm")}
        assert report["llm_linking"] == "done" and llm.calls == 1


def test_llm_linking_skipped_for_tiny_or_huge_chapters(session_factory, monkeypatch):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Atom", []))
        llm = NoLinksLLM()
        assert build_chapter_graph(db, ch, llm)["llm_linking"] == "skipped_too_few_concepts"
        add_page(db, ch, 2, ("Molecule", []))
        monkeypatch.setattr(settings, "link_max_concepts", 1)
        assert build_chapter_graph(db, ch, llm)["llm_linking"] == "skipped_too_many_concepts"
        assert llm.calls == 0


def test_propose_links_validates_retries_and_gives_up():
    concepts = [("A", ""), ("B", ""), ("C", "")]
    bad = ScriptedLLM([{"concept": 9, "prerequisites": [1]}])  # 9 is not in the list
    with pytest.raises(ProcessingError):
        propose_links(bad, concepts)
    assert bad.calls == 3  # first try + 2 corrections

    class Garbage:
        calls = 0

        def complete_json(self, s, u):
            self.calls += 1
            return '{"concepts": []}'  # wrong shape: no 'edges'
    g = Garbage()
    with pytest.raises(ProcessingError):
        propose_links(g, concepts)
    assert g.calls == 3

    ok = ScriptedLLM([{"concept": 3, "prerequisites": [1, 1, 3, 2]}, {"concept": 2, "prerequisites": [1]}])
    assert propose_links(ok, concepts) == [(2, 0), (2, 1), (1, 0)]  # de-duplicated, self-link dropped


# ---- end to end through the API --------------------------------------------------------------

def test_upload_builds_graph_and_exposes_it_to_teacher_and_linked_students(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    _, sh = make_user(session_factory, Role.student, "student1")
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)

    assert upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea", "gamma idea")).status_code == 202
    assert chapter_status(client, th, book_id, ch)["status"] == "ready"

    g = client.get(f"/teacher/books/{book_id}/chapters/{ch}/graph", headers=th).json()
    names = {n["id"]: n["name"] for n in g["nodes"]}
    assert sorted(names.values()) == ["alpha idea", "beta idea", "gamma idea"]
    # fake LLM chains each concept onto the previous one
    assert {(names[e["prerequisite_id"]], names[e["concept_id"]]) for e in g["edges"]} == {
        ("alpha idea", "beta idea"), ("beta idea", "gamma idea")}
    assert g["report"]["llm_linking"] == "done"

    assert client.get(f"/student/books/{book_id}/chapters/{ch}/graph", headers=sh).json()["edges"] == g["edges"]
    pages = client.get(f"/teacher/books/{book_id}/chapters/{ch}/pages", headers=th).json()
    linked = [c for p in pages for c in p["concepts"] if c["prerequisite_ids"]]
    assert len(linked) == 2


def test_graph_endpoints_enforce_access(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea"))
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    _, sh = make_user(session_factory, Role.student, "student1")
    url_t, url_s = f"/teacher/books/{book_id}/chapters/{ch}/graph", f"/student/books/{book_id}/chapters/{ch}/graph"

    assert client.get(url_t, headers=other).status_code == 404  # someone else's private book
    assert client.get(url_s, headers=sh).status_code == 404  # student hasn't linked it
    join_room_of(client, session_factory, th, sh)
    client.post(f"/student/books/{book_id}/link", headers=sh)
    assert client.get(url_s, headers=sh).status_code == 200
    assert client.get(f"/student/books/{book_id}/chapters/{uuid.uuid4()}/graph", headers=sh).status_code == 404


def test_reupload_replaces_graph_without_stale_edges(client, session_factory):
    th, book_id, ch = setup_chapter(client, session_factory)
    upload(client, th, book_id, ch, _text_pdf("alpha idea", "beta idea", "gamma idea"))
    upload(client, th, book_id, ch, _text_pdf("delta idea", "epsilon idea"))
    g = client.get(f"/teacher/books/{book_id}/chapters/{ch}/graph", headers=th).json()
    assert sorted(n["name"] for n in g["nodes"]) == ["delta idea", "epsilon idea"]
    assert len(g["edges"]) == 1
    with session_factory() as db:
        concept_ids = {c.id for c in db.scalars(select(Concept))}
        edges = db.scalars(select(ConceptEdge)).all()
        assert len(edges) == 1
        assert all(e.concept_id in concept_ids and e.prerequisite_id in concept_ids for e in edges)


def test_linking_failure_fails_the_chapter_and_rolls_everything_back(client, session_factory, monkeypatch):
    th, book_id, ch = setup_chapter(client, session_factory)

    class PagesOkLinkingBroken:
        model_name = "x"

        def complete_json(self, system, user):
            if user.startswith("CONCEPTS:"):
                return "definitely not json"
            return CountingLLM().complete_json(system, user).replace("Matter", user.split("TEXT:\n")[-1][:12])

    use_llm(monkeypatch, PagesOkLinkingBroken())
    upload(client, th, book_id, ch, _text_pdf("first page text", "second page text"))
    st = chapter_status(client, th, book_id, ch)
    assert st["status"] == "failed" and "depend on each other" in st["error_message"]
    assert page_count(session_factory, ch) == 0
    with session_factory() as db:
        assert db.scalars(select(ConceptEdge)).all() == [] and db.scalars(select(Concept)).all() == []
