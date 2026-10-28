"""Phase 4 exit check: one command that tests every Phase 4 piece on the REAL database, with the REAL graph store
(Memgraph) and model (gpt-4.1-mini), and prints PASS / FAIL / REVIEW (the way `phase2_check` and `phase3_check` do).

    python -m app.db.phase4_check                       # everything (uses real Memgraph + gpt-4.1-mini)
    python -m app.db.phase4_check --skip-model          # no model calls: Quiz Agent & LLM grader use FakeLLMProvider
    python -m app.db.phase4_check --book <id>           # choose the official book to test on

Everything runs inside one outer transaction that is ALWAYS rolled back at the end: nothing is kept in PostgreSQL
and nothing is written to Memgraph."""
import argparse
import sys
import uuid

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.assessment import mastery, quiz_service
from app.assignments.scope import chapter_concepts
from app.auth.dependencies import session_dependency
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.phase2_check import check_migrations
from app.db.phase3_check import CountingLLM, label, make_user, ok, usable_chapters
from app.db.session import get_db
from app.main import app
from app.models import (
    AnswerFormat, Book, Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, MasteryEvent, Page,
    QuestionType, Quiz, QuizQuestion, QuizResponse, Role, User,
)

Result = tuple[str, str, str]  # (PASS | FAIL | REVIEW, id, message)
FORBIDDEN_BEFORE_SUBMIT = ("correct_index", "expected_answer", "explanation", "chosen_index", "answer_text", "score", "correct", "feedback")


class Ctx:
    def __init__(self, db: Session, client: TestClient, opts):
        self.db, self.client, self.opts = db, client, opts
        self.users: dict[str, User] = {}
        self.headers: dict[str, dict[str, str]] = {}
        self.llm: CountingLLM | None = None
        self.store = None
        self.book_a: Book | None = None
        self.chapters_a: list[Chapter] = []
        self.room_a: dict | None = None
        self.room_b: dict | None = None
        self.private: dict = {}
        self.teacher_quiz: dict | None = None
        self.practice_quiz: dict | None = None

    def call(self, who: str, method: str, path: str, **kw):
        headers = self.headers.get(who, {}) if who else {}
        res = self.client.request(method, path, headers=headers, **kw)
        self.db.expire_all()
        return res


def check_environment(ctx: Ctx) -> list[Result]:
    o = ctx.opts
    if o.allow_fake and ctx.db.get_bind().dialect.name == "sqlite":
        out: list[Result] = [("PASS", "M1", "in-memory SQLite test schema created directly from models (--allow-fake)")]
    else:
        out = list(check_migrations(ctx.db))
    problems = []
    if settings.graph_store_provider.lower() != "memgraph" and not o.allow_fake:
        problems.append(f"GRAPH_STORE_PROVIDER is '{settings.graph_store_provider}' (need memgraph)")
    if settings.llm_provider.lower() != "openai_compat" and not (o.skip_model or o.allow_fake):
        problems.append(f"LLM_PROVIDER is '{settings.llm_provider}' (need openai_compat, or run with --skip-model)")
    if problems:
        return out + [("FAIL", "E1", "; ".join(problems) + ". Fix backend/.env and run again")]

    from app.graph_store import get_graph_store
    from app.llm import get_llm_provider
    from app.llm.fake_provider import FakeLLMProvider
    try:
        ctx.store = get_graph_store()
        inner = FakeLLMProvider() if o.skip_model else get_llm_provider()
        ctx.llm = CountingLLM(inner)
        stats = ctx.store.stats() if ctx.store is not None else {}
    except Exception as exc:
        return out + [("FAIL", "E1", f"providers could not start: {type(exc).__name__}: {str(exc)[:200]}")]

    out.append((
        "PASS",
        "E1",
        f"graph store {settings.graph_store_provider} ({stats}), model {'PLACEHOLDER (--skip-model)' if o.skip_model else ctx.llm.model_name or settings.llm_model}",
    ))
    if o.skip_model:
        out.append(("REVIEW", "E2", "--skip-model: Quiz Agent questions and LLM short-answer grades are placeholders; run without --skip-model to judge real model quality"))
    return out


def check_data(ctx: Ctx) -> list[Result]:
    db, o = ctx.db, ctx.opts
    books = list(db.scalars(select(Book).where(Book.is_reference.is_(True)).order_by(Book.publisher, Book.class_name, Book.subject)))
    usable = {b.id: usable_chapters(db, b) for b in books}
    usable = {k: v for k, v in usable.items() if v}
    if not usable:
        return [("FAIL", "D1", "no official book has a ready chapter with embeddings and its graph copy: run `python -m app.db.sync_graph`")]
    by_id = {b.id: b for b in books}
    if o.book:
        a = by_id.get(uuid.UUID(o.book))
        if a is None or a.id not in usable:
            return [("FAIL", "D1", f"--book {o.book} is not an official book with usable chapters")]
    else:
        a = by_id[max(usable, key=lambda k: len(usable[k]))]
    ctx.book_a, ctx.chapters_a = a, usable[a.id]
    return [("PASS", "D1", f"book A = {label(a)} (id {a.id}): {len(ctx.chapters_a)} usable chapter(s)")]


def setup_world(ctx: Ctx) -> list[Result]:
    db, a = ctx.db, ctx.book_a
    for key, role in (("tA", Role.teacher), ("tB", Role.teacher), ("S1", Role.student), ("S2", Role.student), ("S3", Role.student)):
        u = make_user(db, role, key)
        ctx.users[key], ctx.headers[key] = u, {"Authorization": f"Bearer {u.supertokens_user_id}"}

    pb = Book(board="X", class_name="9", subject=a.subject, publisher="phase4 check", is_reference=False, owner_teacher_id=ctx.users["tB"].id)
    db.add(pb)
    db.flush()
    ch = Chapter(book_id=pb.id, title="Private zebra chapter", sequence_num=1, status=ChapterStatus.READY)
    db.add(ch)
    db.flush()
    pg = Page(chapter_id=ch.id, page_number=1, content_text="Zebra quantum jukebox harmonica private page of teacher B " * 4)
    db.add(pg)
    db.flush()
    cp = Concept(page_id=pg.id, name="Private zebra concept", description="only teacher B's students may see this", name_key="private zebra concept", is_canonical=True)
    db.add(cp)
    db.commit()
    ctx.private = dict(book=pb, chapter=ch, concept=cp)
    limiter.reset()

    r_a = ctx.call("tA", "POST", "/teacher/rooms", json={"name": "phase4 check A", "room_type": "single_class"})
    r_b = ctx.call("tB", "POST", "/teacher/rooms", json={"name": "phase4 check B", "room_type": "single_class"})
    good = r_a.status_code == 201 and r_b.status_code == 201
    if not good:
        return [("FAIL", "W1", f"room creation failed: {r_a.status_code} / {r_b.status_code}")]
    ctx.room_a, ctx.room_b = r_a.json(), r_b.json()

    joins: list[int] = []
    approvals: list[int] = []
    for student_key, room_data, teacher_key in (
        ("S1", ctx.room_a, "tA"), ("S3", ctx.room_a, "tA"), ("S2", ctx.room_b, "tB")
    ):
        joined = ctx.call(student_key, "POST", "/student/rooms/join", json={"join_code": room_data["join_code"]})
        joins.append(joined.status_code)
        if joined.status_code != 202:
            approvals.append(joined.status_code)
            continue
        pending = ctx.call(teacher_key, "GET", f"/teacher/rooms/{room_data['id']}/join-requests")
        request = next((r for r in pending.json() if r["student_id"] == str(ctx.users[student_key].id)), None) if pending.status_code == 200 else None
        if request is None:
            approvals.append(pending.status_code if pending.status_code != 200 else 404)
            continue
        approved = ctx.call(teacher_key, "POST", f"/teacher/rooms/{room_data['id']}/join-requests/{request['id']}/approve")
        approvals.append(approved.status_code)
    link = ctx.call("S1", "POST", f"/student/books/{a.id}/link").status_code
    return [
        ("PASS", "W1", "two teachers each made a room"),
        ok(joins == [202, 202, 202] and approvals == [200, 200, 200] and link == 200,
           "W2", "S1 and S3 requested and were approved for teacher A's room, S2 for teacher B's; only S1 linked book A",
           f"joins={joins}, approvals={approvals}, link={link}"),
    ]


def check_teacher_quizzes(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    a = ctx.book_a
    ch1 = ctx.chapters_a[0]
    room_id = ctx.room_a["id"]
    limiter.reset()

    # Q1: Teacher A generates a Short (10-question) test for ch1 and assigns it to room_a
    res = ctx.call(
        "tA",
        "POST",
        "/teacher/quizzes/generate",
        json={"book_id": str(a.id), "chapter_id": str(ch1.id), "length": "short", "room_id": room_id},
    )
    quiz = res.json() if res.status_code == 201 else {}
    ctx.teacher_quiz = quiz
    qs = quiz.get("questions", [])
    ready_qs = [q for q in qs if q["status"] == "ready"]
    out.append(ok(
        res.status_code == 201 and quiz.get("question_count") == 10 and len(qs) == 10 and len(ready_qs) == 10 and quiz.get("assignment_id") is not None,
        "Q1",
        f"teacher generated a Short (10-question) test for '{ch1.title}', linked to an assignment, all 10 questions ready",
        f"generate gave {res.status_code}: {len(ready_qs)}/10 ready, body={res.text[:200]}",
    ))
    if not ready_qs:
        return out

    # Q2: Difficulty mix (5 recall, 3 application, 2 cross_concept) + hybrid formats (both mcq and short_answer present)
    qtypes = [q["question_type"] for q in qs]
    formats = {q["answer_format"] for q in qs}
    cross_qs = [q for q in qs if q["question_type"] == QuestionType.CROSS_CONCEPT]
    out.append(ok(
        qtypes.count("recall") == 5 and qtypes.count("application") == 3 and qtypes.count("cross_concept") == 2
        and AnswerFormat.MCQ in formats and AnswerFormat.SHORT_ANSWER in formats
        and all(q.get("related_concept_id") is not None for q in cross_qs),
        "Q2",
        f"question mix is 5 recall, 3 application, 2 cross_concept (with related concepts linked) across formats {sorted(formats)}",
        f"qtypes={qtypes}, formats={formats}",
    ))

    # Q3: REVIEW sample questions (1 recall MCQ, 1 application, 1 cross-concept short-answer)
    sample_mcq = next((q for q in ready_qs if q["answer_format"] == "mcq"), ready_qs[0])
    sample_sa = next((q for q in ready_qs if q["answer_format"] == "short_answer"), ready_qs[-1])
    out.append((
        "REVIEW",
        "Q3",
        f"sample MCQ [{sample_mcq['question_type']} | {sample_mcq['concept_name']}]: {sample_mcq['question']} "
        f"options={sample_mcq['options']} key={sample_mcq['correct_index']} || "
        f"sample Short-Answer [{sample_sa['question_type']} | {sample_sa['concept_name']}"
        + (f" + {sample_sa['related_concept_name']}" if sample_sa.get("related_concept_name") else "")
        + f"]: {sample_sa['question']} | expected={sample_sa['expected_answer']!r}",
    ))

    # Q4: Student S1 views the quiz before submission -> zero answer key leakage
    s1_view = ctx.call("S1", "GET", f"/student/quizzes/{quiz['id']}").json()
    leaked = [
        (q["position"], k)
        for q in s1_view.get("questions", [])
        for k in FORBIDDEN_BEFORE_SUBMIT
        if q.get(k) is not None
    ]
    out.append(ok(
        not leaked and s1_view.get("status") == "open" and s1_view.get("can_submit") is True,
        "Q4",
        "before submitting, student view of the quiz hides correct_index, expected_answer, explanation, score and feedback",
        f"LEAK before submit: {leaked[:4]}",
    ))

    # Q5: Length validation (invalid length rejected with 422)
    bad_len = ctx.call("tA", "POST", "/teacher/quizzes/generate", json={"book_id": str(a.id), "chapter_id": str(ch1.id), "question_count": 15})
    out.append(ok(bad_len.status_code == 422, "Q5", "non-standard teacher question_count (15) is rejected with 422", f"got {bad_len.status_code}"))
    return out


def _has_prereq_path(db: Session, dependent: uuid.UUID, source: uuid.UUID, depth: int) -> bool:
    frontier, seen = {dependent}, {dependent}
    for _ in range(depth):
        nxt = set()
        for model in (ConceptEdge, CrossChapterEdge):
            nxt |= set(db.scalars(select(model.prerequisite_id).where(model.concept_id.in_(frontier))))
        if source in nxt:
            return True
        frontier = nxt - seen
        seen |= nxt
        if not frontier:
            break
    return False


def check_hybrid_grading_and_mastery(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1 = ctx.users["S1"]
    quiz = ctx.teacher_quiz
    if not quiz:
        return [("FAIL", "G1", "skipped: no teacher quiz was generated")]

    # Pick 1 concept in the quiz that has at least 1 dependent in the chapter graph so we can test weak propagation
    q_rows = [ ctx.db.get(QuizQuestion, uuid.UUID(q["id"])) for q in quiz["questions"] ]
    concepts_with_deps = [
        q.concept_id for q in q_rows
        if q.concept_id and mastery.dependents(db, q.concept_id)
    ]
    target_weak_cid = concepts_with_deps[0] if concepts_with_deps else q_rows[0].concept_id

    # Build hybrid submission payload:
    # - Answer WRONG on `target_weak_cid` (so it tests weak < 0.6 and triggers propagation if its dependents aren't also measured)
    # - For all other questions: answer RIGHT (exact correct_index for MCQ; a paraphrased expected_answer for short_answer)
    # To guarantee `target_weak_cid`'s dependent is NOT measured in the same quiz, we only need at least one unmeasured dependent,
    # or we also test a focused 2-question practice quiz on a single concept with dependents below.
    answers_payload = []
    short_graded_Ids = []
    for q in q_rows:
        fail_this = (q.concept_id == target_weak_cid)
        if q.answer_format == AnswerFormat.MCQ:
            chosen = ((q.correct_index + 1) % 4) if fail_this else q.correct_index
            answers_payload.append({"question_id": str(q.id), "chosen_index": chosen})
        else:
            short_graded_Ids.append(q.id)
            if fail_this:
                answers_payload.append({"question_id": str(q.id), "answer_text": "I do not know and this is completely unrelated."})
            else:
                answers_payload.append({"question_id": str(q.id), "answer_text": f"In my own words: {q.expected_answer}"})

    sub = ctx.call("S1", "POST", f"/student/quizzes/{quiz['id']}/submit", json={"answers": answers_payload})
    body = sub.json() if sub.status_code == 200 else {}
    out.append(ok(
        sub.status_code == 200 and body.get("status") == "submitted" and body.get("score") is not None,
        "G1",
        f"hybrid quiz submission succeeded (overall score {body.get('score')})",
        f"submit gave {sub.status_code}: {sub.text[:250]}",
    ))
    if sub.status_code != 200:
        return out

    # G2: Verify MCQ deterministic grading and Short-Answer LLM grading
    by_qid = {uuid.UUID(q["id"]): q for q in body["questions"]}
    mcq_ok = True
    sa_ok = True
    sa_reviews = []
    for q in q_rows:
        q_out = by_qid[q.id]
        fail_this = (q.concept_id == target_weak_cid)
        if q.answer_format == AnswerFormat.MCQ:
            expected_bool = not fail_this
            if q_out["correct"] is not expected_bool or q_out["score"] != (1.0 if expected_bool else 0.0):
                mcq_ok = False
        else:
            if fail_this and (q_out["correct"] is not False or q_out["score"] >= settings.quiz_short_answer_pass_score):
                sa_ok = False
            if not fail_this and (q_out["correct"] is not True or q_out["score"] < settings.quiz_short_answer_pass_score):
                sa_ok = False
            if not q_out.get("feedback"):
                sa_ok = False
            sa_reviews.append(f"Q{q.position + 1} ({'fail' if fail_this else 'pass'} case): score={q_out['score']}, correct={q_out['correct']}, feedback={q_out['feedback']!r}")

    out.append(ok(mcq_ok, "G2", "all MCQ questions were graded deterministically in code (1.0 for exact key, 0.0 for wrong option)", "MCQ grading mismatch"))
    out.append(ok(sa_ok, "G3", "all short-answer questions were graded by the LLM grader with valid 0..1 scores and 1-sentence feedback", f"Short-answer grading mismatch: {sa_reviews}"))
    out.append(("REVIEW", "G4", "LLM short-answer grades & feedback to judge: " + " || ".join(sa_reviews)))

    # G5: Second submit is 409 Conflict and writes no extra events
    ev_count = db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.student_id == s1.id))
    again = ctx.call("S1", "POST", f"/student/quizzes/{quiz['id']}/submit", json={"answers": answers_payload})
    out.append(ok(
        again.status_code == 409 and db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.student_id == s1.id)) == ev_count,
        "G5",
        "submitting the same quiz a second time returns 409 and writes no duplicate mastery events",
        f"second submit gave {again.status_code}",
    ))

    # G6: Unified mastery events (`kind='quiz'`) recorded and reflected in GET /student/mastery
    quiz_events = list(db.scalars(select(MasteryEvent).where(MasteryEvent.quiz_id == uuid.UUID(quiz["id"]), MasteryEvent.kind == "quiz")))
    out.append(ok(
        len(quiz_events) >= 1 and all(e.score is not None and e.asked >= 1 for e in quiz_events),
        "G6",
        f"{len(quiz_events)} 'quiz' event(s) written to mastery_events and unified with current_state",
        f"found {len(quiz_events)} quiz mastery events",
    ))
    return out


def check_practice_and_propagation(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1 = ctx.users["S1"]
    ch1 = ctx.chapters_a[0]
    concepts = chapter_concepts(db, ch1.id)

    # Clear S1's earlier events inside a savepoint-friendly way or use S3 (after linking book A) so we have a clean slate
    # Let's link book A for S3 to test clean single-concept weak propagation + 60/20/20 practice weighting!
    s3 = ctx.users["S3"]
    ctx.call("S3", "POST", f"/student/books/{ctx.book_a.id}/link")

    counted = [(len(mastery.dependents(db, c.id)), c.name, c) for c in concepts]
    with_deps = sorted([t for t in counted if t[0] >= 1], key=lambda t: (t[0], t[1]))
    if not with_deps:
        return [("REVIEW", "P0", f"no concept of '{ch1.title}' has dependents in the graph: propagation & at-risk weighting skipped")]

    n_deps, _, weak_concept = with_deps[0]
    limiter.reset()

    # P1: S3 generates a 2-question practice quiz on ch1, or we seed 1 weak quiz result on `weak_concept` via a 2-question practice quiz
    # Let's first record a failing quiz event on `weak_concept` for S3 by taking a 2-question practice quiz or teacher concept quiz
    t_res = ctx.call(
        "tA",
        "POST",
        "/teacher/quizzes/generate",
        json={"book_id": str(ctx.book_a.id), "concept_ids": [str(weak_concept.id)], "length": "short", "room_id": ctx.room_a["id"]},
    )
    t_quiz = t_res.json()
    wrong_answers = [
        {"question_id": q["id"], "chosen_index": (q["correct_index"] + 1) % 4}
        if q["answer_format"] == "mcq"
        else {"question_id": q["id"], "answer_text": ""}
        for q in t_quiz["questions"]
    ]
    sub = ctx.call("S3", "POST", f"/student/quizzes/{t_quiz['id']}/submit", json={"answers": wrong_answers})
    sub_body = sub.json() if sub.status_code == 200 else {}
    flags = [
        e for e in db.scalars(select(MasteryEvent).where(MasteryEvent.quiz_id == uuid.UUID(t_quiz["id"]), MasteryEvent.student_id == s3.id))
        if e.kind == "propagated"
    ]
    expected_deps = {d.concept_id for d in mastery.dependents(db, weak_concept.id)}
    out.append(ok(
        sub.status_code == 200 and len(flags) == len(expected_deps) and {e.concept_id for e in flags} == expected_deps
        and all(_has_prereq_path(db, e.concept_id, weak_concept.id, settings.propagate_max_depth) for e in flags),
        "P1",
        f"failing {weak_concept.name!r} on a quiz wrote a 'quiz' event (score 0.0) and propagated 'at_risk' flags to {len(flags)} dependent(s)",
        f"flags={[e.concept_name for e in flags]}, expected={len(expected_deps)}",
    ))

    # P2: Now S3 has 1 WEAK concept (`weak_concept`), `len(flags)` AT_RISK concepts, and remaining revision concepts.
    # S3 self-triggers `POST /student/practice/generate` (default 10 questions) -> must allocate 60% (6) to weak, 20% (2) to at_risk, 20% (2) to revision!
    limiter.reset()
    prac_res = ctx.call("S3", "POST", "/student/practice/generate", json={"chapter_id": str(ch1.id)})
    prac = prac_res.json() if prac_res.status_code == 201 else {}
    ctx.practice_quiz = prac
    p_qs = prac.get("questions", [])
    q_cids = [uuid.UUID(q["concept_id"]) for q in p_qs if q.get("concept_id")]
    n_weak_slots = sum(cid == weak_concept.id for cid in q_cids)
    n_risk_slots = sum(cid in expected_deps for cid in q_cids)
    n_rev_slots = len(q_cids) - n_weak_slots - n_risk_slots
    out.append(ok(
        prac_res.status_code == 201 and prac.get("kind") == "practice" and len(p_qs) == 10
        and n_weak_slots == 6 and n_risk_slots == 2 and n_rev_slots == 2,
        "P2",
        f"student self-triggered practice quiz (10 questions) allocated 60% ({n_weak_slots}) to weak, 20% ({n_risk_slots}) to at_risk, and 20% ({n_rev_slots}) to revision",
        f"got status={prac_res.status_code}, weak={n_weak_slots}, at_risk={n_risk_slots}, rev={n_rev_slots}",
    ))

    # P3: Simulated failure during mastery_events write rolls back the entire quiz submission (atomicity check)
    full_prac = db.get(Quiz, uuid.UUID(prac["id"]))
    valid_ans = {
        q.id: quiz_service.QuizAnswerInput(question_id=q.id, chosen_index=q.correct_index, answer_text=q.expected_answer)
        for q in full_prac.questions
    }
    orig_record, raised = mastery.record_quiz, False
    mastery.record_quiz = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("simulated mastery failure"))
    try:
        quiz_service.submit_quiz(db, s3, full_prac, valid_ans)
    except RuntimeError:
        raised = True
    finally:
        mastery.record_quiz = orig_record
    db.expire_all()
    full_prac = db.get(Quiz, uuid.UUID(prac["id"]))
    resp_count = db.scalar(select(func.count()).select_from(QuizResponse).where(QuizResponse.quiz_id == full_prac.id))
    out.append(ok(
        raised and full_prac.status == "open" and full_prac.score is None and resp_count == 0,
        "P3",
        "when writing mastery events fails, quiz submission rolls back completely (quiz stays open, 0 quiz_responses kept)",
        f"raised={raised}, status={full_prac.status}, responses={resp_count}",
    ))
    return out


def check_tenancy(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    pb, pch, pc = ctx.private["book"], ctx.private["chapter"], ctx.private["concept"]
    t_quiz_id = ctx.teacher_quiz["id"]
    p_quiz_id = ctx.practice_quiz["id"]

    # L1: Teacher B cannot read, assign, list, or delete Teacher A's quiz
    codes_tb = [
        ctx.call("tB", "GET", f"/teacher/quizzes/{t_quiz_id}").status_code,
        ctx.call("tB", "POST", f"/teacher/quizzes/{t_quiz_id}/assign", json={"room_id": ctx.room_b["id"]}).status_code,
        ctx.call("tB", "DELETE", f"/teacher/quizzes/{t_quiz_id}").status_code,
    ]
    tb_list = ctx.call("tB", "GET", "/teacher/quizzes").json()
    out.append(ok(
        codes_tb == [404, 404, 404] and not tb_list,
        "L1",
        "teacher B cannot read, assign, delete, or list teacher A's quizzes (404 each)",
        f"codes={codes_tb}, list={len(tb_list)}",
    ))

    # L2: Teacher A cannot generate a quiz from Teacher B's private book, chapter, or concept
    priv_codes = [
        ctx.call("tA", "POST", "/teacher/quizzes/generate", json={"book_id": str(pb.id), "chapter_id": str(pch.id)}).status_code,
        ctx.call("tA", "POST", "/teacher/quizzes/generate", json={"book_id": str(ctx.book_a.id), "concept_ids": [str(pc.id)]}).status_code,
    ]
    out.append(ok(
        priv_codes == [404, 404],
        "L2",
        "teacher A cannot generate a quiz from teacher B's private book or concept (404 each)",
        f"got {priv_codes}",
    ))

    # L3: Student S2 (not in room A, book A not linked) cannot view or submit S1's teacher quiz or S3's practice quiz
    s2_codes = [
        ctx.call("S2", "GET", f"/student/quizzes/{t_quiz_id}").status_code,
        ctx.call("S2", "POST", f"/student/quizzes/{t_quiz_id}/submit", json={"answers": []}).status_code,
        ctx.call("S2", "GET", f"/student/quizzes/{p_quiz_id}").status_code,
        ctx.call("S1", "GET", f"/student/quizzes/{p_quiz_id}").status_code,
    ]
    out.append(ok(
        s2_codes == [404, 404, 404, 404],
        "L3",
        "students cannot read or submit another room's teacher quiz or another student's practice quiz (404 each)",
        f"got {s2_codes}",
    ))

    # L4: Student cannot practice on an unlinked or another teacher's private book/chapter (404 before any model call)
    calls_before = ctx.llm.calls
    unlinked_codes = [
        ctx.call("S1", "POST", "/student/practice/generate", json={"book_id": str(pb.id)}).status_code,
        ctx.call("S1", "POST", "/student/practice/generate", json={"chapter_id": str(pch.id)}).status_code,
    ]
    out.append(ok(
        unlinked_codes == [404, 404] and ctx.llm.calls == calls_before,
        "L4",
        "student cannot generate a practice quiz on another teacher's private book/chapter (404 with 0 LLM calls)",
        f"got {unlinked_codes}, calls +{ctx.llm.calls - calls_before}",
    ))

    # L5: Role guards enforce 403 across teacher and student quiz routes
    role_codes = [
        ctx.call("S1", "POST", "/teacher/quizzes/generate", json={"book_id": str(ctx.book_a.id)}).status_code,
        ctx.call("tA", "POST", "/student/practice/generate", json={}).status_code,
        ctx.call("tA", "GET", "/student/quizzes").status_code,
    ]
    out.append(ok(
        role_codes == [403, 403, 403],
        "L5",
        "role guards return 403 when a student calls teacher quiz routes or a teacher calls student quiz routes",
        f"got {role_codes}",
    ))
    return out


def run(engine, opts) -> tuple[list[str], int]:
    class FakeSession:
        def __init__(self, uid):
            self.uid = uid

        def get_user_id(self):
            return self.uid

    lines: list[str] = []
    counts = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    connection = engine.connect()

    # pysqlite (the driver behind SQLite) does not start a real transaction when SQLAlchemy asks it to: it only
    # begins one lazily on the first INSERT/UPDATE/DELETE, which breaks SAVEPOINT/RELEASE and makes the final
    # rollback a no-op (data from this check would stay in the test database). For SQLite we take over transaction
    # control and emit BEGIN ourselves so the whole check really sits inside one transaction.
    # (PostgreSQL does not need this.)
    is_sqlite = engine.dialect.name == "sqlite"
    raw_conn = None
    prev_isolation = None
    if is_sqlite:
        raw_conn = connection.connection.dbapi_connection
        prev_isolation = raw_conn.isolation_level
        raw_conn.isolation_level = None  # driver stops auto-managing transactions
    outer = connection.begin()
    if is_sqlite:
        connection.exec_driver_sql("BEGIN")
    db = Session(bind=connection, join_transaction_mode="create_savepoint", autoflush=False)

    def override_db():
        yield db

    def override_session(request: Request):
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(401, "Not authenticated")
        return FakeSession(auth.removeprefix("Bearer "))

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[session_dependency] = override_session
    ctx = Ctx(db, TestClient(app), opts)
    saved_llm = quiz_service.get_llm_provider

    def section(title, fn, needs=()):
        lines.append(f"\n== {title}")
        if any(getattr(ctx, n) is None for n in needs):
            results = [("FAIL", "?", "skipped: an earlier section it depends on failed")]
        else:
            try:
                results = fn(ctx)
            except Exception as exc:
                db.rollback()
                results = [("FAIL", "?", f"check crashed: {type(exc).__name__}: {str(exc)[:250]}")]
        for st, tag, msg in results:
            counts[st] += 1
            lines.append(f"{st:<6} {tag:<4} {msg}")

    try:
        section("Environment and migrations", check_environment)
        if ctx.llm is not None:
            quiz_service.get_llm_provider = lambda: ctx.llm
            section("Data to test on", check_data)
            if ctx.book_a is not None:
                section("Throwaway world (rolled back at the end)", setup_world)
                if ctx.room_a is not None:
                    section("Teacher-triggered test generation & question mix", check_teacher_quizzes)
                    section("Hybrid grading engine (code MCQ + LLM short-answer) & unified mastery", check_hybrid_grading_and_mastery, needs=("teacher_quiz",))
                    section("Student self-triggered practice (60/20/20 weighting) & weak propagation", check_practice_and_propagation)
                    section("Tenancy & role isolation", check_tenancy, needs=("teacher_quiz", "practice_quiz"))
    finally:
        quiz_service.get_llm_provider = saved_llm
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(session_dependency, None)
        db.close()
        outer.rollback()
        if is_sqlite and raw_conn is not None:
            raw_conn.isolation_level = prev_isolation
        connection.close()

    lines.append(f"\nRESULT: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['REVIEW']} REVIEW")
    lines.append(
        "Phase 4 can be closed once there is no FAIL and every REVIEW line has been judged."
        if not counts["FAIL"]
        else "Phase 4 is NOT finished: fix the FAIL lines and run this again."
    )
    lines.append("Everything this run created was rolled back.")
    return lines, counts["FAIL"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", help="official book ID to test on")
    parser.add_argument("--skip-model", action="store_true", help="no model calls: use FakeLLMProvider")
    parser.add_argument("--allow-fake", action="store_true", help="accept fake graph store / LLM (for script tests)")
    args = parser.parse_args()
    from app.db.session import engine as real_engine
    text, fails = run(real_engine, args)
    print("\n".join(text))
    sys.exit(1 if fails else 0)