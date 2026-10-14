"""Phase 4 Step 1 tests: Quiz Agent planning, Memgraph prerequisite linking, schema validation/retries, and no answer leak."""
import json
import pytest

from app.assessment import quiz_agent
from app.graph_store import get_graph_store
from app.graph_store.base import ChapterGraph, ConceptNode, EdgeRow, PageNode
from app.llm.fake_provider import FakeLLMProvider
from app.models import AnswerFormat, Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, QuestionType, Role, User


class ScriptedLLM:
    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.prompts: list[str] = []

    def complete_json(self, system: str, user: str) -> str:
        self.prompts.append(user)
        return self.replies.pop(0)


def _seed_chapter_with_memgraph(db):
    teacher = User(supertokens_user_id="st-t-p4s1", name="Teacher", username="tp4s1", phone="9100000001", role=Role.teacher)
    db.add(teacher)
    db.flush()

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()

    chapter = Chapter(book_id=book.id, title="Force and Motion", sequence_num=1, status=ChapterStatus.READY)
    db.add(chapter)
    db.flush()

    p1 = Page(chapter_id=chapter.id, page_number=1, content_text="Force is a push or pull that changes the state of motion of an object.")
    p2 = Page(chapter_id=chapter.id, page_number=2, content_text="Momentum is the product of mass and velocity, and net force changes momentum.")
    p3 = Page(chapter_id=chapter.id, page_number=3, content_text="Inertia is the natural tendency of an object to resist a change in its state of rest or motion.")
    db.add_all([p1, p2, p3])
    db.flush()

    c1 = Concept(page_id=p1.id, name="Balanced and Unbalanced Forces", description="Net force causes acceleration", name_key="force", is_canonical=True, position=0)
    c2 = Concept(page_id=p2.id, name="Linear Momentum", description="Product of mass and velocity", name_key="momentum", is_canonical=True, position=0)
    c3 = Concept(page_id=p3.id, name="Law of Inertia", description="Resistance to change in motion", name_key="inertia", is_canonical=True, position=0)
    db.add_all([c1, c2, c3])
    db.flush()

    db.add(ConceptEdge(chapter_id=chapter.id, concept_id=c2.id, prerequisite_id=c1.id, source="llm"))
    db.commit()

    store = get_graph_store()
    if store is not None:
        vec = [0.1] * 1536
        store.replace_chapter(
            ChapterGraph(
                book_id=str(book.id),
                chapter_id=str(chapter.id),
                title=chapter.title,
                sequence_num=1,
                is_reference=True,
                owner_teacher_id=None,
                embedding_model="fake-embedding",
                pages=[PageNode(str(p1.id), 1, vec), PageNode(str(p2.id), 2, vec), PageNode(str(p3.id), 3, vec)],
                concepts=[
                    ConceptNode(str(c1.id), c1.name, c1.description, 0, vec),
                    ConceptNode(str(c2.id), c2.name, c2.description, 1, vec),
                    ConceptNode(str(c3.id), c3.name, c3.description, 2, vec),
                ],
                edges=[EdgeRow(str(c2.id), str(c1.id), "llm")],
                concept_pages=[(str(c1.id), str(p1.id)), (str(c2.id), str(p2.id)), (str(c3.id), str(p3.id))],
            )
        )
    return book, chapter, [c1, c2, c3]


def test_question_mix_ratios_and_guaranteed_cross_concept():
    # Standard sizes: Short=10, Medium=20, Long=30 (50% recall, 30% application, 20% cross_concept)
    assert quiz_agent.question_mix(10, can_cross=True) == (5, 3, 2)
    assert quiz_agent.question_mix(20, can_cross=True) == (10, 6, 4)
    assert quiz_agent.question_mix(30, can_cross=True) == (15, 9, 6)
    # Even a small 2-question quiz guarantees at least 1 cross-concept question
    _, _, n_cross = quiz_agent.question_mix(2, can_cross=True)
    assert n_cross >= 1


def test_plan_and_generate_mixed_difficulty_without_answer_leak(session_factory, indexing_on):
    with session_factory() as db:
        book, _, concepts = _seed_chapter_with_memgraph(db)
        store = get_graph_store()
        contexts, related_map = quiz_agent.load_concept_contexts(
            db, [c.id for c in concepts], book_ids=[book.id], store=store
        )
        # c2 (Linear Momentum) requires c1 (Balanced and Unbalanced Forces) in Memgraph + PG
        assert concepts[0].id in related_map[concepts[1].id]

        plan = quiz_agent.plan_quiz_questions([c.id for c in concepts], total_questions=10, related_map=related_map)
        assert len(plan) == 10
        assert sum(p.question_type == QuestionType.RECALL for p in plan) == 5
        assert sum(p.question_type == QuestionType.APPLICATION for p in plan) == 3
        assert sum(p.question_type == QuestionType.CROSS_CONCEPT for p in plan) == 2

        llm = FakeLLMProvider()
        for item in plan:
            primary = contexts[item.concept_id]
            related = contexts.get(item.related_concept_id) if item.related_concept_id else None
            generated = quiz_agent.generate_quiz_question(llm, item, primary, related, seed=f"s-{item.position}")
            view = quiz_agent.student_view(generated)

            # Student view NEVER contains answer keys or explanations
            assert "correct_index" not in view
            assert "expected_answer" not in view
            assert "explanation" not in view
            assert view["question_type"] == item.question_type
            assert view["answer_format"] == item.answer_format

            if item.answer_format == AnswerFormat.MCQ:
                assert len(view["options"]) == 4
                assert generated.correct_index in (0, 1, 2, 3)
            else:
                assert view["options"] is None
                assert generated.expected_answer and len(generated.expected_answer) >= 5


def test_quiz_agent_retries_invalid_json_and_fails_cleanly_after_max_retries(session_factory):
    with session_factory() as db:
        book, _, concepts = _seed_chapter_with_memgraph(db)
        contexts, related_map = quiz_agent.load_concept_contexts(db, [c.id for c in concepts], book_ids=[book.id])
        plan = quiz_agent.plan_quiz_questions([c.id for c in concepts], total_questions=2, related_map=related_map)

        mcq_item = next(p for p in plan if p.answer_format == AnswerFormat.MCQ)
        sa_item = next(p for p in plan if p.answer_format == AnswerFormat.SHORT_ANSWER)

        # 1st reply uses forbidden "all of the above", 2nd reply is valid JSON
        good_mcq = json.dumps({
            "question": "Which statement describes balanced forces?",
            "options": ["Zero net force", "Constant acceleration", "Increasing mass", "Infinite velocity"],
            "correct_index": 0,
            "explanation": "Balanced forces produce zero net force.",
        })
        scripted = ScriptedLLM([
            json.dumps({
                "question": "Which is true?",
                "options": ["Option A", "Option B", "Option C", "All of the above"],
                "correct_index": 3,
                "explanation": "Bad option",
            }),
            good_mcq,
        ])
        q = quiz_agent.generate_quiz_question(scripted, mcq_item, contexts[mcq_item.concept_id])
        assert len(scripted.prompts) == 2
        assert "previous reply was invalid" in scripted.prompts[1]
        assert q.options[q.correct_index] == "Zero net force"

        # 3 bad replies in a row -> raises QuizAgentError with a safe human message
        bad_llm = ScriptedLLM(["not json", '{"question": "short"}', '{"question": "still bad"}'])
        with pytest.raises(quiz_agent.QuizAgentError):
            quiz_agent.generate_quiz_question(
                bad_llm, sa_item, contexts[sa_item.concept_id], contexts.get(sa_item.related_concept_id)
            )