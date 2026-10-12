"""Phase 3 groundwork: the pieces that settle the open decisions (page kind, exercise -> concepts, retrieval and its
cut-off, photographed doubts, the comprehension check). No Phase 3 route or table exists yet."""
import json
import uuid

import pytest
from sqlalchemy import select

from app.assessment.checks import (
    CheckQuestionError, Question, concept_scores, generate_question, grade, plan_check, question_count, shuffle_options, student_view,
)
from app.assignments.scope import chapter_concepts, propose_exercise_concepts, subject_concepts
from app.core.config import settings
from app.db import backfill_page_kind, check_probe, exercise_map, try_doubt_photo
from app.db.retrieval_probe import format_report
from app.doubts.calibration import probe, summarize
from app.doubts.query import DOUBT, PAGE, TOO_SHORT, classify_doubt_text
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, Scope, retrieve, scope_for_concepts
from app.embeddings.fake_provider import FakeEmbeddingProvider
from app.graph_store.base import EdgeRow
from app.graph_store.fake_store import FakeGraphStore
from app.llm.fake_provider import FakeLLMProvider
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, PageKind
from app.pipeline.concepts import extract_page, heading_page_kind
from app.pipeline.indexing import build_chapter_payload, embed_chapter
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_step10 import SENTENCES, ChapterLLM, StubOCR, make_ready

CELL = "The cell is the basic structural unit of all living organisms and every cell has a membrane and a nucleus and cytoplasm inside it"
TISSUE = "A tissue is a group of similar cells that work together to perform one function in plants and animals such as muscle tissue"
FORCE = "Force is a push or a pull on an object and a net force changes the speed or the direction of motion of that object"
EXERCISE = "Exercises 1. What is a cell and what is a membrane 2. Name the cell parts nucleus cytoplasm 3. Why does a cell have a membrane"


def words(tag: str, n: int = 20) -> str:
    return " ".join(f"{tag}{i}" for i in range(n))


@pytest.fixture()
def embedder():
    return FakeEmbeddingProvider(settings.embedding_dim)


def add_chapter(db, book, title, seq, pages, concepts=(), status=ChapterStatus.READY):
    """pages: [(number, text, kind)], concepts: [(page number, name, description)]. Returns the chapter."""
    ch = Chapter(book_id=book.id, title=title, sequence_num=seq, status=status)
    db.add(ch)
    db.flush()
    by_number = {}
    for number, text, kind in pages:
        page = Page(chapter_id=ch.id, page_number=number, content_text=text, page_kind=kind)
        db.add(page)
        by_number[number] = page
    db.flush()
    for position, (number, name, description) in enumerate(concepts):
        db.add(Concept(page_id=by_number[number].id, name=name, description=description, position=position))
    db.flush()
    return ch


def index(db, chapter, embedder, store=None):
    embed_chapter(db, chapter, embedder)
    db.flush()
    if store is not None:
        store.replace_chapter(build_chapter_payload(db, chapter))


def make_book(db, subject="Science", reference=True, owner=None):
    book = Book(board="CBSE", class_name="9", subject=subject, publisher="NCERT", is_reference=reference, owner_teacher_id=owner)
    db.add(book)
    db.flush()
    return book


def science_chapter(db, book, embedder, store=None):
    ch = add_chapter(db, book, "Cells", 1, [
        (1, CELL, "content"), (2, TISSUE, "content"), (3, EXERCISE, "exercise"),
    ], [(1, "Cell", "The cell is the basic structural unit of living organisms with a membrane nucleus and cytoplasm"),
        (2, "Tissue", "A tissue is a group of similar cells that perform one function")])
    index(db, ch, embedder, store)
    return ch


# ---- page kind ------------------------------------------------------------------------------------

def test_heading_decides_exercise_or_recap():
    assert heading_page_kind("Exercises\n1. What is a cell?") == "exercise"
    assert heading_page_kind("Review Questions\n1. Name") == "exercise"
    assert heading_page_kind("At a Glance\nThe cell is") == "recap"
    assert heading_page_kind("Cells divide. The summary of this process is long.") is None


def test_filter_reports_the_kind_of_non_teaching_page_from_the_heading_not_the_model():
    llm = FakeLLMProvider()
    llm.complete_json = lambda s, u: json.dumps({"page_kind": "recap", "concepts": []})
    assert extract_page(llm, "Exercises\n1. What is a cell?").page_kind == "exercise"
    assert extract_page(llm, "At a Glance\nCells are units").page_kind == "recap"


def test_the_pipeline_saves_page_kind(session_factory):
    pages = SENTENCES + ["At a Glance " + SENTENCES[0], "Exercises 1. What is an atom? " + SENTENCES[1]]
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        PipelineOrchestrator(db, ocr_provider=StubOCR(pages), llm_provider=ChapterLLM()).process_chapter_file(ch, b"x", "pdf", None)
        kinds = [p.page_kind for p in db.scalars(select(Page).where(Page.chapter_id == ch.id).order_by(Page.page_number))]
    assert kinds == ["content", "content", "content", "recap", "exercise"]


def test_backfill_labels_old_pages_once_and_only_touches_content_pages(session_factory):
    with session_factory() as db:
        book = make_book(db)
        add_chapter(db, book, "Old", 1, [
            (1, CELL, "content"), (2, TISSUE, "content"), (3, FORCE, "content"), (4, CELL + " again", "content"), (5, TISSUE + " again", "content"),
            (6, "At a Glance " + CELL, "content"), (7, "Some question text without any heading " + TISSUE, "content"), (8, "Exercises 1. what", "other"),
        ])
        db.commit()
    dry = backfill_page_kind.run(session_factory, yes=False)
    assert "dry run, would label" in dry[-1]
    with session_factory() as db:
        assert {p.page_kind for p in db.scalars(select(Page))} == {"content", "other"}  # dry run wrote nothing
    backfill_page_kind.run(session_factory, yes=True)
    with session_factory() as db:
        kinds = {p.page_number: p.page_kind for p in db.scalars(select(Page))}
    # 6 = summary heading in the last 40%; 7 comes after it = exercise; 8 was labelled `other` by someone: untouched
    assert kinds == {1: "content", 2: "content", 3: "content", 4: "content", 5: "content", 6: "recap", 7: "exercise", 8: "other"}
    assert "nothing" in backfill_page_kind.run(session_factory, yes=True)[-1]


# ---- scope: how each assignment level becomes concepts ---------------------------------------------

def test_chapter_and_subject_scope_use_canonical_concepts_of_ready_chapters(session_factory, embedder):
    with session_factory() as db:
        sci, maths = make_book(db), make_book(db, "Maths")
        c1 = science_chapter(db, sci, embedder)
        add_chapter(db, sci, "Draft", 2, [(1, FORCE, "content")], [(1, "Force", "push or pull")], status=ChapterStatus.PROCESSING)
        add_chapter(db, maths, "Sets", 1, [(1, FORCE, "content")], [(1, "Set", "a collection")])
        assert [c.name for c in chapter_concepts(db, c1.id)] == ["Cell", "Tissue"]
        assert [c.name for c in subject_concepts(db, [sci.id, maths.id], "science")] == ["Cell", "Tissue"]
        assert subject_concepts(db, [], "Science") == []


def test_exercise_pages_are_mapped_to_the_concepts_they_practise(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        ch = science_chapter(db, book, embedder)
        mapping = propose_exercise_concepts(db, ch, min_similarity=0.05)
        assert mapping.status == "ok" and mapping.exercise_pages == [3]
        assert mapping.proposed[0].name == "Cell"  # the exercise is about cells and membranes
        assert mapping.per_page[3][0][0] == "Cell"
        # a high floor proposes nothing rather than something arbitrary
        assert propose_exercise_concepts(db, ch, min_similarity=0.99).proposed == []
        # the teacher can point at pages explicitly (e.g. the pages of Ex.9.5) instead of the labelled ones
        assert propose_exercise_concepts(db, ch, [2], min_similarity=0.05).proposed[0].name == "Tissue"


def test_exercise_mapping_degrades_clearly(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        plain = add_chapter(db, book, "NoEx", 1, [(1, CELL, "content")], [(1, "Cell", "d")])
        assert propose_exercise_concepts(db, plain).status == "no_exercise_pages"
        unindexed = add_chapter(db, book, "NoVec", 2, [(1, CELL, "content"), (2, EXERCISE, "exercise")], [(1, "Cell", "d")])
        assert propose_exercise_concepts(db, unindexed).status == "no_vectors"
        capped = science_chapter(db, book, embedder)
        assert len(propose_exercise_concepts(db, capped, min_similarity=-1, max_concepts=1).proposed) == 1


def test_exercise_map_command_prints_the_evidence_and_writes_nothing(session_factory, embedder):
    with session_factory() as db:
        science_chapter(db, make_book(db), embedder)
        db.commit()
    text = "\n".join(exercise_map.run(session_factory, min_similarity=0.05))
    assert "page 3:" in text and "PROPOSED: Cell" in text and "Nothing was written" in text


# ---- retrieval ---------------------------------------------------------------------------------------

@pytest.fixture()
def world(session_factory, embedder, indexing_on):
    """Two books of two teachers in one store, like production: the student is linked only to `mine`."""
    store = FakeGraphStore()
    with session_factory() as db:
        mine, other = make_book(db), make_book(db, "Science", reference=True)
        cells = science_chapter(db, mine, embedder, store)
        force = add_chapter(db, mine, "Force", 2, [(1, FORCE, "content")], [(1, "Force", "Force is a push or a pull on an object")])
        index(db, force, embedder, store)
        db.add(ConceptEdge(chapter_id=cells.id, concept_id=chapter_concepts(db, cells.id)[1].id,
                           prerequisite_id=chapter_concepts(db, cells.id)[0].id, source="llm"))
        db.flush()
        store.replace_chapter(build_chapter_payload(db, cells))
        secret = add_chapter(db, other, "Secret", 1, [(1, "photosynthesis converts sunlight water and carbon dioxide into glucose and oxygen in the chloroplast of green leaves", "content")],
                             [(1, "Photosynthesis", "Plants make glucose from sunlight water and carbon dioxide")])
        index(db, secret, embedder, store)
        db.commit()
        yield {"db": db, "store": store, "mine": mine.id, "other": other.id, "cells": cells, "force": force, "secret": secret}


def ask(w, text, embedder, scope=None, books=None, threshold=0.2):
    books = [w["mine"]] if books is None else books
    return retrieve(w["db"], text, embedder=embedder, store=w["store"], book_ids=books, scope=scope, threshold=threshold)


def test_a_doubt_inside_the_book_is_grounded_with_page_text_and_a_prerequisite_refresher(world, embedder):
    r = ask(world, "what is a tissue group of similar cells", embedder, threshold=0.5)
    assert r.status == GROUNDED and r.confidence >= 0.5
    assert r.pages[0].text.startswith("A tissue is a group") and r.pages[0].chapter_title == "Cells"
    assert r.concepts[0].name == "Tissue"
    assert [p.name for p in r.prerequisites] == ["Cell"]  # Tissue needs Cell; never the hit itself


def test_a_doubt_with_no_support_in_the_books_is_not_in_book(world, embedder):
    r = ask(world, "zebra quantum jukebox harmonica", embedder, threshold=0.5)
    assert r.status == NOT_IN_BOOK and r.pages == [] and r.concepts == []


def test_retrieval_never_leaves_the_linked_books(world, embedder):
    q = "photosynthesis sunlight water carbon dioxide glucose chloroplast"
    assert ask(world, q, embedder, threshold=0.45).status == NOT_IN_BOOK                     # not linked: invisible
    r = ask(world, q, embedder, books=[world["other"]], threshold=0.45)
    assert r.status == GROUNDED and r.pages[0].book_id == str(world["other"])             # linked: found
    assert ask(world, q, embedder, books=[], threshold=0.0).status == NOT_IN_BOOK          # no books: never "everything"


def test_the_page_text_is_checked_in_postgres_not_taken_on_trust_from_the_store(world, embedder):
    world["db"].get(Chapter, world["cells"].id).status = ChapterStatus.PROCESSING  # e.g. re-uploaded since the sync
    world["db"].flush()
    r = ask(world, "what is a tissue group of similar cells", embedder)
    assert all(p.chapter_id != str(world["cells"].id) for p in r.pages)


def test_scoped_to_an_assignment_then_outside_assignment_when_the_books_cover_it_elsewhere(world, embedder):
    q = "what is a tissue group of similar cells"
    inside = ask(world, q, embedder, scope=Scope(chapter_ids={str(world["cells"].id)}))
    assert inside.status == GROUNDED
    outside = ask(world, q, embedder, scope=Scope(chapter_ids={str(world["force"].id)}), threshold=0.3)
    assert outside.status == OUTSIDE and outside.elsewhere[0].name == "Tissue" and outside.pages == []
    cell = next(c for c in chapter_concepts(world["db"], world["cells"].id) if c.name == "Cell")
    tissue = next(c for c in chapter_concepts(world["db"], world["cells"].id) if c.name == "Tissue")
    cell_only = ask(world, q, embedder, scope=scope_for_concepts(world["db"], [cell]), threshold=0.5)
    assert cell_only.status == OUTSIDE  # a concept-level assignment is narrower than its chapter: the tissue page is outside it
    assert ask(world, q, embedder, scope=scope_for_concepts(world["db"], [tissue]), threshold=0.5).status == GROUNDED


def test_service_failures_are_unavailable_not_a_guess(world, embedder):
    world["store"].fail_with = RuntimeError("down")
    assert ask(world, "what is a tissue", embedder).status == UNAVAILABLE

    class Broken:
        model_name, dim = "x", 4

        def embed(self, texts):
            from app.embeddings import EmbeddingError
            raise EmbeddingError("down")

    world["store"].fail_with = None
    assert retrieve(world["db"], "what is a tissue", embedder=Broken(), store=world["store"], book_ids=[world["mine"]]).status == UNAVAILABLE
    assert retrieve(world["db"], "x", embedder=None, store=None, book_ids=[world["mine"]]).status == UNAVAILABLE


# ---- photographed / typed doubts ------------------------------------------------------------------------

def test_photo_text_is_classified_by_length():
    assert classify_doubt_text("", from_photo=True).kind == TOO_SHORT
    assert classify_doubt_text("smudge ink", from_photo=True).kind == TOO_SHORT
    assert classify_doubt_text("cell", from_photo=False).kind == DOUBT  # one typed word is a legitimate doubt
    assert classify_doubt_text("why does the cell need a membrane at all", from_photo=True).kind == DOUBT
    page = classify_doubt_text(words("w", 80), from_photo=True)
    assert page.kind == PAGE and page.words == 80
    assert classify_doubt_text("   ", from_photo=False).kind == TOO_SHORT


def test_try_doubt_photo_command_covers_each_outcome(world, embedder):
    run = lambda text, photo=True, scope=None: "\n".join(try_doubt_photo.run(
        world["db"], text, photo, [world["mine"]], scope or [], embedder, world["store"]))
    assert "retake" in run("blur")
    assert "retrieval: grounded" in run("what is a tissue group of similar cells")
    page = run(CELL + " " + TISSUE + " " + words("filler", 30))
    assert "classified as: page" in page and "pick the concept" in page
    assert "ask your teacher" in run("zebra quantum jukebox harmonica harmonica quantum zebra jukebox", photo=True)


# ---- the comprehension check -------------------------------------------------------------------------------

def test_check_size_has_a_floor_and_a_ceiling():
    assert [question_count(n) for n in (0, 1, 2, 5, 10, 11, 60)] == [2, 2, 2, 5, 10, 10, 10]


def test_one_concept_still_gets_a_real_check_and_a_big_scope_is_capped_weak_first():
    assert plan_check(["a"]) == ["a", "a"]
    assert plan_check([]) == []
    ids = [f"c{i}" for i in range(15)]
    plan = plan_check(ids, priority_ids=["c13", "c14", "c9", "zzz"])
    assert len(plan) == 10 and {"c13", "c14", "c9"} <= set(plan) and plan == sorted(plan, key=ids.index)
    assert plan_check(ids[:4]) == ids[:4]  # in book order, one each


class Scripted:
    model_name = "scripted"

    def __init__(self, *replies):
        self.replies, self.calls, self.prompts = list(replies), 0, []

    def complete_json(self, system, user):
        self.prompts.append(user)
        self.calls += 1
        return self.replies.pop(0)


GOOD = json.dumps({"question": "Why does a cell have a membrane?", "options": ["To control what enters", "To store sunlight", "To make bones", "To pump blood"],
                   "correct_index": 0, "explanation": "The membrane controls entry."})


def test_a_valid_question_is_graded_by_code_and_the_student_view_has_no_key():
    q = generate_question(Scripted(GOOD), "c1", "Cell membrane", "d", "page text", seed="s")
    assert q.options[q.correct_index] == "To control what enters"
    view = student_view(q)
    assert set(view) == {"concept_id", "question", "options"} and "correct_index" not in json.dumps(view) and "explanation" not in view
    assert grade(q, q.correct_index).correct and not grade(q, (q.correct_index + 1) % 4).correct
    assert not grade(q, None).correct and not grade(q, True).correct and not grade(q, 9).correct
    assert grade(q, 0).explanation == "The membrane controls entry."


def test_options_are_shuffled_but_the_key_follows_the_right_answer():
    positions = set()
    for i in range(30):
        q = shuffle_options(Question("c", "Q?" * 5, ["right", "b", "c", "d"], 0, ""), seed=str(i))
        assert q.options[q.correct_index] == "right"
        positions.add(q.correct_index)
    assert len(positions) > 1
    again = [shuffle_options(Question("c", "Q?" * 5, ["right", "b", "c", "d"], 0, ""), seed="same") for _ in range(2)]
    assert again[0].options == again[1].options  # seeded: the same question looks the same on a reload


@pytest.mark.parametrize("bad", [
    "not json",
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "a", "c", "d"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c", "All of the above"], "correct_index": 0}),
    json.dumps({"question": "Why does a cell have a membrane?", "options": ["a", "b", "c", "d"], "correct_index": 4}),
])
def test_invalid_questions_are_retried_with_a_correction_then_accepted(bad):
    llm = Scripted(bad, GOOD)
    q = generate_question(llm, "c1", "Cell", "d", "text")
    assert llm.calls == 2 and "previous reply was invalid" in llm.prompts[1] and q.question.startswith("Why does")


def test_three_invalid_replies_raise_a_safe_error():
    with pytest.raises(CheckQuestionError) as e:
        generate_question(Scripted("x", "y", "z"), "c1", "Cell", "d", "text")
    assert "try again" in str(e.value).lower()


def test_concept_scores_are_the_share_correct_per_concept():
    q = lambda c: Question(c, "Q?" * 5, ["a", "b", "c", "d"], 0, "")
    graded = [grade(q("a"), 0), grade(q("a"), 1), grade(q("b"), 0)]
    assert concept_scores(graded) == {"a": 0.5, "b": 1.0}


def test_check_probe_prints_the_question_and_the_key_separately(session_factory, embedder):
    with session_factory() as db:
        science_chapter(db, make_book(db), embedder)
        db.commit()
    text = "\n".join(check_probe.run(session_factory, FakeLLMProvider(), n=2))
    assert "Q: Which statement about" in text and "KEY (not shown to the student)" in text and "2/2 valid" in text
    sizes = "\n".join(check_probe.sizes(session_factory))
    assert "Cells: 2 concepts -> 2 questions" in sizes


# ---- calibrating "not in your book" ------------------------------------------------------------------

def test_summarize_finds_the_gap_between_in_book_and_off_topic():
    ok = summarize([0.62, 0.55, 0.7, 0.58, 0.66, 0.6, 0.64, 0.57, 0.61, 0.59], [0.2, 0.31, 0.25], [0.3], threshold=0.45)
    assert ok["separable"] and ok["recommended"] == pytest.approx((0.55 + 0.31) / 2, abs=0.01) and ok["pass"]
    overlap = summarize([0.3, 0.5, 0.6], [0.45, 0.2], [], threshold=0.4)
    assert not overlap["separable"] and overlap["recommended"] is None and not overlap["pass"]
    assert "OVERLAP" in "\n".join(format_report({**overlap, "status": "done", "doubts": 3, "off_topic_values": [0.2],
                                                 "in_book_values": [0.3], "right_chapter_top_hit": 1.0, "wrong_chapter_outside": None}))


def test_probe_runs_end_to_end_on_stored_chapters(session_factory, embedder, indexing_on):
    store = FakeGraphStore()
    with session_factory() as db:
        book = make_book(db)
        for i, (title, text) in enumerate([("Cells", CELL), ("Tissue", TISSUE), ("Force", FORCE)], 1):
            ch = add_chapter(db, book, title, i, [(1, text, "content"), (2, text + " more", "content")], [(1, title, text), (2, title + " two", text)])
            index(db, ch, embedder, store)
        db.commit()
        report = probe(db, FakeLLMProvider(), embedder, store, [book.id], pages=6)
    assert report["status"] == "done" and report["doubts"] >= 3 and 0 <= report["right_chapter_top_hit"] <= 1
    assert len(report["off_topic_values"]) == 10 and "in_book_p10" in report


def test_probe_says_when_there_is_too_little_to_judge(session_factory, embedder):
    with session_factory() as db:
        book = make_book(db)
        assert probe(db, FakeLLMProvider(), embedder, FakeGraphStore(), [book.id])["status"] == "not_enough_pages"
