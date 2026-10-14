"""See what the Quiz Agent generates on your real chapters (real LLM + Memgraph prerequisites, writes nothing).

    python -m app.db.try_quiz_agent --chapter <chapter_id> [--n 6]

Prints the planned question mix (recall / application / cross_concept), the student view (confirming no answer key is
present), and the hidden server-side key (`correct_index` or `expected_answer`)."""
import argparse
import uuid

from app.assessment import quiz_agent
from app.assignments.scope import chapter_concepts
from app.core.config import refuse_fake_llm
from app.db.session import SessionLocal
from app.graph_store import get_graph_store
from app.llm import get_llm_provider
from app.models import Chapter


def run(db, llm, store, chapter_id: uuid.UUID, total: int = 6) -> list[str]:
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return ["Chapter not found."]
    concepts = chapter_concepts(db, chapter_id)
    if not concepts:
        return ["No canonical concepts in that chapter."]

    contexts, related_map = quiz_agent.load_concept_contexts(
        db, [c.id for c in concepts], book_ids=[chapter.book_id], store=store
    )
    plan = quiz_agent.plan_quiz_questions(list(contexts), total, related_map)
    n_rec = sum(p.question_type == "recall" for p in plan)
    n_app = sum(p.question_type == "application" for p in plan)
    n_cross = sum(p.question_type == "cross_concept" for p in plan)
    out = [
        f"{chapter.title}: {len(contexts)} concepts -> {len(plan)} quiz questions "
        f"(recall={n_rec}, application={n_app}, cross_concept={n_cross})"
    ]

    asked: dict[uuid.UUID, list[str]] = {}
    valid = 0
    for item in plan:
        primary = contexts[item.concept_id]
        related = contexts.get(item.related_concept_id) if item.related_concept_id else None
        try:
            q = quiz_agent.generate_quiz_question(
                llm, item, primary, related, already_asked=asked.get(item.concept_id, ()), seed=f"try-quiz-{item.position}"
            )
        except quiz_agent.QuizAgentError as exc:
            out.append(f"\nQ{item.position + 1} [{item.question_type} / {item.answer_format}] FAILED: {exc}")
            continue

        valid += 1
        asked.setdefault(item.concept_id, []).append(q.question)
        view = quiz_agent.student_view(q)
        rel_label = f" + {related.name}" if related else ""
        out.append(f"\nQ{item.position + 1} [{view['question_type']} | {view['answer_format']} | {primary.name}{rel_label}]")
        out.append(f"  Q: {view['question']}")
        if view["options"]:
            out += [f"     {'ABCD'[i]}. {o}" for i, o in enumerate(view["options"])]
            out.append(f"  HIDDEN KEY: {'ABCD'[q.correct_index]} — {q.explanation}")
        else:
            out.append(f"  HIDDEN EXPECTED ANSWER: {q.expected_answer}")
            out.append(f"  EXPLANATION: {q.explanation}")

    out.append(f"\n{valid}/{len(plan)} valid questions generated. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--allow-fake", action="store_true")
    args = parser.parse_args()
    refuse_fake_llm(args.allow_fake)
    with SessionLocal() as db:
        print("\n".join(run(db, get_llm_provider(), get_graph_store(), uuid.UUID(args.chapter), args.n)))