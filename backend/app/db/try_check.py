"""See the comprehension check a chapter would give, with the real model, exactly as `POST /student/assignments/{id}/complete`
would build it (same plan, same prompts, same retries), and how grading behaves. Writes nothing.

    python -m app.db.try_check --chapter <chapter id>
    python -m app.db.try_check --chapter <id> --concept "Grid-based thinking" --concept "Origin"    # a concept-level assignment
    python -m app.db.try_check --chapter <id> --doubted "Origin"                                   # pretend the student asked about it

Prints the questions as the student sees them (no key), then the key and explanation, then what grading would give for all-right
and all-wrong answers. Judge: is each question about its concept, is exactly one option right according to the page, are the
wrong ones plausible but wrong, and do two questions on one concept ask about different aspects?"""
import argparse
import uuid

from sqlalchemy import select

from app.assessment import checks
from app.assignments.scope import chapter_concepts
from app.core.config import refuse_fake_llm, settings
from app.core.errors import ProcessingError
from app.db.session import SessionLocal
from app.llm import get_llm_provider
from app.models import Chapter, Concept, Page


def run(db, llm, chapter_id, concept_names=(), doubted=()) -> list[str]:
    chapter = db.get(Chapter, chapter_id)
    if chapter is None:
        return ["no such chapter"]
    concepts = chapter_concepts(db, chapter_id)
    if concept_names:
        wanted = {n.strip().lower() for n in concept_names}
        concepts = [c for c in concepts if c.name.lower() in wanted]
    if not concepts:
        return ["no concepts matched"]
    by_id = {str(c.id): c for c in concepts}
    priority = [str(c.id) for c in concepts if c.name.lower() in {d.strip().lower() for d in doubted}]
    plan = checks.plan_check(list(by_id), priority)
    out = [f"{chapter.title}: {len(by_id)} concepts -> {len(plan)} questions (floor {settings.check_min_questions}, ceiling {settings.check_max_questions})"]
    made, asked = [], {}
    for position, cid in enumerate(plan, 1):
        c = by_id[cid]
        page = db.get(Page, c.page_id)
        try:
            q = checks.generate_question(llm, cid, c.name, c.description or "", page.content_text, already_asked=asked.get(cid, ()), seed=f"try-{position}")
        except ProcessingError:
            out.append(f"\nQ{position} [{c.name}, p{page.page_number}] FAILED: the model gave no valid question after retries (the student would see 'couldn't write this question')")
            continue
        asked.setdefault(cid, []).append(q.question)
        made.append(q)
        view = checks.student_view(q)
        out.append(f"\nQ{position} [{c.name}, p{page.page_number}] {view['question']}")
        out += [f"     {'ABCD'[i]}. {o}" for i, o in enumerate(view["options"])]
        out.append(f"   KEY (hidden from the student until submit): {'ABCD'[q.correct_index]} - {q.explanation}")
    if made:
        right = [checks.grade(q, q.correct_index) for q in made]
        wrong = [checks.grade(q, (q.correct_index + 1) % 4) for q in made]
        out.append(f"\ngrading: all right -> {sum(g.correct for g in right)}/{len(made)}, all wrong -> {sum(g.correct for g in wrong)}/{len(made)}")
        out.append("per-concept scores if the first question were missed: " + str({by_id[k].name: v for k, v in checks.concept_scores(
            [checks.grade(q, (q.correct_index + 1) % 4 if i == 0 else q.correct_index) for i, q in enumerate(made)]).items()}))
    out.append(f"\n{len(made)}/{len(plan)} valid questions. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--concept", action="append")
    parser.add_argument("--doubted", action="append")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    refuse_fake_llm(a.allow_fake)
    with SessionLocal() as db:
        print("\n".join(run(db, get_llm_provider(), uuid.UUID(a.chapter), a.concept or (), a.doubted or ())))
