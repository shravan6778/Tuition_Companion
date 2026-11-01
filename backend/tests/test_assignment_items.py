"""Assignments at finer grain: the `items` level, the outline the picker reads, and item + page scope for doubts and checks.

World: an official (reference) book is the teacher's source; the student owns a private copy of the same chapter whose
pages are numbered differently, so every test also proves that an assignment resolves BY LABEL against the student's
own copy and never by the source book's ids or page numbers.
"""
import uuid

import pytest
from sqlalchemy import select

from app.assignments.scope import item_key, match_items
from app.assessment import checks
from app.core.config import settings
from app.doubts.retrieval import Scope
from app.doubts.service import assignment_scope
from app.models import (Assignment, AssignmentItem, Book, Chapter, ChapterStatus, Concept, Page, PageItem, Role, User)
from app.pipeline.indexing import index_chapter
from tests.test_book_access import join_room_of, make_user

CELL = "The cell is the basic structural unit of all living organisms and every cell has a membrane and a nucleus inside it"
TISSUE = "A tissue is a group of similar cells that work together to perform one function in plants and animals such as muscle"
EXERCISES = "Exercise 2.1 questions about the cell and about tissue for the students to answer"

# (page offset applied to the student's copy, kind, label, text, linked concept or None)
ITEMS = [
    (1, "example", "Example 1", "Example 1 a cell under the microscope shows a membrane and a nucleus", "Cell"),
    (2, "diagram", "Fig. 2.1", "Fig. 2.1 a diagram of a muscle tissue made of similar cells", None),   # no link: falls back to its page's concept
    (3, "exercise_question", "Ex 2.1 Q1", "Name the three parts you can see inside every cell of an onion peel", "Cell"),
    (3, "exercise_question", "Ex 2.1 Q2", "Why is muscle called a tissue and not a single cell of the body", "Tissue"),
    (3, "exercise_question", "Ex 2.1 Q3", "Draw and label any plant cell that you have seen in your laboratory work", None),  # no link, no concept on its page
]
PAGES = {1: ("content", CELL), 2: ("content", TISSUE), 3: ("exercise", EXERCISES)}
CONCEPTS = [(1, "Cell", "basic structural unit of living things"), (2, "Tissue", "a group of similar cells with one function")]


def build_book(db, *, reference: bool, owner=None, offset: int = 0) -> tuple[Book, Chapter]:
    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=reference,
                owner_student_id=owner)
    db.add(book)
    db.flush()
    chapter = Chapter(book_id=book.id, title="Cells", sequence_num=1, status=ChapterStatus.READY)
    db.add(chapter)
    db.flush()
    pages = {}
    for number, (kind, text) in PAGES.items():
        pages[number] = Page(chapter_id=chapter.id, page_number=number + offset, content_text=text, page_kind=kind)
        db.add(pages[number])
    db.flush()
    concepts = {}
    for position, (number, name, description) in enumerate(CONCEPTS):
        concepts[name] = Concept(page_id=pages[number].id, name=name, description=description, position=position,
                                 name_key=name.lower(), is_canonical=True)
        db.add(concepts[name])
    db.flush()
    for position, (number, kind, label, text, concept) in enumerate(ITEMS):
        item = PageItem(page_id=pages[number].id, kind=kind, label=label, text=text, position=position)
        if concept:
            item.concepts.append(concepts[concept])
        db.add(item)
    db.flush()
    return book, chapter


@pytest.fixture()
def world(client, session_factory):
    teacher, th = make_user(session_factory, Role.teacher, "teachera")
    student, sh = make_user(session_factory, Role.student, "studenta")
    room = join_room_of(client, session_factory, th, sh)
    with session_factory() as db:
        source, source_chapter = build_book(db, reference=True)
        mine, my_chapter = build_book(db, reference=False, owner=student.id, offset=20)
        db.commit()
        ids = dict(book=str(source.id), chapter=str(source_chapter.id), my_book=str(mine.id), my_chapter=str(my_chapter.id))
    return dict(th=th, sh=sh, student=student, room=room, ids=ids)


def picks(*labels):
    by_label = {label: (kind, label) for _, kind, label, _, _ in ITEMS}
    return [dict(kind=by_label[label][0], label=label) for label in labels]


def assign(client, w, items, **extra):
    body = dict(level="items", book_id=w["ids"]["book"], chapter_id=w["ids"]["chapter"], room_id=w["room"]["id"],
                items=items, **extra)
    return client.post("/teacher/assignments", json=body, headers=w["th"])


# ---- the outline the picker reads ---------------------------------------------------------------------------------

def test_outline_lists_concepts_examples_exercises_and_figures_without_page_text(client, world):
    res = client.get("/teacher/assignments/outline", params={"book_id": world["ids"]["book"], "chapter_id": world["ids"]["chapter"]},
                     headers=world["th"])
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["chapter_title"] == "Cells" and body["concepts"] == ["Cell", "Tissue"]
    assert [i["label"] for i in body["examples"]] == ["Example 1"]
    assert [i["label"] for i in body["exercises"]] == ["Ex 2.1 Q1", "Ex 2.1 Q2", "Ex 2.1 Q3"]
    assert [i["label"] for i in body["figures"]] == ["Fig. 2.1"]
    assert body["exercises"][0] == {"kind": "exercise_question", "label": "Ex 2.1 Q1", "page_number": 3}
    assert "membrane" not in res.text  # labels and numbers only


def test_outline_of_a_students_private_book_is_metadata_only_and_needs_a_room_link(client, session_factory, world):
    params = {"book_id": world["ids"]["my_book"], "chapter_id": world["ids"]["my_chapter"]}
    body = client.get("/teacher/assignments/outline", params=params, headers=world["th"])
    assert body.status_code == 200 and "membrane" not in body.text
    stranger, stranger_headers = make_user(session_factory, Role.teacher, "teacherb")
    assert client.get("/teacher/assignments/outline", params=params, headers=stranger_headers).status_code == 404


# ---- creating an items assignment ---------------------------------------------------------------------------------

def test_items_assignment_stores_the_items_and_the_concepts_they_test(client, session_factory, world):
    res = assign(client, world, picks("Ex 2.1 Q1", "Ex 2.1 Q2", "Fig. 2.1"), title="Cells practice")
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["level"] == "items" and body["item_count"] == 3 and body["chapter_title"] == "Cells"
    assert [i["label"] for i in body["items"]] == ["Ex 2.1 Q1", "Ex 2.1 Q2", "Fig. 2.1"]
    # Q1 -> Cell, Q2 -> Tissue, and the figure has no link so its page's concept (Tissue) is used
    assert [c["name"] for c in body["concepts"]] == ["Cell", "Tissue"]
    with session_factory() as db:
        rows = db.scalars(select(AssignmentItem).order_by(AssignmentItem.position)).all()
        assert [r.item_key for r in rows] == ["ex 2.1 q1", "ex 2.1 q2", "fig 2.1"]
        assert [r.page_number for r in rows] == [3, 3, 2]  # the SOURCE book's pages, a hint only


def test_picking_only_one_question_stores_only_the_concept_it_tests(client, world):
    body = assign(client, world, picks("Ex 2.1 Q1")).json()
    assert [c["name"] for c in body["concepts"]] == ["Cell"]


def test_ticked_concepts_are_added_to_the_items_concepts(client, world):
    body = assign(client, world, picks("Ex 2.1 Q1"), concept_names=["Tissue"]).json()
    assert [c["name"] for c in body["concepts"]] == ["Cell", "Tissue"]


def test_items_assignment_validation(client, world):
    assert assign(client, world, []).status_code == 422                                        # nothing picked
    assert assign(client, world, [dict(kind="exercise_question", label="Ex 9.9 Q9")]).status_code == 404   # not in the chapter
    assert assign(client, world, [dict(kind="concept", label="Cell")]).status_code == 422       # concepts go in concept_names
    assert assign(client, world, picks("Ex 2.1 Q1"), concept_names=["Gravity"]).status_code == 422
    same = assign(client, world, picks("Ex 2.1 Q1", "Ex 2.1 Q1")).json()
    assert same["item_count"] == 1                                                              # duplicates are dropped


def test_only_the_owning_teacher_can_use_a_room_and_a_visible_book(client, session_factory, world):
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    res = client.post("/teacher/assignments", headers=other, json=dict(
        level="items", book_id=world["ids"]["book"], chapter_id=world["ids"]["chapter"], room_id=world["room"]["id"],
        items=picks("Ex 2.1 Q1")))
    assert res.status_code == 404


# ---- resolving against the student's own copy ---------------------------------------------------------------------

def test_student_sees_the_assignment_resolved_to_their_own_copy(client, world):
    created = assign(client, world, picks("Ex 2.1 Q1")).json()
    mine = client.get(f"/student/assignments/{created['id']}", headers=world["sh"]).json()
    assert mine["available"] is True
    assert mine["resolved_book_id"] == world["ids"]["my_book"] and mine["resolved_chapter_id"] == world["ids"]["my_chapter"]
    assert [i["label"] for i in mine["items"]] == ["Ex 2.1 Q1"]


def test_an_assignment_whose_items_are_missing_from_the_copy_is_unavailable(client, session_factory, world):
    created = assign(client, world, picks("Ex 2.1 Q1")).json()
    with session_factory() as db:
        db.query(PageItem).filter(PageItem.label == "Ex 2.1 Q1").delete()
        db.commit()
    mine = client.get(f"/student/assignments/{created['id']}", headers=world["sh"]).json()
    assert mine["available"] is False and mine["resolved_book_id"] is None


def test_item_keys_tell_decimals_apart_but_ignore_punctuation_and_wording():
    assert item_key("Fig. 9.5") == item_key("Figure 9.5") == item_key("fig 9.5")
    assert item_key("Exercise 9.5") == item_key("Ex 9.5")
    assert item_key("Ex 5.9 Q4") != item_key("Ex 9.5 Q4")


def test_a_repeated_label_is_pinned_by_page_only_when_the_copy_has_that_page(session_factory, world):
    with session_factory() as db:
        chapter = db.get(Chapter, uuid.UUID(world["ids"]["my_chapter"]))
        extra_page = db.scalar(select(Page).where(Page.chapter_id == chapter.id, Page.page_number == 21))
        db.add(PageItem(page_id=extra_page.id, kind="exercise_question", label="Ex 2.1 Q1", text="another Q1", position=9))
        db.commit()

        class W:  # what an AssignmentItem exposes
            kind, item_key = "exercise_question", "ex 2.1 q1"

        W.page_number = 23  # the source page + 20: this copy has that Q1 on page 23 only
        assert len(match_items(db, chapter, [W])) == 1
        W.page_number = 99  # no such page in this copy: both Q1s are kept
        assert len(match_items(db, chapter, [W])) == 2


# ---- doubt scope: items and their pages ---------------------------------------------------------------------------

def test_scope_is_the_picked_items_their_pages_and_the_concepts_they_test(client, session_factory, world):
    created = assign(client, world, picks("Ex 2.1 Q1")).json()
    with session_factory() as db:
        assignment = db.get(Assignment, uuid.UUID(created["id"]))
        scope = assignment_scope(db, world["student"], assignment)
        q1 = db.scalar(select(PageItem).where(PageItem.label == "Ex 2.1 Q1", PageItem.page_id.in_(
            select(Page.id).where(Page.chapter_id == uuid.UUID(world["ids"]["my_chapter"])))))
        q2 = db.scalar(select(PageItem).where(PageItem.label == "Ex 2.1 Q2", PageItem.page_id.in_(
            select(Page.id).where(Page.chapter_id == uuid.UUID(world["ids"]["my_chapter"])))))
        cell = db.scalar(select(Concept).where(Concept.name == "Cell", Concept.page_id.in_(
            select(Page.id).where(Page.chapter_id == uuid.UUID(world["ids"]["my_chapter"])))))
        tissue_page = db.scalar(select(Page).where(Page.chapter_id == uuid.UUID(world["ids"]["my_chapter"]), Page.page_number == 22))
    chapter = world["ids"]["my_chapter"]
    assert scope.item_ids == {str(q1.id)}
    assert scope.has_item(str(q1.id), str(q1.page_id), chapter)
    assert not scope.has_item(str(q2.id), str(q2.page_id), chapter)       # same exercise page, not picked
    assert scope.has_concept(str(cell.id), chapter) and scope.concept_ids == {str(cell.id)}
    assert not scope.has_page(str(tissue_page.id), chapter)


def test_an_item_with_no_concept_never_lets_the_whole_chapter_back_in():
    scope = Scope(chapter_ids={"c1"}, item_ids={"i1"}, page_ids={"p1"})
    assert not scope.has_concept("any", "c1")
    assert scope.has_item("i1", "p1", "c1") and not scope.has_item("i2", "p1", "c1")
    # chapter/concept levels behave exactly as before
    assert Scope(chapter_ids={"c1"}).has_concept("any", "c1") and Scope(chapter_ids={"c1"}).has_item("i", "p", "c1")
    assert not Scope(chapter_ids={"c1"}, concept_ids={"k1"}).has_concept("k2", "c1")


def test_doubt_inside_the_picked_items_is_grounded_and_another_idea_is_outside(client, session_factory, world, indexing_on, monkeypatch):
    monkeypatch.setattr(settings, "retrieval_min_similarity", 0.5)
    index_chapter(session_factory, uuid.UUID(world["ids"]["my_chapter"]))
    created = assign(client, world, picks("Ex 2.1 Q1")).json()

    inside = client.post("/student/doubts", headers=world["sh"], json=dict(
        text=ITEMS[2][3], assignment_id=created["id"]))
    assert inside.status_code == 200, inside.text
    assert inside.json()["status"] == "grounded"

    outside = client.post("/student/doubts", headers=world["sh"], json=dict(
        text="what is a tissue group of similar cells", assignment_id=created["id"]))
    assert outside.status_code == 200, outside.text
    assert outside.json()["status"] == "outside_assignment"


# ---- comprehension check: item + page scope -----------------------------------------------------------------------

def start_check(client, w, assignment_id):
    return client.post(f"/student/assignments/{assignment_id}/complete", headers=w["sh"])


def test_check_asks_only_about_the_concepts_the_picked_items_test(client, session_factory, world, monkeypatch):
    seen = []
    real = checks.generate_question

    def spy(provider, concept_id, name, description, page_text, already_asked=(), seed=None, focus=""):
        seen.append((name, focus))
        return real(provider, concept_id, name, description, page_text, already_asked, seed, focus)

    monkeypatch.setattr(checks, "generate_question", spy)
    created = assign(client, world, picks("Ex 2.1 Q1")).json()
    res = start_check(client, world, created["id"])
    assert res.status_code in (200, 201), res.text
    assert seen and {name for name, _ in seen} == {"Cell"}            # Tissue is in the chapter, not in the assignment
    assert all("Ex 2.1 Q1" in focus for _, focus in seen)             # the picked question steers the question writer


def test_check_of_an_item_that_tests_no_concept_says_so_instead_of_guessing(client, world):
    created = assign(client, world, picks("Ex 2.1 Q3")).json()
    assert created["concepts"] == []
    res = start_check(client, world, created["id"])
    assert res.status_code == 409 and "no concepts" in res.json()["detail"].lower()


def test_focus_is_part_of_the_question_prompt():
    prompts = []

    class Provider:
        def complete_json(self, system, user):
            prompts.append(user)
            return ('{"question":"What does a membrane do?","options":["Holds the cell","Makes light","Cuts wood","Boils water"],'
                    '"correct_index":0,"explanation":"It holds the cell."}')

    checks.generate_question(Provider(), "c1", "Cell", "unit", "page text", focus="- Ex 2.1 Q1 (exercise question): name the parts")
    assert "ASSIGNED ITEMS" in prompts[0] and "Ex 2.1 Q1" in prompts[0]
    checks.generate_question(Provider(), "c1", "Cell", "unit", "page text")
    assert "ASSIGNED ITEMS" not in prompts[1]
