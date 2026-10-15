"""Phase 4 Steps 4, 5 & 6 tests: Hybrid grading (MCQ + LLM short-answer), unified mastery updates, and phase4_check."""
import json
from types import SimpleNamespace
import uuid

import pytest
from sqlalchemy import func, select

from app.assessment import llm_grader
from app.db import phase4_check
from app.models import (
    AnswerFormat, Book, Chapter, ChapterStatus, Concept, ConceptEdge, ContentEmbedding, IndexStatus, MasteryEvent, Page,
    QuizQuestion, QuizResponse, Role, User,
)
from app.embeddings.vectors import to_bytes


class ScriptedGraderLLM:
    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls = 0

    def complete_json(self, system: str, user: str) -> str:
        self.calls += 1
        return self.replies.pop(0)


def _seed_grading_world(db):
    t1 = User(supertokens_user_id="st-t1-p4s4", name="Teacher 1", username="t1p4s4", phone="9400000001", role=Role.teacher)
    s1 = User(supertokens_user_id="st-s1-p4s4", name="Student 1", username="s1p4s4", phone="9400000002", role=Role.student, link_code="P4S4CD01")
    db.add_all([t1, s1])
    db.flush()

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()

    ch = Chapter(
        book_id=book.id,
        title="Gravitation",
        sequence_num=1,
        status=ChapterStatus.READY,
        embedding_status=IndexStatus.DONE,
        graph_sync_status=IndexStatus.DONE,
    )
    db.add(ch)
    db.flush()

    p1 = Page(chapter_id=ch.id, page_number=1, content_text="Universal law of gravitation states that every object attracts every other object with a force proportional to the product of their masses and inversely proportional to the square of the distance between them.")
    p2 = Page(chapter_id=ch.id, page_number=2, content_text="Free fall occurs when an object falls toward the Earth under gravitational force alone, experiencing acceleration due to gravity g.")
    p3 = Page(chapter_id=ch.id, page_number=3, content_text="Weight of an object is the force with which the Earth attracts it (W = m * g), whereas mass remains constant everywhere.")
    db.add_all([p1, p2, p3])
    db.flush()

    c1 = Concept(page_id=p1.id, name="Universal Law of Gravitation", description="Force proportional to masses and inverse square of distance", name_key="gravitation", is_canonical=True, position=0)
    c2 = Concept(page_id=p2.id, name="Free Fall and Acceleration g", description="Motion under gravity alone", name_key="free fall", is_canonical=True, position=0)
    c3 = Concept(page_id=p3.id, name="Mass and Weight", description="Weight is gravitational force m*g", name_key="mass weight", is_canonical=True, position=0)
    db.add_all([c1, c2, c3])
    db.flush()

    # Prerequisite chain: c2 depends on c1; c3 depends on c2
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c2.id, prerequisite_id=c1.id, source="llm"))
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c3.id, prerequisite_id=c2.id, source="llm"))

    vec_bytes = to_bytes([0.1] * 1536)
    for p in (p1, p2, p3):
        db.add(ContentEmbedding(chapter_id=ch.id, page_id=p.id, model="fake-embedding", dim=1536, text_sha256="h", vector=vec_bytes))
    for c in (c1, c2, c3):
        db.add(ContentEmbedding(chapter_id=ch.id, concept_id=c.id, model="fake-embedding", dim=1536, text_sha256="h", vector=vec_bytes))

    out = {
        "t1": {"Authorization": f"Bearer {t1.supertokens_user_id}"},
        "s1": {"Authorization": f"Bearer {s1.supertokens_user_id}"},
        "s1_id": s1.id,
        "book_id": str(book.id),
        "ch_id": str(ch.id),
        "c1_id": str(c1.id),
        "c2_id": str(c2.id),
        "c3_id": str(c3.id),
    }
    db.commit()
    return out


def test_llm_short_answer_grader_handles_blank_retries_and_threshold():
    # 1. Blank student answer -> 0.0 without calling the LLM
    llm = ScriptedGraderLLM([])
    blank_res = llm_grader.grade_short_answer(llm, "What is free fall?", "Motion under gravity alone.", "   ")
    assert blank_res.score == 0.0
    assert blank_res.correct is False
    assert llm.calls == 0

    # 2. First reply invalid JSON, second reply valid with score 0.85 (>= 0.80 -> correct=True)
    llm2 = ScriptedGraderLLM([
        "not valid json",
        json.dumps({"score": 0.85, "feedback": "Accurately explains motion under gravity alone."}),
    ])
    good_res = llm_grader.grade_short_answer(
        llm2, "What is free fall?", "Motion under gravity alone.", "When an object falls only under gravity.", "Free Fall"
    )
    assert llm2.calls == 2
    assert good_res.score == 0.85
    assert good_res.correct is True
    assert "gravity" in good_res.feedback

    # 3. Score below 0.80 (e.g. 0.65) -> correct=False
    llm3 = ScriptedGraderLLM([json.dumps({"score": 0.65, "feedback": "Mentions falling but omits that only gravity acts."})])
    partial_res = llm_grader.grade_short_answer(llm3, "What is free fall?", "Motion under gravity alone.", "Objects falling down.")
    assert partial_res.score == 0.65
    assert partial_res.correct is False

    # 4. 3 invalid replies -> raises ShortAnswerGradeError
    bad_llm = ScriptedGraderLLM(["bad 1", '{"score": 1.5, "feedback": "out of range"}', "bad 3"])
    with pytest.raises(llm_grader.ShortAnswerGradeError):
        llm_grader.grade_short_answer(bad_llm, "What is free fall?", "Motion under gravity alone.", "Some answer")


def test_hybrid_quiz_submit_updates_unified_mastery_and_propagates_weak_flags(client, session_factory):
    with session_factory() as db:
        w = _seed_grading_world(db)

    t1, s1 = w["t1"], w["s1"]
    room = client.post("/teacher/rooms", headers=t1, json={"name": "Gravitation Room", "room_type": "single_class"}).json()
    client.post("/student/rooms/join", headers=s1, json={"join_code": room["join_code"]})
    client.post(f"/student/books/{w['book_id']}/link", headers=s1)

    # Teacher generates a quiz scoped to Concept 1 (Universal Law of Gravitation) so Concept 2 and Concept 3 are unmeasured dependents
    gen = client.post(
        "/teacher/quizzes/generate",
        headers=t1,
        json={"book_id": w["book_id"], "concept_ids": [w["c1_id"]], "length": "short", "room_id": room["id"]},
    )
    assert gen.status_code == 201, gen.text
    quiz = gen.json()

    # Fetch server-side keys from DB to craft a submission where S1 fails Concept 1 (0%)
    with session_factory() as db:
        q_rows = list(db.scalars(select(QuizQuestion).where(QuizQuestion.quiz_id == uuid.UUID(quiz["id"])).order_by(QuizQuestion.position)))
        answers = []
        for q in q_rows:
            if q.answer_format == AnswerFormat.MCQ:
                answers.append({"question_id": str(q.id), "chosen_index": (q.correct_index + 1) % 4})
            else:
                answers.append({"question_id": str(q.id), "answer_text": "wrong answer"})

    sub = client.post(f"/student/quizzes/{quiz['id']}/submit", headers=s1, json={"answers": answers})
    assert sub.status_code == 200, sub.text
    graded = sub.json()
    assert graded["status"] == "submitted"
    assert graded["score"] == 0.0

    # Keys, feedback, concept_results, and propagated at_risk concepts are now revealed to S1
    assert len(graded["concept_results"]) == 1
    assert graded["concept_results"][0]["concept_id"] == w["c1_id"]
    assert graded["concept_results"][0]["weak"] is True
    at_risk_ids = {r["concept_id"] for r in graded["at_risk"]}
    assert w["c2_id"] in at_risk_ids
    assert w["c3_id"] in at_risk_ids

    # GET /student/mastery reflects the unified mastery state (1 weak, 2 at_risk)
    mastery_view = client.get("/student/mastery", headers=s1).json()
    assert mastery_view["weak"] == 1
    assert mastery_view["at_risk"] == 2

    # Submitting a second time is blocked with 409
    assert client.post(f"/student/quizzes/{quiz['id']}/submit", headers=s1, json={"answers": answers}).status_code == 409


def test_phase4_check_script_passes_and_rolls_everything_back(session_factory, indexing_on):
    with session_factory() as db:
        w = _seed_grading_world(db)
        engine = db.get_bind()
        quizzes_before = db.scalar(select(func.count()).select_from(QuizQuestion))

    opts = SimpleNamespace(book=w["book_id"], skip_model=True, allow_fake=True)
    lines, fails = phase4_check.run(engine, opts)
    output = "\n".join(lines)
    assert fails == 0, output
    assert "RESULT:" in output

    with session_factory() as db:
        quizzes_after = db.scalar(select(func.count()).select_from(QuizQuestion))
        assert quizzes_after == quizzes_before