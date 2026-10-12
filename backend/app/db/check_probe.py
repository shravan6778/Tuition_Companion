"""See what the comprehension check would ask, on your real concepts (real model, writes nothing).

    python -m app.db.check_probe                       # 3 concepts spread over the ready chapters
    python -m app.db.check_probe --book <id> --n 5     # 5 concepts of one book
    python -m app.db.check_probe --sizes               # only: how many questions each ready chapter's check would have

Prints each question as the student would see it, then the key and explanation on a separate line (the key is never
sent to a student before submission). Judge: is the question about the concept, is exactly one option right according to
the page, are the wrong options plausible but wrong, and is it more than a copy of the page's sentence?"""
import argparse
import uuid

from sqlalchemy import select

from app.assessment.checks import CheckQuestionError, generate_question, plan_check, question_count, student_view
from app.assignments.scope import chapter_concepts
from app.core.config import refuse_fake_llm, settings
from app.db.session import SessionLocal
from app.llm import get_llm_provider
from app.models import Book, Chapter, ChapterStatus, Concept, Page


def sizes(db_factory, book_id=None) -> list[str]:
    out = [f"questions per concept count: floor {settings.check_min_questions}, ceiling {settings.check_max_questions}"]
    with db_factory() as db:
        query = select(Chapter).where(Chapter.status == ChapterStatus.READY).order_by(Chapter.book_id, Chapter.sequence_num)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        for ch in db.scalars(query):
            n = len(chapter_concepts(db, ch.id))
            out.append(f"  {ch.title}: {n} concepts -> {question_count(n)} questions")
    return out


def run(db_factory, llm, book_id=None, n: int = 3) -> list[str]:
    out = []
    with db_factory() as db:
        query = select(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id) \
            .where(Chapter.status == ChapterStatus.READY, Concept.is_canonical.is_(True)) \
            .order_by(Chapter.book_id, Chapter.sequence_num, Page.page_number, Concept.position)
        if book_id is not None:
            query = query.where(Chapter.book_id == book_id)
        concepts = list(db.scalars(query))
        if not concepts:
            return ["no ready concepts found"]
        step = max(1, len(concepts) // n)
        picked = concepts[::step][:n]
        failures = 0
        for c in picked:
            page = db.get(Page, c.page_id)
            chapter = db.get(Chapter, page.chapter_id)
            book = db.get(Book, chapter.book_id)
            out.append(f"\n[{book.subject or ''} / {chapter.title} / p{page.page_number}] concept: {c.name}")
            try:
                q = generate_question(llm, str(c.id), c.name, c.description, page.content_text, seed=str(c.id))
            except CheckQuestionError:
                failures += 1
                out.append("    FAILED: the model did not return a valid question after retries")
                continue
            view = student_view(q)
            out.append(f"  Q: {view['question']}")
            out += [f"     {'ABCD'[i]}. {o}" for i, o in enumerate(view["options"])]
            out.append(f"  KEY (not shown to the student): {'ABCD'[q.correct_index]} - {q.explanation}")
        out.append(f"\n{len(picked) - failures}/{len(picked)} valid questions. Nothing was written.")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--sizes", action="store_true")
    parser.add_argument("--allow-fake", action="store_true")
    a = parser.parse_args()
    book = uuid.UUID(a.book) if a.book else None
    if a.sizes:
        print("\n".join(sizes(SessionLocal, book)))
    else:
        refuse_fake_llm(a.allow_fake)
        print("\n".join(run(SessionLocal, get_llm_provider(), book, a.n)))
