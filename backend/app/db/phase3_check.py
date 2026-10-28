"""Phase 3 exit check: one command that tests every Phase 3 piece on the REAL database, with the REAL embedding service,
Memgraph and model, and prints PASS / FAIL / REVIEW (the way `phase2_check` does).

    python -m app.db.phase3_check                       # everything (about 8 model calls and 60 embedding calls)
    python -m app.db.phase3_check --skip-model          # no model calls: the Tutor and the check questions are placeholders
    python -m app.db.phase3_check --book <id> --other-book <id>    # choose the two official books

What it does: it makes a throwaway world (two teachers, three students, rooms, one private book) and then drives the REAL
routes (assignments, doubts, checks, mastery) as those users against your real official books. EVERYTHING IS ROLLED BACK at
the end: nothing is kept, and nothing is written to Memgraph (retrieval only reads it). A small cost is real: embedding
calls for the doubts and, unless --skip-model, about eight model calls (1 Tutor answer, 3 checks of 2 questions).

PASS   = verified by a rule.
FAIL   = a rule was broken (a leak, a wrong grade, a missing reason, a wrong status...): must be fixed, the line says what.
REVIEW = a person has to judge the printed lines (the Tutor's answer against its pages, the exercise concepts proposed, the
         flags a weak concept raised, any score that is a measurement and not a rule). A measured rate (R1, R2, R3) FAILS only far below what the retrieval probe measured, and is REVIEW in between.
Phase 3 is finished when there is no FAIL and every REVIEW line was judged.

Students are linked to ONE official book (A). A second official book of another subject (B) supplies the doubts that A does
not cover: that is the 'a question from another school subject' case the retrieval probe never tested."""
import argparse
import sys
import uuid
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.assessment import mastery
from app.assignments.scope import chapter_concepts, subject_concepts
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.phase2_check import check_migrations
from app.doubts.retrieval import GROUNDED, NOT_IN_BOOK, OUTSIDE, UNAVAILABLE, Scope, retrieve
from app.embeddings import EmbeddingError
from app.graph_store.base import GraphStoreError
from app.models import (
    Assignment, AssignmentCheck, Book, Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, Doubt, MasteryEvent, Page, Role,
    User,
)

Result = tuple[str, str, str]  # (PASS | FAIL | REVIEW, id, message)
OFF_TOPIC = [
    "who won the cricket world cup in 2011", "how does GST work on restaurant bills", "best way to cook fluffy biryani",
    "what is the capital of Australia", "how do I get better at playing the guitar",
]
FORBIDDEN_BEFORE_SUBMIT = ("correct_index", "explanation", "chosen_index", "correct")


# ---- small helpers ----------------------------------------------------------------------------------------------

def ok(passed: bool, tag: str, good: str, bad: str | None = None) -> Result:
    return ("PASS", tag, good) if passed else ("FAIL", tag, bad or good)


def graded(share: float, pass_at: float, review_at: float, tag: str, text: str, detail: str, fake: bool) -> Result:
    """A MEASURED rate: PASS at the level the retrieval probe measured, REVIEW in between, FAIL only far below it
    (a regression, e.g. a missing index). With placeholder vectors (--allow-fake) it can never be more than REVIEW."""
    if share >= pass_at:
        return ("PASS", tag, text)
    return ("REVIEW" if fake or share >= review_at else "FAIL", tag, f"{text}{detail}")


def spread(items: list, n: int) -> list:
    """n items spread evenly through the list (not just its start)."""
    if len(items) <= n:
        return list(items)
    return [items[int((i + 0.5) * len(items) / n)] for i in range(n)]


def label(book: Book) -> str:
    return f"{book.publisher} {book.class_name} {book.subject}"


class CountingLLM:
    """Wraps the model so the check can prove the Tutor / question writer is NOT called when it must not be."""

    def __init__(self, inner):
        self.inner, self.calls = inner, 0
        self.model_name = getattr(inner, "model_name", "")

    def complete_json(self, system, user):
        self.calls += 1
        return self.inner.complete_json(system, user)


class FailingEmbedder:
    def embed(self, texts):
        raise EmbeddingError("simulated outage")


class FailingStore:
    def __init__(self, inner):
        self.inner = inner

    def search_concepts(self, *a, **k):
        raise GraphStoreError("simulated outage")

    search_pages = search_concepts


class Ctx:
    def __init__(self, db: Session, client, opts):
        self.db, self.client, self.opts = db, client, opts
        self.users: dict[str, User] = {}
        self.headers: dict[str, dict] = {}
        self.llm: CountingLLM | None = None
        self.embedder = self.store = None
        self.book_a: Book | None = None
        self.book_b: Book | None = None
        self.chapters_a: list[Chapter] = []   # usable chapters of A, in book order
        self.chapters_b: list[Chapter] = []
        self.room_a = self.room_b = None
        self.private: dict = {}
        self.seen: list[tuple] = []           # (RetrievalResult, allowed book ids) for the leak rule
        self.assignments: dict[str, dict] = {}
        self.refused_off_topic: str | None = None
        self.last_doubt = self.last_check = None

    def call(self, who: str, method: str, path: str, **kw):
        headers = self.headers.get(who, {}) if who else {}
        res = self.client.request(method, path, headers=headers, **kw)
        self.db.expire_all()  # the routes ran on this very session; look at the database as it now is
        return res

    def concept_ids(self, chapter: Chapter) -> list[uuid.UUID]:
        return [c.id for c in chapter_concepts(self.db, chapter.id)]

    def doubt_events(self, student: User) -> int:
        return self.db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.student_id == student.id, MasteryEvent.kind == "doubt"))

    def retrieve(self, text: str, book_ids, scope: Scope | None = None, embedder=None, store=None):
        r = retrieve(self.db, text, embedder=embedder or self.embedder, store=store or self.store, book_ids=book_ids, scope=scope)
        self.seen.append((r, {str(b) for b in book_ids}))
        return r


def _name(c: Concept) -> str:
    return f"{c.name!r}"


# ---- 1. environment and the data to test on --------------------------------------------------------------------

def check_environment(ctx: Ctx) -> list[Result]:
    o = ctx.opts
    out = check_migrations(ctx.db)
    problems = []
    if settings.embedding_provider.lower() != "openai_compat" and not o.allow_fake:
        problems.append(f"EMBEDDING_PROVIDER is '{settings.embedding_provider}' (need openai_compat: doubts are searched with real vectors)")
    if settings.graph_store_provider.lower() != "memgraph" and not o.allow_fake:
        problems.append(f"GRAPH_STORE_PROVIDER is '{settings.graph_store_provider}' (need memgraph)")
    if settings.llm_provider.lower() != "openai_compat" and not (o.skip_model or o.allow_fake):
        problems.append(f"LLM_PROVIDER is '{settings.llm_provider}' (need openai_compat, or run with --skip-model)")
    if problems:
        return out + [("FAIL", "E1", "; ".join(problems) + ". Fix backend/.env and run again")]
    from app.embeddings import get_embedding_provider
    from app.graph_store import get_graph_store
    from app.llm import get_llm_provider
    from app.llm.fake_provider import FakeLLMProvider
    try:
        ctx.embedder, ctx.store = get_embedding_provider(), get_graph_store()
        inner = FakeLLMProvider() if o.skip_model else get_llm_provider()
        ctx.llm = CountingLLM(inner)
        stats = ctx.store.stats()
    except Exception as exc:
        return out + [("FAIL", "E1", f"providers could not start: {type(exc).__name__}: {str(exc)[:200]}")]
    out.append(("PASS", "E1", f"embedding provider {settings.embedding_provider}, graph store {settings.graph_store_provider} ({stats}), "
                              f"model {'PLACEHOLDER (--skip-model)' if o.skip_model else ctx.llm.model_name or settings.llm_model}"))
    if o.skip_model:
        out.append(("REVIEW", "E2", "--skip-model: the Tutor answer and the check questions are placeholders, so their QUALITY was not judged; run without it"))
    return out


def usable_chapters(db: Session, book: Book) -> list[Chapter]:
    """READY chapters whose search copy is complete and that have concepts."""
    found = []
    chapters = db.scalars(select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num))
    for c in chapters:
        if c.embedding_status == "done" and c.graph_sync_status == "done" and chapter_concepts(db, c.id):
            found.append(c)
    return found


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
    out = [("PASS", "D1", f"book A = {label(a)} (id {a.id}): {len(ctx.chapters_a)} usable chapter(s)")]
    if o.other_book:
        b = by_id.get(uuid.UUID(o.other_book))
        if b is None or b.id not in usable:
            return out + [("FAIL", "D2", f"--other-book {o.other_book} is not an official book with usable chapters")]
    else:
        others = [by_id[k] for k in usable if k != a.id and (by_id[k].subject or "").strip().lower() != (a.subject or "").strip().lower()]
        b = max(others, key=lambda x: len(usable[x.id])) if others else None
    if b is None:
        out.append(("REVIEW", "D2", "no official book of ANOTHER subject with usable chapters: the 'other school subject is not in the book' and cross-book "
                                    "leak checks were skipped (ingest a second subject, e.g. Science next to Maths)"))
    else:
        ctx.book_b, ctx.chapters_b = b, usable[b.id]
        out.append(("PASS", "D2", f"book B = {label(b)} (id {b.id}): {len(ctx.chapters_b)} usable chapter(s)"))
    if len(ctx.chapters_a) < 2:
        out.append(("REVIEW", "D3", "book A has only one usable chapter: the 'asked inside the wrong chapter' checks were skipped"))
    return out


# ---- 2. the throwaway world ------------------------------------------------------------------------------------

def make_user(db: Session, role: Role, tag: str) -> User:
    t = uuid.uuid4().hex[:8]
    u = User(supertokens_user_id=f"p3chk-{tag}-{t}", name=f"phase3 check {tag}", username=f"p3{tag}{t}"[:30], phone="0" + t, role=role,
             link_code=t.upper() if role == Role.student else None)
    db.add(u)
    db.flush()
    return u


def setup_world(ctx: Ctx) -> list[Result]:
    db, a = ctx.db, ctx.book_a
    for key, role in (("tA", Role.teacher), ("tB", Role.teacher), ("S1", Role.student), ("S2", Role.student), ("S3", Role.student)):
        u = make_user(db, role, key)
        ctx.users[key], ctx.headers[key] = u, {"Authorization": f"Bearer {u.supertokens_user_id}"}
    # a private book of teacher B (no vectors, so it can only ever show up through a tenancy hole)
    pb = Book(board="X", class_name="9", subject=a.subject, publisher="phase3 check", is_reference=False, owner_teacher_id=ctx.users["tB"].id)
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
    out: list[Result] = []
    room = ctx.call("tA", "POST", "/teacher/rooms", json={"name": "phase3 check A", "room_type": "single_class"})
    room_b = ctx.call("tB", "POST", "/teacher/rooms", json={"name": "phase3 check B", "room_type": "single_class"})
    good = room.status_code == 201 and room_b.status_code == 201
    out.append(ok(good, "W1", "two teachers each made a room", f"room creation failed: {room.status_code} {room.text[:150]} / {room_b.status_code}"))
    if not good:
        return out
    ctx.room_a, ctx.room_b = room.json(), room_b.json()
    # Joining now creates a pending request (202); room access starts only after the owning
    # teacher approves it. Keep this exit check representative of the real workflow.
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
    good = joins == [202, 202, 202] and approvals == [200, 200, 200] and link == 200
    out.append(ok(good, "W2",
                  "S1 and S3 requested and were approved for teacher A's room, S2 for teacher B's; only S1 linked book A",
                  f"joining/approval/linking failed: joins {joins}, approvals {approvals}, link {link}"))
    return out


# ---- 3. assignments --------------------------------------------------------------------------------------------

def _assign(ctx: Ctx, **body):
    return ctx.call("tA", "POST", "/teacher/assignments", json=body)


def check_assignments(ctx: Ctx) -> list[Result]:
    db, a, out = ctx.db, ctx.book_a, []
    ch1 = ctx.chapters_a[0]
    ids1 = ctx.concept_ids(ch1)
    room = ctx.room_a["id"]
    soon, later = (date.today() + timedelta(days=1)).isoformat(), (date.today() + timedelta(days=3)).isoformat()

    r = _assign(ctx, level="chapter", book_id=str(a.id), chapter_id=str(ch1.id), room_id=room, due_date=later)
    body = r.json() if r.status_code == 201 else {}
    ctx.assignments["chapter"] = body
    out.append(ok(r.status_code == 201 and [c["id"] for c in body["concepts"]] == [str(i) for i in ids1], "A1",
                  f"chapter level '{ch1.title}': stored list = the chapter's {len(ids1)} canonical concepts, in book order",
                  f"chapter level: {r.status_code} {r.text[:200]}"))

    r = _assign(ctx, level="subject", book_id=str(a.id), room_id=room)
    body = r.json() if r.status_code == 201 else {}
    ctx.assignments["subject"] = body
    expected = {str(c.id) for c in subject_concepts(db, [a.id], a.subject or "")}
    out.append(ok(r.status_code == 201 and {c["id"] for c in body["concepts"]} == expected and expected, "A2",
                  f"subject level: stored list = every canonical concept of the ready chapters ({len(expected)})",
                  f"subject level: {r.status_code}, got {len(body.get('concepts', []))} concepts, expected {len(expected)}"))

    picks = [ids1[-1], ids1[0], ids1[-1]] if len(ids1) > 1 else [ids1[0]]
    r = _assign(ctx, level="concept", book_id=str(a.id), concept_ids=[str(p) for p in picks], room_id=room, due_date=soon)
    body = r.json() if r.status_code == 201 else {}
    ctx.assignments["concept"] = body
    want = [str(p) for p in dict.fromkeys(picks)]
    out.append(ok(r.status_code == 201 and [c["id"] for c in body["concepts"]] == want, "A3",
                  "concept level: the picked concepts, in the picked order, a duplicate dropped", f"concept level: {r.status_code} {r.text[:200]}"))

    # exercise level: the proposal writes nothing, the teacher's confirmed list is what is stored
    ex = next((c for c in ctx.chapters_a if db.scalar(select(func.count()).select_from(Page).where(Page.chapter_id == c.id, Page.page_kind == "exercise"))), None)
    if ex is None:
        out.append(("REVIEW", "A4", "no chapter of book A has a page labelled 'exercise': the exercise level was not tried on real data"))
    else:
        before = db.scalar(select(func.count()).select_from(Assignment))
        p = ctx.call("tA", "POST", "/teacher/assignments/exercise-proposal", json={"book_id": str(a.id), "chapter_id": str(ex.id)})
        prop = p.json() if p.status_code == 200 else {}
        after = db.scalar(select(func.count()).select_from(Assignment))
        out.append(ok(p.status_code == 200 and prop.get("status") == "ok" and prop["proposed"] and before == after, "A4",
                      f"exercise proposal for '{ex.title}': {len(prop.get('proposed', []))} concept(s) proposed from pages {prop.get('exercise_pages')}, nothing written",
                      f"exercise proposal: {p.status_code} {p.text[:200]} (assignments before {before}, after {after})"))
        if prop.get("proposed"):
            confirmed = [x["concept_id"] for x in prop["proposed"]][:-1] or [prop["proposed"][0]["concept_id"]]  # the teacher dropped the last one
            r = _assign(ctx, level="exercise", book_id=str(a.id), chapter_id=str(ex.id), concept_ids=confirmed, page_numbers=prop["exercise_pages"], room_id=room)
            body = r.json() if r.status_code == 201 else {}
            ctx.assignments["exercise"] = body
            out.append(ok(r.status_code == 201 and [c["id"] for c in body["concepts"]] == confirmed and body["exercise_pages"] == prop["exercise_pages"], "A5",
                          f"exercise level: stored the {len(confirmed)} concept(s) the teacher CONFIRMED (one proposed concept was dropped) and the pages",
                          f"exercise level: {r.status_code} {r.text[:200]}"))
            out.append(("REVIEW", "A6", f"exercise proposal to judge ('{ex.title}', pages {prop['exercise_pages']}): "
                                        + "; ".join(f"{x['name']} ({x['similarity']}, p{x['pages']})" for x in prop["proposed"])))

    # a concept of ANOTHER book (or another teacher's private book) is refused, never silently dropped
    foreign = (chapter_concepts(db, ctx.chapters_b[0].id)[0] if ctx.book_b else ctx.private["concept"])
    r = _assign(ctx, level="concept", book_id=str(a.id), concept_ids=[str(foreign.id)], room_id=room)
    out.append(ok(r.status_code == 404, "A7", "a concept that belongs to another book is a 404, not silently dropped", f"foreign concept: got {r.status_code}, expected 404"))
    both = _assign(ctx, level="chapter", book_id=str(a.id), chapter_id=str(ch1.id), room_id=room, student_id=str(ctx.users["S1"].id))
    neither = _assign(ctx, level="chapter", book_id=str(a.id), chapter_id=str(ch1.id))
    out.append(ok(both.status_code == 422 and neither.status_code == 422, "A8", "an assignment goes to a room OR a student, never both, never neither",
                  f"room+student gave {both.status_code}, neither gave {neither.status_code} (expected 422)"))

    # one assignment for S1 alone, then Today's Work: only S1 sees them, soonest due date first
    r = _assign(ctx, level="chapter", book_id=str(a.id), chapter_id=str(ch1.id), student_id=str(ctx.users["S1"].id), title="phase3 check: only S1")
    ctx.assignments["solo"] = r.json() if r.status_code == 201 else {}
    mine = ctx.call("S1", "GET", "/student/assignments").json()
    made = {x["id"]: x for x in ctx.assignments.values() if x}
    got = [x["id"] for x in mine if x["id"] in made]
    order = sorted(got, key=lambda i: (made[i].get("due_date") is None, made[i].get("due_date") or "9999"))
    out.append(ok(set(got) == set(made) and got == order, "A9",
                  f"S1's Today's Work shows all {len(made)} assignments (room and personal), soonest due date first",
                  f"S1 sees {len(got)} of {len(made)} assignments, order correct: {got == order}"))
    s3 = [x["id"] for x in ctx.call("S3", "GET", "/student/assignments").json() if x["id"] in made]
    s2 = [x["id"] for x in ctx.call("S2", "GET", "/student/assignments").json() if x["id"] in made]
    out.append(ok(not s3 and not s2, "A10",
                  "S3 (same room, book not linked) and S2 (another teacher's room) see none of them",
                  f"S3 sees {len(s3)} and S2 sees {len(s2)} of S1's assignments"))
    return out


# ---- 4. retrieval statuses (real embeddings + Memgraph) ---------------------------------------------------------

def _sample(ctx: Ctx, chapters: list[Chapter], n: int) -> list[tuple[Concept, Chapter]]:
    pairs = [(c, ch) for ch in chapters for c in chapter_concepts(ctx.db, ch.id) if (c.description or "").strip()]
    return spread(pairs, n)


def _doubt_text(c: Concept) -> str:
    return f"Can you explain {c.name} to me?"


def check_retrieval(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    a_ids = [ctx.book_a.id]
    samples = _sample(ctx, ctx.chapters_a, 6)

    inside, page_hits, misses = 0, 0, []
    for c, ch in samples:
        r = ctx.retrieve(_doubt_text(c), a_ids, Scope(chapter_ids={str(ch.id)}))
        if r.status == GROUNDED:
            inside += 1
            page_hits += any(p.page_id == str(c.page_id) for p in r.pages)
        else:
            misses.append(f"{c.name!r} -> {r.status} ({r.confidence:.2f})")
    fake = bool(ctx.opts.allow_fake)
    out.append(graded(inside / len(samples), 1.0, 0.6, "R1", f"{inside}/{len(samples)} doubts about a chapter's own concepts are grounded when asked inside that chapter "
                      f"(the concept's page was among the pages returned for {page_hits})", " -- not grounded: " + "; ".join(misses), fake))

    if len(ctx.chapters_a) >= 2:
        outside, wrong = 0, []
        for c, ch in samples:
            other = next(x for x in ctx.chapters_a if x.id != ch.id)
            r = ctx.retrieve(_doubt_text(c), a_ids, Scope(chapter_ids={str(other.id)}))
            if r.status == OUTSIDE:
                outside += 1
            else:
                wrong.append(f"{c.name!r} asked in '{other.title}' -> {r.status} ({r.confidence:.2f})")
        share = outside / len(samples)
        out.append(graded(share, 0.75, 0.5, "R2", f"{outside}/{len(samples)} doubts asked inside the WRONG chapter came back outside_assignment (PASS from 75%, the probe measured 100%)",
                          " -- others: " + "; ".join(wrong), fake))
        if wrong and share >= 0.75:
            out.append(("REVIEW", "R2", "not outside_assignment (the same idea may really recur there): " + "; ".join(wrong)))

    wrong = []
    for t in OFF_TOPIC:
        r = ctx.retrieve(t, a_ids)
        if r.status != NOT_IN_BOOK:
            wrong.append(f"{t!r} -> {r.status} ({r.confidence:.2f}, cut-off {r.threshold})")
        elif ctx.refused_off_topic is None:
            ctx.refused_off_topic = t
    out.append(graded(1 - len(wrong) / len(OFF_TOPIC), 1.0, 0.8, "R3", f"all {len(OFF_TOPIC)} off-topic questions are not_in_book (the probe's highest off-topic score was 0.23)",
                      " -- NOT refused: " + "; ".join(wrong), fake))

    if ctx.book_b is not None:
        theirs = _sample(ctx, ctx.chapters_b, 6)
        got = [(c, ctx.retrieve(_doubt_text(c), a_ids)) for c, _ in theirs]
        refused = sum(r.status == NOT_IN_BOOK for _, r in got)
        share = refused / len(got)
        out.append(("PASS" if share >= 0.8 else "REVIEW", "R4",
                    f"{refused}/{len(got)} doubts from {label(ctx.book_b)} asked by a student who only linked {label(ctx.book_a)} came back not_in_book"
                    + ("" if share >= 0.8 else " (below 80%: judge below, this is the 'other school subject' gap the cut-off was never measured on)")))
        for c, r in got:
            if r.status != NOT_IN_BOOK:
                out.append(("REVIEW", "R4", f"{c.name!r} (from the other book) -> {r.status}, best similarity {r.confidence:.2f}, "
                                            f"matched {[x.name for x in r.concepts[:3]]}"))

    unavailable_embed = ctx.retrieve("what is a coordinate", a_ids, embedder=FailingEmbedder())
    unavailable_store = ctx.retrieve("what is a coordinate", a_ids, store=FailingStore(ctx.store))
    out.append(ok(unavailable_embed.status == unavailable_store.status == UNAVAILABLE and not unavailable_embed.pages and not unavailable_store.pages, "R6",
                  "an embedding outage and a Memgraph outage both give 'unavailable', with nothing returned (never a guess)",
                  f"outage gave {unavailable_embed.status} / {unavailable_store.status}"))
    none_linked = ctx.retrieve(_doubt_text(samples[0][0]), [])
    out.append(ok(none_linked.status == NOT_IN_BOOK and not none_linked.pages and not none_linked.concepts, "R7",
                  "a student with no linked book gets not_in_book and nothing back (an empty list never means 'search everything')",
                  f"no linked books gave {none_linked.status} with {len(none_linked.pages)} pages"))
    return out


def check_no_retrieval_leak(ctx: Ctx) -> list[Result]:
    bad = []
    for r, allowed in ctx.seen:
        bad += [f"page {p.page_number} of book {p.book_id}" for p in r.pages if p.book_id not in allowed]
        bad += [f"concept {h.name!r} of book {h.book_id}" for h in r.concepts + r.elsewhere if h.book_id not in allowed]
    return [ok(not bad, "R9", f"across all {len(ctx.seen)} searches made by this check, every page and concept came from a book the student had linked",
               "LEAK: results from books the student did not link: " + "; ".join(bad[:5]))]


# ---- 5. doubts through the real routes, and the Tutor ------------------------------------------------------------

def check_doubts(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1, s3 = ctx.users["S1"], ctx.users["S3"]
    chapter_a = ctx.assignments["chapter"]
    ch1 = ctx.chapters_a[0]
    c1 = next(c for c in chapter_concepts(db, ch1.id) if (c.description or "").strip())
    llm = ctx.llm

    made: list[str] = []  # the doubts S1 asked through the route in this run

    def ask(who, **body):
        limiter.reset()
        res = ctx.call(who, "POST", "/student/doubts", json=body)
        if who == "S1" and res.status_code == 200:
            made.append(res.json()["id"])
        return res

    # T1: in-scope doubt on the chapter assignment -> grounded, explained, sources are real pages
    events_before, calls_before = ctx.doubt_events(s1), llm.calls
    r = ask("S1", text=_doubt_text(c1), assignment_id=chapter_a["id"])
    b = r.json() if r.status_code == 200 else {}
    shown = {p["page_number"] for p in b.get("pages", [])}
    good_t1 = r.status_code == 200 and b.get("status") == GROUNDED and bool(b.get("pages")) and bool(b.get("concepts"))
    out.append(ok(good_t1, "T1",
                  f"doubt on the chapter assignment is grounded (similarity {b.get('confidence')}, {len(b.get('pages', []))} page(s), concept {(b.get('concepts') or [{}])[0].get('name')!r})",
                  f"in-scope doubt: {r.status_code} status {b.get('status')}, confidence {b.get('confidence')}: {r.text[:200]}"))
    if b.get("status") == GROUNDED:
        if b["answer_status"] == "answered":
            sources = [s["page_number"] for s in b["sources"]]
            out.append(ok(bool(sources) and set(sources) <= shown and llm.calls > calls_before, "T2",
                          f"the Tutor answered and named only pages it was shown (pages {sources} of {sorted(shown)})",
                          f"the Tutor's sources {sources} are not all among the shown pages {sorted(shown)}"))
            out.append(("REVIEW", "T3", f"Tutor answer to judge against its pages (needs_review={b['needs_review']}, note={b['note']!r}): {b['answer']!r} "
                                        f"| refresher: {b['refresher']!r} | pages shown: " + "; ".join(f"p{p['page_number']} ({p['similarity']}): {p['excerpt'][:160]!r}" for p in b["pages"][:3])))
        else:
            out.append(("REVIEW", "T2", f"grounded but the Tutor gave answer_status '{b['answer_status']}' ({b['message']}): the pages are still shown; judge whether the model or the prompt is at fault"))
        out.append(ok(ctx.doubt_events(s1) == events_before + 1 and db.get(Doubt, uuid.UUID(b["id"])).concept_id is not None, "T4",
                      "the doubt row was stored with its concept and one 'doubt' mastery event was written", "doubt row or its mastery event is missing"))
        ctx.last_doubt = b

    # T5: a doubt about another chapter -> outside_assignment, the Tutor is never called, nothing logged
    if len(ctx.chapters_a) >= 2:
        pick = None
        for c, ch in _sample(ctx, ctx.chapters_a[1:], 6):
            probe = ctx.retrieve(_doubt_text(c), [ctx.book_a.id], Scope(chapter_ids={str(ch1.id)}))
            if probe.status == OUTSIDE:
                pick = c
                break
        if pick is None:
            out.append(("REVIEW", "T5", "no concept of another chapter came back outside_assignment on the chapter assignment (see R2): the route case was not shown"))
        else:
            calls, events = llm.calls, ctx.doubt_events(s1)
            r = ask("S1", text=_doubt_text(pick), assignment_id=chapter_a["id"])
            b = r.json() if r.status_code == 200 else {}
            out.append(ok(b.get("status") == OUTSIDE and b["answer_status"] == "none" and b["answer"] is None and b["elsewhere"] and "Ask a Doubt" in b["message"]
                          and llm.calls == calls and ctx.doubt_events(s1) == events, "T5",
                          f"a doubt about another chapter ({pick.name!r}) is outside_assignment: points to Ask a Doubt, lists where the book covers it, no Tutor call, no doubt event",
                          f"outside_assignment case: {r.status_code} status {b.get('status')}, answer_status {b.get('answer_status')}, "
                          f"model calls +{llm.calls - calls}, events +{ctx.doubt_events(s1) - events}"))

    # T6: not in the book -> chapter-request path, no Tutor call, nothing logged
    off = ctx.refused_off_topic
    if off is None:
        out.append(("REVIEW", "T6", "no off-topic question was refused in R3, so the not_in_book route case was not shown"))
    else:
        calls, events = llm.calls, ctx.doubt_events(s1)
        r = ask("S1", text=off, assignment_id=chapter_a["id"])
        b = r.json() if r.status_code == 200 else {}
        out.append(ok(b.get("status") == NOT_IN_BOOK and b["request_chapter"]["path"] == f"/student/books/{ctx.book_a.id}/chapter-requests"
                      and b["answer"] is None and llm.calls == calls and ctx.doubt_events(s1) == events, "T6",
                      "an off-topic doubt is not_in_book: offers the chapter-request path, no Tutor call, no doubt event",
                      f"not_in_book case: {r.status_code} {r.text[:250]}"))

    # T7: a student with no linked book
    r = ask("S2", text=_doubt_text(c1))
    b = r.json() if r.status_code == 200 else {}
    out.append(ok(b.get("status") == NOT_IN_BOOK and not b["pages"] and not b["concepts"] and b["answer"] is None, "T7",
                  "S2 (nothing linked) asking about book A's content gets not_in_book and no text from it", f"S2's doubt: {r.status_code} {r.text[:250]}"))

    # T8: standalone chapter doubts and their guards
    r = ask("S1", text=_doubt_text(c1), chapter_id=str(ch1.id))
    out.append(ok(r.status_code == 200 and r.json()["status"] == GROUNDED and r.json()["chapter_id"] == str(ch1.id), "T8",
                  "standalone 'Ask a Doubt' narrowed to a chapter is grounded", f"chapter doubt: {r.status_code} {r.text[:200]}"))
    both = ask("S1", text="x y z", chapter_id=str(ch1.id), assignment_id=chapter_a["id"])
    foreign_ch = ask("S1", text=_doubt_text(c1), chapter_id=str(ctx.private["chapter"].id))
    foreign_as = ask("S3", text=_doubt_text(c1), assignment_id=chapter_a["id"])
    saved = db.scalar(select(func.count()).select_from(Doubt).where(Doubt.student_id.in_([s3.id])))
    out.append(ok(both.status_code == 422 and foreign_ch.status_code == 404 and foreign_as.status_code == 404 and saved == 0, "T9",
                  "chapter + assignment together is 422; another teacher's chapter is 404; S3 (book not linked) using S1's assignment is 404 and saves nothing",
                  f"guards gave {both.status_code} / {foreign_ch.status_code} / {foreign_as.status_code} (expected 422 / 404 / 404), S3 doubts saved: {saved}"))

    # T10: the photo route refuses a bad file BEFORE any OCR call
    pdf = ctx.call("S1", "POST", "/student/doubts/photo", files={"file": ("p.pdf", b"%PDF-1.4 fake", "application/pdf")})
    bad_as = ctx.call("S1", "POST", "/student/doubts/photo", files={"file": ("p.png", b"x", "image/png")}, data={"assignment_id": str(uuid.uuid4())})
    out.append(ok(pdf.status_code == 415 and bad_as.status_code == 404, "T10", "photo route: a PDF is 415 and an unknown assignment is 404, both before any OCR call",
                  f"photo guards gave {pdf.status_code} / {bad_as.status_code} (expected 415 / 404)"))
    out.append(("REVIEW", "T11", "a real photo was not sent through the route (it needs OCR): the real-photo proof is `python -m app.db.try_doubt_photo <photo> --book <id>`, already judged in step 4"))

    # T12: history is the student's own
    h1 = ctx.call("S1", "GET", "/student/doubts").json()
    h2 = ctx.call("S2", "GET", "/student/doubts").json()
    out.append(ok(made and set(made) <= {d["id"] for d in h1} and not {d["id"] for d in h1} & {d["id"] for d in h2}, "T12",
                  f"S1's doubt history holds the {len(made)} doubts S1 asked and shares none with S2's", "doubt history is incomplete or shared between students"))

    # T13: deleting an assignment keeps the doubt history
    solo = ctx.assignments["solo"]
    r = ask("S1", text="zebra quantum jukebox harmonica", assignment_id=solo["id"])
    deleted = ctx.call("tA", "DELETE", f"/teacher/assignments/{solo['id']}")
    kept = db.get(Doubt, uuid.UUID(r.json()["id"])) if r.status_code == 200 else None
    out.append(ok(deleted.status_code == 204 and kept is not None and kept.assignment_id is None, "T13",
                  "deleting an assignment keeps the student's doubt (its assignment becomes none)", f"delete gave {deleted.status_code}, doubt kept: {kept is not None}"))
    ctx.assignments.pop("solo", None)

    # B1: browse lists exactly the linked book's ready chapters
    r = ctx.call("S1", "GET", "/student/doubts/browse")
    books = {bk["id"]: bk for s in r.json() for bk in s["books"]} if r.status_code == 200 else {}
    ready = {str(c.id) for c in db.scalars(select(Chapter).where(Chapter.book_id == ctx.book_a.id, Chapter.status == ChapterStatus.READY))}
    listed = {c["id"] for bk in books.values() for c in bk["chapters"]}
    s2_browse = ctx.call("S2", "GET", "/student/doubts/browse").json()
    out.append(ok(set(books) == {str(ctx.book_a.id)} and listed == ready and s2_browse == [], "B1",
                  f"browse shows only the linked book A with its {len(ready)} ready chapter(s); S2 sees nothing, nobody sees the private book",
                  f"browse listed books {sorted(books)}, chapters match: {listed == ready}, S2 browse: {s2_browse}"))
    return out


# ---- 6. mark complete, the check, grading, mastery, propagation -------------------------------------------------

def _has_path(db: Session, dependent: uuid.UUID, source: uuid.UUID, depth: int) -> bool:
    """Is `source` a prerequisite of `dependent` within `depth` steps? Walked independently of mastery.py, straight on the edge tables."""
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


def _take(ctx: Ctx, concept: Concept, right: bool, tag: str):
    """Assign one concept and mark it complete. -> (assignment json | None, the response, None). `right` is unused: the caller submits."""
    r = _assign(ctx, level="concept", book_id=str(ctx.book_a.id), concept_ids=[str(concept.id)], room_id=ctx.room_a["id"], title=f"phase3 check {tag}")
    if r.status_code != 201:
        return None, r, None
    limiter.reset()
    c = ctx.call("S1", "POST", f"/student/assignments/{r.json()['id']}/complete")
    return r.json(), c, None


def _answers(ctx: Ctx, check_json: dict, right: bool) -> list[dict]:
    from app.models import CheckQuestion
    out = []
    for q in check_json["questions"]:
        if q["status"] != "ready":
            continue
        key = ctx.db.get(CheckQuestion, uuid.UUID(q["id"])).correct_index
        out.append({"question_id": q["id"], "chosen_index": key if right else (key + 1) % 4})
    return out


def _snapshot(ctx: Ctx, student: User):
    return [(e.id, e.kind, e.concept_id, e.score, e.reason) for e in ctx.db.scalars(
        select(MasteryEvent).where(MasteryEvent.student_id == student.id).order_by(MasteryEvent.id))]


def check_checks_and_mastery(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1 = ctx.users["S1"]
    ch1 = ctx.chapters_a[0]
    concepts = chapter_concepts(db, ch1.id)
    depth = settings.propagate_max_depth

    # the weak concept: the one with the FEWEST (but at least one) dependents, so the flags are easy to judge
    counted = [(len(mastery.dependents(db, c.id)), c.name, c) for c in concepts]
    with_deps = sorted([t for t in counted if t[0] >= 1], key=lambda t: (t[0], t[1]))
    if not with_deps:
        return [("REVIEW", "K0", f"no concept of '{ch1.title}' has a dependent in the stored graph: checks and propagation were not exercised")]
    n_deps, _, weak = with_deps[0]
    out.append(("PASS", "K0", f"weak concept for the test: {weak.name!r} ({n_deps} dependent(s) within {depth} step(s))"))

    # K1/K2: mark complete -> questions, no key
    assignment, c, _ = _take(ctx, weak, False, "weak")
    if assignment is None:
        return out + [("FAIL", "K1", f"could not assign the weak concept: {c.status_code} {c.text[:200]}")]
    check = c.json() if c.status_code == 200 else {}
    qs = check.get("questions", [])
    states = [q["status"] for q in qs]
    out.append(ok(c.status_code == 200 and len(qs) == settings.check_min_questions and all(s == "ready" for s in states) and check["can_submit"], "K1",
                  f"mark complete on a one-concept assignment opens a check of {len(qs)} questions (the floor), all written",
                  f"mark complete: {c.status_code}, question states {states} {c.text[:200] if c.status_code != 200 else ''}"))
    if not qs or any(s != "ready" for s in states):
        return out + [("FAIL", "K1", "questions could not be written, so grading and propagation were not exercised: check the model settings and run again")]
    leaked = [(k, q[k]) for q in qs for k in FORBIDDEN_BEFORE_SUBMIT if q.get(k) is not None]
    got = ctx.call("S1", "GET", f"/student/checks/{check['id']}").json()
    leaked += [(k, q[k]) for q in got["questions"] for k in FORBIDDEN_BEFORE_SUBMIT if q.get(k) is not None]
    out.append(ok(not leaked and all(len(q["options"]) == 4 for q in qs), "K2", "before submitting, neither the opened check nor a re-read shows a key, explanation or choice; 4 options each",
                  f"LEAK before submit: {leaked[:3]}"))
    ctx.last_check = check
    out.append(("REVIEW", "K3", "check questions to judge (is each about its concept, exactly one right option, plausible wrong ones): "
                                + " || ".join(f"{q['question']} " + " / ".join(f"{'ABCD'[i]}. {o}" for i, o in enumerate(q['options'])) for q in qs)))

    # K4: resume, no new model calls, no new check; other students cannot touch it
    calls = ctx.llm.calls
    again = ctx.call("S1", "POST", f"/student/assignments/{assignment['id']}/complete").json()
    n_checks = db.scalar(select(func.count()).select_from(AssignmentCheck).where(AssignmentCheck.assignment_id == uuid.UUID(assignment["id"])))
    out.append(ok(again.get("id") == check["id"] and n_checks == 1 and ctx.llm.calls == calls, "K4",
                  "marking complete again resumes the same open check: one check row, no new model call", f"resume gave id {again.get('id')}, {n_checks} check rows, model calls +{ctx.llm.calls - calls}"))
    codes = [ctx.call(who, "GET", f"/student/checks/{check['id']}").status_code for who in ("S2", "S3")]
    codes += [ctx.call("S3", "POST", f"/student/assignments/{assignment['id']}/complete").status_code, ctx.call("S2", "POST", f"/student/checks/{check['id']}/submit", json={"answers": []}).status_code]
    out.append(ok(codes == [404] * 4, "K5", "another student cannot read, open or submit S1's check (404 each time)", f"other students got {codes}"))

    # K6: submit all wrong -> graded by code, key revealed, events written
    submit = ctx.call("S1", "POST", f"/student/checks/{check['id']}/submit", json={"answers": _answers(ctx, check, right=False)})
    res = submit.json() if submit.status_code == 200 else {}
    revealed = res and all(q["correct_index"] is not None and q["correct"] is False and q["explanation"] is not None for q in res["questions"])
    out.append(ok(submit.status_code == 200 and res["status"] == "submitted" and res["score"] == 0.0 and revealed, "K6",
                  "submitting all-wrong answers grades 0.0 by code and only now reveals the key, the explanation and each choice", f"submit: {submit.status_code} {submit.text[:250]}"))
    events = list(db.scalars(select(MasteryEvent).where(MasteryEvent.check_id == uuid.UUID(check["id"])).order_by(MasteryEvent.id)))
    checks_ev = [e for e in events if e.kind == "check"]
    flags = [e for e in events if e.kind == "propagated"]
    out.append(ok(len(checks_ev) == 1 and checks_ev[0].concept_id == weak.id and (checks_ev[0].asked, checks_ev[0].correct, checks_ev[0].score) == (len(qs), 0, 0.0), "K7",
                  f"one 'check' event for {weak.name!r}: {len(qs)} asked, 0 correct, score 0.0 (weak, below {settings.weak_below})",
                  f"check events: {[(e.concept_name, e.asked, e.correct, e.score) for e in checks_ev]}"))
    problems = []
    for e in flags:
        if not e.reason or weak.name not in e.reason or "tested weak" not in e.reason:
            problems.append(f"{e.concept_name!r} reason {e.reason!r}")
        if e.source_concept_id != weak.id or e.score is not None or not _has_path(db, e.concept_id, weak.id, depth):
            problems.append(f"{e.concept_name!r} is not a dependent of {weak.name!r} within {depth} step(s)")
    expected = {d.concept_id for d in mastery.dependents(db, weak.id)}
    out.append(ok(flags and not problems and {e.concept_id for e in flags} == expected and weak.id not in {e.concept_id for e in flags}, "K8",
                  f"{len(flags)} dependent(s) flagged at risk: each has a reason naming {weak.name!r}, no score, and a prerequisite path to it checked straight on the edge tables",
                  f"propagation problems: {problems[:3] or 'flagged ' + str(len(flags)) + ' of ' + str(len(expected))}"))
    out.append(("REVIEW", "K9", f"flags raised by {weak.name!r} testing weak, to judge (do these concepts really need it?): "
                                + "; ".join(f"{e.concept_name}: {e.reason}" for e in flags[:12]) + (f"; ...and {len(flags) - 12} more" if len(flags) > 12 else "")))

    # K10: submitted once only; the log did not move
    count = db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.student_id == s1.id))
    second = ctx.call("S1", "POST", f"/student/checks/{check['id']}/submit", json={"answers": _answers(ctx, check, right=True)})
    out.append(ok(second.status_code == 409 and db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.student_id == s1.id)) == count, "K10",
                  "a second submit is 409 and adds no event", f"second submit gave {second.status_code}"))

    # K11: the student's picture
    m = ctx.call("S1", "GET", "/student/mastery").json()
    by = {x["concept_id"]: x for x in m["concepts"]}
    out.append(ok(by.get(str(weak.id), {}).get("status") == "weak" and all(by.get(str(e.concept_id), {}).get("status") == "at_risk" and by[str(e.concept_id)]["reason"] for e in flags)
                  and m["weak"] == 1 and m["at_risk"] == len(flags), "K11",
                  f"GET /student/mastery: 1 weak, {len(flags)} at risk, each at-risk concept with its reason and no score",
                  f"mastery picture: weak {m['weak']}, at_risk {m['at_risk']}, weak concept status {by.get(str(weak.id), {}).get('status')}"))

    # K12: the next check on a flagged concept clears its flag (and nothing in the log is rewritten)
    first_flag = flags[0]
    dep = db.get(Concept, first_flag.concept_id)
    snap = _snapshot(ctx, s1)
    a2, c2, _ = _take(ctx, dep, True, "clear")
    check2 = c2.json() if c2.status_code == 200 else {}
    if a2 is None or not check2 or any(q["status"] != "ready" for q in check2["questions"]):
        out.append(("FAIL", "K12", f"could not open the second check: {c2.status_code} {c2.text[:200]}"))
    else:
        sub = ctx.call("S1", "POST", f"/student/checks/{check2['id']}/submit", json={"answers": _answers(ctx, check2, right=True)})
        m2 = ctx.call("S1", "GET", "/student/mastery").json()
        by2 = {x["concept_id"]: x for x in m2["concepts"]}
        now = _snapshot(ctx, s1)
        out.append(ok(sub.status_code == 200 and sub.json()["score"] == 1.0 and by2[str(dep.id)]["status"] == "ok" and by2[str(dep.id)]["score"] == 1.0
                      and by2[str(weak.id)]["status"] == "weak", "K12",
                      f"measured all-right on the flagged concept {dep.name!r}: its flag is cleared (status ok, score 1.0) while {weak.name!r} stays weak",
                      f"clear: submit {sub.status_code}, {dep.name!r} is {by2.get(str(dep.id))}"))
        out.append(ok(now[:len(snap)] == snap and len(now) > len(snap), "K13",
                      f"append-only: all {len(snap)} earlier events are unchanged and {len(now) - len(snap)} new one(s) were added", "an earlier mastery event was changed or removed"))

    # K14: a failure while writing the events leaves the check open and the log untouched (one transaction)
    spare = next((c for c in concepts if c.id not in {weak.id, dep.id}), concepts[0])
    a3, c3, _ = _take(ctx, spare, True, "atomic")
    check3 = c3.json() if c3.status_code == 200 else {}
    if a3 is None or not check3 or any(q["status"] != "ready" for q in check3["questions"]):
        out.append(("FAIL", "K14", f"could not open the third check: {c3.status_code} {c3.text[:200]}"))
    else:
        from app.assessment import service as check_service
        row = db.get(AssignmentCheck, uuid.UUID(check3["id"]))
        answers = {q.id: q.correct_index for q in row.questions}
        original, raised = mastery.record_check, False
        mastery.record_check = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("simulated failure while writing the events"))
        try:
            check_service.submit(db, row, answers)
        except RuntimeError:
            raised = True
        finally:
            mastery.record_check = original
        db.expire_all()
        row = db.get(AssignmentCheck, uuid.UUID(check3["id"]))
        n_events = db.scalar(select(func.count()).select_from(MasteryEvent).where(MasteryEvent.check_id == row.id))
        untouched = all(q.chosen_index is None and q.correct is None for q in row.questions)
        out.append(ok(raised and row.status == "open" and row.score is None and n_events == 0 and untouched, "K14",
                      "when writing the mastery events fails, the check stays open, ungraded, with no event (grade and events are ONE transaction)",
                      f"after a simulated failure: raised {raised}, status {row.status}, score {row.score}, events {n_events}, questions untouched {untouched}"))
        sub = ctx.call("S1", "POST", f"/student/checks/{row.id}/submit", json={"answers": _answers(ctx, check3, right=True)})
        out.append(ok(sub.status_code == 200 and sub.json()["status"] == "submitted", "K15", "that check can still be submitted normally afterwards", f"later submit gave {sub.status_code}"))

    # K16: the next check asks weak concepts first when the scope is bigger than the ceiling
    from app.assessment import checks as check_rules
    from app.assessment import service as check_service
    ids = [str(c.id) for c in concepts]
    first = check_service._ask_first(db, s1, [c.id for c in concepts])
    planned = check_rules.plan_check(ids, priority_ids=first)
    out.append(ok(first[:1] == [str(weak.id)] and str(weak.id) in planned and len(planned) == check_rules.question_count(len(ids)), "K16",
                  f"the next whole-chapter check ({len(ids)} concepts -> {len(planned)} questions) asks the weak concept {weak.name!r} first and includes it",
                  f"ask-first order {first[:3]}, weak concept planned: {str(weak.id) in planned}"))

    # K17: the database itself refuses a flag without a reason and a score out of range
    refused = []
    for kw in (dict(kind="propagated", reason=None), dict(kind="check", score=1.5, asked=2, correct=2)):
        nested = db.begin_nested()
        try:
            db.add(MasteryEvent(student_id=s1.id, concept_id=weak.id, concept_name="x", **kw))
            db.flush()
            refused.append(False)
        except IntegrityError:
            refused.append(True)
        finally:
            nested.rollback()
    out.append(ok(all(refused), "K17", "the database refuses a flag with no reason and a score above 1", f"constraints refused: {refused}"))
    return out


# ---- 7. tenancy ------------------------------------------------------------------------------------------------

def check_tenancy(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1 = ctx.users["S1"]
    a = ctx.book_a
    pb, pch, pc = ctx.private["book"], ctx.private["chapter"], ctx.private["concept"]
    chapter_assignment = ctx.assignments["chapter"]

    codes = [ctx.call(who, "GET", f"/student/assignments/{chapter_assignment['id']}").status_code for who in ("S2", "S3")]
    out.append(ok(codes == [404, 404], "L1", "S2 (another teacher's room) and S3 (book not linked) get 404 on S1's assignment", f"got {codes}"))

    codes = [ctx.call("tB", "GET", f"/teacher/assignments/{chapter_assignment['id']}").status_code,
             ctx.call("tB", "DELETE", f"/teacher/assignments/{chapter_assignment['id']}").status_code]
    listed = ctx.call("tB", "GET", "/teacher/assignments").json()
    still = db.get(Assignment, uuid.UUID(chapter_assignment["id"])) is not None
    out.append(ok(codes == [404, 404] and not listed and still, "L2", "teacher B cannot read, delete or even list teacher A's assignments", f"got {codes}, listed {len(listed)}, still exists {still}"))

    body = dict(level="chapter", book_id=str(a.id), chapter_id=str(ctx.chapters_a[0].id))
    to_room = ctx.call("tB", "POST", "/teacher/assignments", json={**body, "room_id": ctx.room_a["id"]}).status_code
    to_student = ctx.call("tB", "POST", "/teacher/assignments", json={**body, "student_id": str(s1.id)}).status_code
    private = ctx.call("tA", "POST", "/teacher/assignments", json={"level": "subject", "book_id": str(pb.id), "room_id": ctx.room_a["id"]}).status_code
    out.append(ok([to_room, to_student, private] == [404, 404, 404], "L3",
                  "a teacher cannot assign to another teacher's room or student, nor from another teacher's private book (404 each)",
                  f"got room {to_room}, student {to_student}, private book {private}"))

    link_s1 = ctx.call("S1", "POST", f"/student/books/{pb.id}/link").status_code
    chapter_s1 = ctx.call("S1", "POST", "/student/doubts", json={"text": "zebra quantum jukebox", "chapter_id": str(pch.id)}).status_code
    concept_s1 = ctx.call("S1", "POST", "/student/doubts", json={"concept_id": str(pc.id)}).status_code
    out.append(ok([link_s1, chapter_s1, concept_s1] == [404, 404, 404], "L4",
                  "S1 cannot link teacher B's private book, nor ask a doubt scoped to its chapter or built from its concept (404 each)",
                  f"got link {link_s1}, chapter {chapter_s1}, concept {concept_s1}"))

    m2 = ctx.call("S2", "GET", "/student/mastery").json()
    m3 = ctx.call("S3", "GET", "/student/mastery").json()
    e2 = ctx.call("S2", "GET", "/student/mastery/events").json()
    out.append(ok(m2["concepts"] == m3["concepts"] == [] and e2 == [], "L5", "S2 and S3 see none of S1's mastery or its events", f"S2 sees {len(m2['concepts'])}, S3 sees {len(m3['concepts'])} concepts"))

    teacher_route = ctx.call("S1", "GET", "/teacher/assignments").status_code
    student_route = ctx.call("tA", "GET", "/student/assignments").status_code
    doubt_route = ctx.call("tA", "POST", "/student/doubts", json={"text": "hello there"}).status_code
    out.append(ok([teacher_route, student_route, doubt_route] == [403, 403, 403], "L6", "a student cannot use teacher routes and a teacher cannot use student routes (403)",
                  f"got {teacher_route} / {student_route} / {doubt_route}"))

    # unlinking removes the book's work and chapters from S1 at once; linking again brings them back
    ctx.call("S1", "DELETE", f"/student/books/{a.id}/link")
    work = [x for x in ctx.call("S1", "GET", "/student/assignments").json()]
    chapter_code = ctx.call("S1", "POST", "/student/doubts", json={"text": "what is this", "chapter_id": str(ctx.chapters_a[0].id)}).status_code
    browse = ctx.call("S1", "GET", "/student/doubts/browse").json()
    ctx.call("S1", "POST", f"/student/books/{a.id}/link")
    back = ctx.call("S1", "GET", "/student/assignments").json()
    out.append(ok(not work and chapter_code == 404 and browse == [] and len(back) >= 1, "L7",
                  "after S1 unlinks book A its Today's Work is empty, its chapters are 404 and browse is empty; linking again brings the work back",
                  f"after unlinking: {len(work)} assignments, chapter {chapter_code}, browse {len(browse)}, after relinking {len(back)}"))
    return out


# ---- run -------------------------------------------------------------------------------------------------------

def run(engine, opts) -> tuple[list[str], int]:
    from fastapi.testclient import TestClient

    from app.auth.dependencies import session_dependency
    from app.db.session import get_db
    from app.main import app
    from fastapi import HTTPException, Request

    class FakeSession:  # stands in for a SuperTokens session: "Authorization: Bearer <supertokens_user_id>"
        def __init__(self, uid):
            self.uid = uid

        def get_user_id(self):
            return self.uid

    lines: list[str] = []
    counts = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    connection = engine.connect()
    outer = connection.begin()
    # Every commit the app makes only releases a savepoint of `outer`, and `outer` is ALWAYS rolled back: nothing is kept.
    db = Session(bind=connection, join_transaction_mode="create_savepoint", autoflush=False)

    def override_db():
        yield db  # one shared session; never closed by a request

    def override_session(request: Request):
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(401, "Not authenticated")
        return FakeSession(auth.removeprefix("Bearer "))

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[session_dependency] = override_session
    ctx = Ctx(db, TestClient(app), opts)
    import app.doubts.service as doubt_service
    import app.assessment.service as check_service
    saved = (doubt_service.get_llm_provider, check_service.get_llm_provider)

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
        for status, tag, message in results:
            counts[status] += 1
            lines.append(f"{status:<6} {tag:<4} {message}")

    try:
        section("Environment and migrations", check_environment, needs=())
        if ctx.llm is not None:
            doubt_service.get_llm_provider = check_service.get_llm_provider = lambda: ctx.llm  # counted, and the placeholder one with --skip-model
            section("Data to test on", check_data)
            if ctx.book_a is not None:
                section("Throwaway world (rolled back at the end)", setup_world)
                if ctx.room_a is not None:
                    section("Assignments: four levels, scope, Today's Work", check_assignments)
                    section("Retrieval statuses on real embeddings and Memgraph", check_retrieval)
                    section("Doubts through the routes, the Tutor, browse", check_doubts)
                    section("Mark complete, the check, grading, mastery, propagation", check_checks_and_mastery)
                    section("Tenancy: no leaks", check_tenancy)
                    section("Search results across the whole run", check_no_retrieval_leak)
    finally:
        doubt_service.get_llm_provider, check_service.get_llm_provider = saved
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(session_dependency, None)
        db.close()
        outer.rollback()  # nothing this script does is ever kept
        connection.close()
    lines.append(f"\nRESULT: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['REVIEW']} REVIEW")
    lines.append("Phase 3 can be closed once there is no FAIL and every REVIEW line has been judged." if not counts["FAIL"]
                 else "Phase 3 is NOT finished: fix the FAIL lines (each says what) and run this again.")
    lines.append("Everything this run created was rolled back.")
    return lines, counts["FAIL"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", help="official book A (the one the test student links)")
    parser.add_argument("--other-book", help="official book B of another subject")
    parser.add_argument("--skip-model", action="store_true", help="no model calls: the Tutor and the check questions are placeholders")
    parser.add_argument("--allow-fake", action="store_true", help="accept fake embeddings / store (only for developing this script)")
    args = parser.parse_args()
    from app.db.session import engine as real_engine
    text, fails = run(real_engine, args)
    print("\n".join(text))
    sys.exit(1 if fails else 0)
