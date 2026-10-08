"""Step 10: graph quality - near-duplicate merge, backward edges, activity/recap filtering, edge copy on full reuse."""
import json

import pytest
from sqlalchemy import select

from app.core.errors import ProcessingError
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page
from app.pipeline.concepts import extract_page, looks_like_activity, looks_like_recap_page
from app.pipeline.graph import build_chapter_graph, loose_key
from app.pipeline.orchestrator import PipelineOrchestrator
from tests.test_concept_graph import NoLinksLLM, add_page, edges_by_name, make_chapter


# ---- 10d: near-duplicate names -----------------------------------------------------------------

def test_loose_key_ignores_stop_words_case_and_order():
    assert loose_key("Cell as the Basic Unit of Life") == loose_key("Cell as Basic Unit of Life")
    assert loose_key("Basic unit of life: the cell") == loose_key("Cell as Basic Unit of Life")
    assert loose_key("Cell membrane") != loose_key("Cell wall")


def test_stop_word_variants_merge_and_prerequisites_resolve_to_the_merged_concept(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Cell as the Basic Unit of Life", []))
        add_page(db, ch, 2, ("Cell membrane", ["Cell as Basic Unit of Life"]))
        add_page(db, ch, 3, ("Cell as Basic Unit of Life", []))
        report = build_chapter_graph(db, ch, NoLinksLLM())
        assert report["duplicate_names_merged"] == 1
        assert edges_by_name(db, ch) == {("Cell as the Basic Unit of Life", "Cell membrane", "page")}


NAME_VECTORS = {
    "Plastids": [1.0, 0.0, 0.0],
    "Plastids in plant cells": [0.99, 0.1, 0.0],
    "Cell wall": [0.0, 1.0, 0.0],
    "Example 1.2 Speed": [0.0, 0.0, 1.0],
    "Example 1.3 Speed": [0.0, 0.0, 1.0],
}


def vectors(names):
    return [NAME_VECTORS[n] for n in names]


def test_embedding_similarity_merges_near_duplicates_but_not_different_ideas_or_numbers(session_factory):
    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Plastids", []), ("Cell wall", []))
        add_page(db, ch, 2, ("Plastids in plant cells", []), ("Example 1.2 Speed", []))
        add_page(db, ch, 3, ("Example 1.3 Speed", []))
        report = build_chapter_graph(db, ch, NoLinksLLM(), embedder=vectors)
        assert report["merge_by_embedding"] == "done" and report["duplicate_names_merged"] == 1
        canonical = {c.name for c in db.scalars(select(Concept).where(Concept.is_canonical.is_(True)))}
        assert canonical == {"Plastids", "Cell wall", "Example 1.2 Speed", "Example 1.3 Speed"}


def test_embedder_failure_never_fails_the_chapter(session_factory):
    def broken(names):
        raise RuntimeError("secret-key-123 service down")

    with session_factory() as db:
        ch = make_chapter(db)
        add_page(db, ch, 1, ("Plastids", []))
        add_page(db, ch, 2, ("Plastids in plant cells", ["Plastids"]))
        report = build_chapter_graph(db, ch, NoLinksLLM(), embedder=broken)
        assert report["merge_by_embedding"] == "failed" and report["duplicate_names_merged"] == 0
        assert "secret" not in json.dumps(report)
        assert report["edges"] == 1


# ---- 10b/10c: recap pages and activities ------------------------------------------------------

def reply(page_kind="content", **concepts):
    items = [{"name": n, "kind": k, "description": "d"} for n, k in concepts.items()]
    return json.dumps({"page_kind": page_kind, "concepts": items})


class Scripted:
    model_name = "scripted"

    def __init__(self, text):
        self.text, self.calls = text, 0

    def complete_json(self, system, user):
        self.calls += 1
        return self.text


def test_activities_and_exercises_are_filtered_by_kind():
    out = extract_page(Scripted(reply(Osmosis="idea", Potato_demo="activity", Q3="exercise")), "Osmosis is the movement of water")
    assert [c.name for c in out.concepts] == ["Osmosis"] and out.dropped == 2


def test_activity_names_are_filtered_even_if_the_model_calls_them_ideas():
    out = extract_page(Scripted(json.dumps({"concepts": [
        {"name": "Osmosis experiment with potato pieces"}, {"name": "Onion Root Tip Experiment"},
        {"name": "Educational Activities on Cell Division"}, {"name": "Mitosis"}]})), "Mitosis divides a cell in two")
    assert [c.name for c in out.concepts] == ["Mitosis"] and out.dropped == 3
    assert looks_like_activity("Fig. 2.19 Meiosis") and not looks_like_activity("Cell membrane")


def test_recap_pages_keep_no_concepts_whether_flagged_by_the_model_or_the_heading():
    by_model = extract_page(Scripted(reply("recap", Cell="idea")), "The cell is the unit")
    assert by_model.concepts == [] and by_model.page_kind == "recap" and by_model.dropped == 1
    by_heading = extract_page(Scripted(reply("content", Cell="idea")), "At a Glance\n The cell is the unit of life")
    assert by_heading.concepts == []
    assert looks_like_recap_page("N 25 Cell\nExercises\n1. What is a cell?")
    assert not looks_like_recap_page("Cells divide. The summary of this process is long.\n" + "x " * 200)


def test_old_style_replies_without_kind_still_work():
    out = extract_page(Scripted('{"concepts":[{"name":"Matter","description":"d"}]}'), "Matter has mass")
    assert [c.name for c in out.concepts] == ["Matter"] and out.dropped == 0


# ---- pipeline level: recap pages are not flagged as bad scans; edges are copied -----------------

SENTENCES = [
    "Atoms are the smallest particles of an element that keep its chemical properties and they combine to form molecules in many ways.",
    "Molecules join together through chemical bonds and the shared electrons decide how strong each bond is within a compound.",
    "Compounds have properties very different from their elements because their atoms are arranged in fixed repeating patterns.",
]


class StubOCR:
    def __init__(self, pages):
        self.pages = pages

    def extract_layout(self, data, ext):
        return {"pages": [{"page_number": i + 1, "text": t, "lines": []} for i, t in enumerate(self.pages)]}


class ChapterLLM:
    """Page replies by text; every linking call returns a DIFFERENT edge set, like a real model would."""
    model_name = "scripted"

    def __init__(self):
        self.page_calls = self.link_calls = 0

    def complete_json(self, system, user):
        if user.startswith("CONCEPTS:\n"):
            self.link_calls += 1
            return json.dumps({"edges": [{"concept": 3, "prerequisites": [self.link_calls % 2 + 1]}]})
        self.page_calls += 1
        for i, s in enumerate(SENTENCES, 1):
            if s in user:
                return json.dumps({"concepts": [{"name": f"Concept {i}", "description": "d"}]})
        if "rivers" in user:
            return json.dumps({"concepts": [{"name": "Rivers", "description": "d"}]})
        return '{"concepts": []}'


def make_ready(db, owner_book, title, seq):
    ch = Chapter(book_id=owner_book.id, title=title, sequence_num=seq, status=ChapterStatus.PROCESSING)
    db.add(ch)
    db.flush()
    return ch


def run(db, chapter, llm, pages=SENTENCES):
    PipelineOrchestrator(db, ocr_provider=StubOCR(pages), llm_provider=llm).process_chapter_file(chapter, b"x", "pdf", None)
    chapter.status = ChapterStatus.READY
    db.flush()


def edge_names(db, chapter):
    return edges_by_name(db, chapter)


def test_identical_chapter_gets_a_copy_of_the_graph_not_a_new_llm_opinion(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        assert llm.link_calls == 1 and llm.page_calls == 3
        run(db, second, llm)
        assert llm.link_calls == 1 and llm.page_calls == 3  # no linking call, no page calls
        assert second.graph_report["edges_copied"] is True
        assert edge_names(db, second) == edge_names(db, first) and edge_names(db, first)
        new_ids = {c.id for c in db.scalars(select(Concept).join(Page).where(Page.chapter_id == second.id))}
        assert all(e.concept_id in new_ids and e.prerequisite_id in new_ids
                   for e in db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == second.id)))


def test_a_changed_page_means_the_graph_is_built_again(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        run(db, second, llm, pages=[*SENTENCES[:2], "A completely different page about rivers, deltas and the sediment they carry to the sea over thousands of years."])
        assert llm.link_calls == 2 and not second.graph_report.get("edges_copied")


def test_fresh_run_ignores_stored_concepts(session_factory):
    llm = ChapterLLM()
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        first, second = make_ready(db, book, "A", 1), make_ready(db, book, "B", 2)
        run(db, first, llm)
        PipelineOrchestrator(db, ocr_provider=StubOCR(SENTENCES), llm_provider=llm, reuse_concepts=False) \
            .process_chapter_file(second, b"x", "pdf", None)
        assert llm.page_calls == 6 and not second.graph_report.get("edges_copied")


def test_recap_page_with_no_concepts_is_not_flagged_as_a_bad_scan(session_factory):
    llm = ChapterLLM()
    long_recap = "At a Glance\n" + " ".join(["The cell is the basic unit of life and it divides."] * 8)
    with session_factory() as db:
        book = Book(board="CBSE", class_name="9", subject="Sci", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()
        ch = make_ready(db, book, "A", 1)
        run(db, ch, llm, pages=[SENTENCES[0], long_recap])
        assert ch.graph_report["review_pages"] == [] and ch.graph_report["recap_pages"] == 1
