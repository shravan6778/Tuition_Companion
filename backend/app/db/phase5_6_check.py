"""Phase 5 & 6 exit check: one command that tests every Phase 5 & 6 piece on the REAL database, with the REAL model
(gpt-4.1-mini), and prints PASS / FAIL / REVIEW (the way `phase2_check`, `phase3_check`, and `phase4_check` do).

    python -m app.db.phase5_6_check                       # everything (uses real database + gpt-4.1-mini)
    python -m app.db.phase5_6_check --skip-model          # no model calls: Personalization Agent uses FakeLLMProvider
    python -m app.db.phase5_6_check --book <id>           # choose the official book to test on

Everything runs inside one outer transaction that is ALWAYS rolled back at the end: nothing is kept in PostgreSQL
and nothing is written to Memgraph."""
import argparse
import sys
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents import personalization
from app.assessment import mastery
from app.assignments.scope import chapter_concepts
from app.auth.dependencies import session_dependency
from app.core.config import settings
from app.core.ratelimit import limiter
from app.db.phase2_check import check_migrations
from app.db.phase3_check import CountingLLM, label, make_user, ok
from app.db.session import get_db
from app.main import app
from app.models import (
    Book, Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, MasteryEvent, Page, Role, User,
)

Result = tuple[str, str, str]  # (PASS | FAIL | REVIEW, id, message)


class Ctx:
    def __init__(self, db: Session, client: TestClient, opts):
        self.db, self.client, self.opts = db, client, opts
        self.users: dict[str, User] = {}
        self.headers: dict[str, dict[str, str]] = {}
        self.llm: CountingLLM | None = None
        self.book_a: Book | None = None
        self.chapters_a: list[Chapter] = []
        self.room_a: dict | None = None
        self.room_b: dict | None = None
        self.private: dict = {}
        self.concepts_used: dict[str, Concept] = {}

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

    if settings.llm_provider.lower() != "openai_compat" and not (o.skip_model or o.allow_fake):
        return out + [("FAIL", "E1", f"LLM_PROVIDER is '{settings.llm_provider}' (need openai_compat, or run with --skip-model)")]

    from app.llm import get_llm_provider
    from app.llm.fake_provider import FakeLLMProvider
    try:
        inner = FakeLLMProvider() if o.skip_model else get_llm_provider()
        ctx.llm = CountingLLM(inner)
    except Exception as exc:
        return out + [("FAIL", "E1", f"LLM provider could not start: {type(exc).__name__}: {str(exc)[:200]}")]

    out.append((
        "PASS",
        "E1",
        f"model {'PLACEHOLDER (--skip-model)' if o.skip_model else ctx.llm.model_name or settings.llm_model}, "
        f"rolling window={settings.mastery_rolling_window} {settings.mastery_rolling_weights}, "
        f"briefing TTL={settings.briefing_cache_ttl_s}s",
    ))
    if o.skip_model:
        out.append(("REVIEW", "E2", "--skip-model: Personalization Agent briefing is a placeholder; run without --skip-model to judge real model quality"))
    return out


def _ready_chapters_with_concepts(db: Session, book: Book) -> list[Chapter]:
    found = []
    for ch in db.scalars(select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)):
        if len(chapter_concepts(db, ch.id)) >= 3:
            found.append(ch)
    return found


def check_data(ctx: Ctx) -> list[Result]:
    db, o = ctx.db, ctx.opts
    books = list(db.scalars(select(Book).where(Book.is_reference.is_(True)).order_by(Book.publisher, Book.class_name, Book.subject)))
    usable = {b.id: _ready_chapters_with_concepts(db, b) for b in books}
    usable = {k: v for k, v in usable.items() if v}
    if not usable:
        return [("FAIL", "D1", "no official book has a ready chapter with at least 3 concepts")]
    by_id = {b.id: b for b in books}
    if o.book:
        a = by_id.get(uuid.UUID(o.book))
        if a is None or a.id not in usable:
            return [("FAIL", "D1", f"--book {o.book} is not an official book with a ready chapter (>=3 concepts)")]
    else:
        a = by_id[max(usable, key=lambda k: len(usable[k]))]
    ctx.book_a, ctx.chapters_a = a, usable[a.id]
    return [("PASS", "D1", f"book A = {label(a)} (id {a.id}): {len(ctx.chapters_a)} ready chapter(s)")]


def setup_world(ctx: Ctx) -> list[Result]:
    db, a = ctx.db, ctx.book_a
    personalization.briefing_cache.clear()
    limiter.reset()

    for key, role in (("tA", Role.teacher), ("tB", Role.teacher), ("S1", Role.student), ("S2", Role.student)):
        u = make_user(db, role, key)
        ctx.users[key], ctx.headers[key] = u, {"Authorization": f"Bearer {u.supertokens_user_id}"}

    pb = Book(board="X", class_name="9", subject=a.subject, publisher="phase5_6 check", is_reference=False, owner_teacher_id=ctx.users["tB"].id)
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

    r_a = ctx.call("tA", "POST", "/teacher/rooms", json={"name": "phase5_6 check A", "room_type": "single_class"})
    r_b = ctx.call("tB", "POST", "/teacher/rooms", json={"name": "phase5_6 check B", "room_type": "single_class"})
    if r_a.status_code != 201 or r_b.status_code != 201:
        return [("FAIL", "W1", f"room creation failed: {r_a.status_code} / {r_b.status_code}")]
    ctx.room_a, ctx.room_b = r_a.json(), r_b.json()

    joins: list[int] = []
    approvals: list[int] = []
    for student_key, room_data, teacher_key in (("S1", ctx.room_a, "tA"), ("S2", ctx.room_b, "tB")):
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
        ("PASS", "W1", "two teachers each created a room"),
        ok(joins == [202, 202] and approvals == [200, 200] and link == 200, "W2",
           "S1 requested and was approved for teacher A's room and linked book A; S2 was approved for teacher B's room",
           f"joins={joins}, approvals={approvals}, link={link}"),
    ]


def check_rolling_mastery_and_propagation(ctx: Ctx) -> list[Result]:
    db, out = ctx.db, []
    s1 = ctx.users["S1"]
    ch1 = ctx.chapters_a[0]
    concepts = chapter_concepts(db, ch1.id)

    # Pick a concept with at least 1 dependent for weak/propagation testing
    with_deps = sorted(
        [(len(mastery.dependents(db, c.id)), c.name, c) for c in concepts if mastery.dependents(db, c.id)],
        key=lambda t: (t[0], t[1]),
    )
    if not with_deps:
        return [("REVIEW", "R0", f"no concept in '{ch1.title}' has dependents; rolling propagation check skipped")]

    _, _, c_weak = with_deps[0]
    deps = mastery.dependents(db, c_weak.id)
    dep_ids = {d.concept_id for d in deps}
    others = [c for c in concepts if c.id != c_weak.id and c.id not in dep_ids]
    if len(others) < 2:
        others = [c for c in concepts if c.id != c_weak.id]
    c_imp, c_stb = others[0], others[1]
    ctx.concepts_used = {"weak": c_weak, "improving": c_imp, "stable": c_stb, "dep": db.get(Concept, deps[0].concept_id)}

    now = datetime.now(timezone.utc)

    def add_hist(concept: Concept, kind: str, asked: int, correct: int, days_ago: int):
        sc = round(correct / asked, 4)
        db.add(
            MasteryEvent(
                student_id=s1.id,
                concept_id=concept.id,
                concept_name=concept.name[:300],
                kind=kind,
                score=sc,
                asked=asked,
                correct=correct,
                created_at=now - timedelta(days=days_ago),
            )
        )
        db.flush()

    # R1: Single off-day smoothing on `c_imp`: two 1.0 scores followed by a 0.50 off day -> rolling score 0.75 (OK, no weak flag)
    add_hist(c_imp, mastery.CHECK, 2, 0, days_ago=26)  # old baseline: 0.0
    add_hist(c_imp, mastery.QUIZ, 2, 1, days_ago=19)   # old baseline: 0.5 (baseline avg = 0.25)
    add_hist(c_imp, mastery.CHECK, 2, 2, days_ago=6)   # recent window: 1.0
    add_hist(c_imp, mastery.QUIZ, 2, 2, days_ago=3)    # recent window: 1.0
    add_hist(c_imp, mastery.CHECK, 2, 1, days_ago=1)   # recent window off day: 0.5 -> 0.5*0.5 + 0.3*1.0 + 0.2*1.0 = 0.75
    db.commit()

    st_imp = mastery.current_state(db, s1.id, [c_imp.id])[c_imp.id]
    out.append(ok(
        st_imp.score == 0.75 and st_imp.status == mastery.OK and st_imp.reason is None,
        "R1",
        f"3-event rolling window smoothed a single off day on {c_imp.name!r} ([1.0, 1.0, 0.5] -> rolling 0.75 >= 0.60, status='ok')",
        f"got score={st_imp.score}, status={st_imp.status}",
    ))

    # R2: Declining trajectory on `c_weak` that crosses below WEAK_BELOW (0.60) and propagates `at_risk` to its dependents
    add_hist(c_weak, mastery.CHECK, 2, 2, days_ago=25)  # old baseline: 1.0
    add_hist(c_weak, mastery.QUIZ, 2, 2, days_ago=18)   # old baseline: 1.0
    add_hist(c_weak, mastery.CHECK, 2, 1, days_ago=4)   # window oldest: 0.5
    add_hist(c_weak, mastery.QUIZ, 2, 0, days_ago=2)    # window previous: 0.0
    # Latest check via record_check (0/2 = 0.0) -> window [0.5, 0.0, 0.0] -> rolling score = 0.5*0 + 0.3*0 + 0.2*0.5 = 0.10 (WEAK!)
    mastery.record_check(db, s1.id, None, None, {c_weak.id: (2, 0)}, kind=mastery.QUIZ)

    # Also seed a stable concept `c_stb` (1.0 twenty days ago, 1.0 yesterday)
    add_hist(c_stb, mastery.CHECK, 2, 2, days_ago=20)
    add_hist(c_stb, mastery.QUIZ, 2, 2, days_ago=1)
    db.commit()

    states = mastery.current_state(db, s1.id)
    st_weak = states.get(c_weak.id)
    flagged_deps = [states.get(d.concept_id) for d in deps if states.get(d.concept_id) is not None]
    out.append(ok(
        st_weak is not None and st_weak.status == mastery.WEAK and st_weak.score == 0.10
        and st_weak.reason is not None and "tested weak directly" in st_weak.reason,
        "R2",
        f"rolling-window weak concept {c_weak.name!r} has score 0.10, status='weak', and explainable direct reason: {st_weak.reason!r}",
        f"got {st_weak}",
    ))
    out.append(ok(
        len(flagged_deps) == len(deps)
        and all(fd.status == mastery.AT_RISK and fd.reason and c_weak.name in fd.reason and fd.flagged_by == c_weak.id for fd in flagged_deps),
        "R3",
        f"{len(flagged_deps)} dependent concept(s) flagged 'at_risk' with explainable prerequisite reason naming {c_weak.name!r}",
        f"flagged_deps={flagged_deps}",
    ))

    # R4: Student mastery endpoint returns explainable reasons for both weak and at_risk concepts
    m_res = ctx.call("S1", "GET", "/student/mastery").json()
    by_cid = {c["concept_id"]: c for c in m_res.get("concepts", [])}
    w_item = by_cid.get(str(c_weak.id), {})
    d_item = by_cid.get(str(deps[0].concept_id), {})
    out.append(ok(
        w_item.get("status") == "weak" and bool(w_item.get("reason"))
        and d_item.get("status") == "at_risk" and bool(d_item.get("reason")),
        "R4",
        "GET /student/mastery exposes explainable reasons on both directly weak and propagated at_risk concepts",
        f"w_item={w_item}, d_item={d_item}",
    ))
    return out


def check_trends_api(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    s1 = ctx.users["S1"]
    c_weak = ctx.concepts_used["weak"]
    c_imp = ctx.concepts_used["improving"]
    c_stb = ctx.concepts_used["stable"]
    c_dep = ctx.concepts_used["dep"]

    res = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/trends")
    body = res.json() if res.status_code == 200 else {}
    out.append(ok(
        res.status_code == 200 and body.get("weeks_window") == 4 and len(body.get("subjects", [])) >= 1,
        "T1",
        f"GET /teacher/students/{{id}}/trends returned 4-week subject/chapter breakdown ({body.get('weak_count')} weak, {body.get('at_risk_count')} at risk)",
        f"status={res.status_code}, body={res.text[:200]}",
    ))
    if res.status_code != 200:
        return out

    by_id = {c["concept_id"]: c for c in body.get("concepts", [])}
    imp_t = by_id.get(str(c_imp.id), {})
    weak_t = by_id.get(str(c_weak.id), {})
    stb_t = by_id.get(str(c_stb.id), {})
    dep_t = by_id.get(str(c_dep.id), {})

    out.append(ok(
        imp_t.get("trend") == "improving" and weak_t.get("trend") == "declining" and stb_t.get("trend") == "stable"
        and dep_t.get("status") == "at_risk" and bool(dep_t.get("reason")),
        "T2",
        f"trends accurately categorized {c_imp.name!r} as improving (+{imp_t.get('delta')}), "
        f"{c_weak.name!r} as declining ({weak_t.get('delta')}), and {c_stb.name!r} as stable",
        f"imp={imp_t.get('trend')}, weak={weak_t.get('trend')}, stb={stb_t.get('trend')}",
    ))
    return out


def check_sessions_and_briefing(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    s1 = ctx.users["S1"]
    c_weak = ctx.concepts_used["weak"]
    c_dep = ctx.concepts_used["dep"]
    c_imp = ctx.concepts_used["improving"]

    # S1: Teacher A logs 2 post-session entries for S1
    s_old = ctx.call(
        "tA",
        "POST",
        f"/teacher/students/{s1.id}/sessions",
        json={
            "session_date": (date.today() - timedelta(days=4)).isoformat(),
            "notes": f"Worked on {c_imp.name}; student showed steady improvement on practice problems.",
            "tags": ["revision", "improving"],
        },
    )
    s_new = ctx.call(
        "tA",
        "POST",
        f"/teacher/students/{s1.id}/sessions",
        json={
            "session_date": (date.today() - timedelta(days=1)).isoformat(),
            "notes": f"Covered {c_weak.name}; student struggled with core definitions and needs a refresher before {c_dep.name}.",
            "tags": ["needs-refresher", "weak-area"],
        },
    )
    listed = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/sessions")
    logs = listed.json() if listed.status_code == 200 else []
    out.append(ok(
        s_old.status_code == 201 and s_new.status_code == 201 and len(logs) == 2 and logs[0]["id"] == s_new.json()["id"],
        "S1",
        "teacher recorded 2 session logs (with free text and tags) and retrieved them newest-first",
        f"post={s_old.status_code}/{s_new.status_code}, listed={len(logs)}",
    ))

    # B1: Request pre-session briefing -> generated by Personalization Agent, grounded in allowed concepts
    calls_before = ctx.llm.calls
    b1_res = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/briefing")
    b1 = b1_res.json() if b1_res.status_code == 200 else {}
    allowed_names = {c.name.lower() for c in chapter_concepts(ctx.db, ctx.chapters_a[0].id)}
    focus_ok = all(fc.lower() in allowed_names for fc in b1.get("focus_concepts", []))
    out.append(ok(
        b1_res.status_code == 200 and b1.get("cached") is False and ctx.llm.calls > calls_before
        and bool(b1.get("last_covered")) and bool(b1.get("weak_areas")) and bool(b1.get("suggested_focus")) and focus_ok,
        "B1",
        f"GET /teacher/students/{{id}}/briefing generated a fresh pre-session briefing (focus_concepts={b1.get('focus_concepts')}, 0 hallucinated concepts)",
        f"status={b1_res.status_code}, body={b1_res.text[:250]}",
    ))
    if b1_res.status_code != 200:
        return out

    out.append((
        "REVIEW",
        "B2",
        f"Personalization Agent briefing to judge: "
        f"LAST COVERED: {b1['last_covered']!r} || "
        f"WEAK AREAS: {b1['weak_areas']!r} || "
        f"SUGGESTED FOCUS: {b1['suggested_focus']!r} (focus_concepts={b1['focus_concepts']})",
    ))

    # B3: Second request within 5 minutes returns cached briefing with 0 extra LLM calls
    calls_mid = ctx.llm.calls
    b2_res = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/briefing")
    b2 = b2_res.json() if b2_res.status_code == 200 else {}
    out.append(ok(
        b2_res.status_code == 200 and b2.get("cached") is True and ctx.llm.calls == calls_mid
        and b2.get("generated_at") == b1.get("generated_at"),
        "B3",
        "subsequent briefing call within 5 minutes returned the cached briefing with 0 extra LLM calls",
        f"cached={b2.get('cached')}, calls +{ctx.llm.calls - calls_mid}",
    ))

    # B4: Cache expiry after 5 minutes AND immediate invalidation when a new session log is recorded
    key = (str(ctx.users["tA"].id), str(s1.id))
    personalization.briefing_cache._entries[key].expires_at = 0.0
    b3_res = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/briefing")
    expired_ok = b3_res.status_code == 200 and b3_res.json().get("cached") is False and ctx.llm.calls > calls_mid

    calls_before_new_sess = ctx.llm.calls
    ctx.call(
        "tA",
        "POST",
        f"/teacher/students/{s1.id}/sessions",
        json={"notes": f"Follow-up session: practiced {c_weak.name} diagrams.", "tags": ["follow-up"]},
    )
    b4_res = ctx.call("tA", "GET", f"/teacher/students/{s1.id}/briefing")
    invalidated_ok = b4_res.status_code == 200 and b4_res.json().get("cached") is False and ctx.llm.calls > calls_before_new_sess
    out.append(ok(
        expired_ok and invalidated_ok,
        "B4",
        "briefing cache expires after 5 minutes and invalidates immediately when a new session log is recorded",
        f"expired_ok={expired_ok}, invalidated_ok={invalidated_ok}",
    ))
    return out


def check_tenancy(ctx: Ctx) -> list[Result]:
    out: list[Result] = []
    s1, s2 = ctx.users["S1"], ctx.users["S2"]
    calls_before = ctx.llm.calls

    # L1: Teacher B cannot view trends, list/create session logs, or generate a briefing for Teacher A's student S1 (404, 0 LLM calls)
    tb_codes = [
        ctx.call("tB", "GET", f"/teacher/students/{s1.id}/trends").status_code,
        ctx.call("tB", "GET", f"/teacher/students/{s1.id}/sessions").status_code,
        ctx.call("tB", "POST", f"/teacher/students/{s1.id}/sessions", json={"notes": "unauthorized", "tags": []}).status_code,
        ctx.call("tB", "GET", f"/teacher/students/{s1.id}/briefing").status_code,
    ]
    # Teacher A cannot access Teacher B's student S2
    ta_codes = [
        ctx.call("tA", "GET", f"/teacher/students/{s2.id}/trends").status_code,
        ctx.call("tA", "GET", f"/teacher/students/{s2.id}/briefing").status_code,
    ]
    out.append(ok(
        tb_codes == [404, 404, 404, 404] and ta_codes == [404, 404] and ctx.llm.calls == calls_before,
        "L1",
        "teachers get 404 on another teacher's student across /trends, /sessions, and /briefing with 0 LLM calls",
        f"tb_codes={tb_codes}, ta_codes={ta_codes}",
    ))

    # L2: Student role gets 403 Forbidden on all teacher analytics/session/briefing routes
    s1_codes = [
        ctx.call("S1", "GET", f"/teacher/students/{s1.id}/trends").status_code,
        ctx.call("S1", "GET", f"/teacher/students/{s1.id}/sessions").status_code,
        ctx.call("S1", "POST", f"/teacher/students/{s1.id}/sessions", json={"notes": "self", "tags": []}).status_code,
        ctx.call("S1", "GET", f"/teacher/students/{s1.id}/briefing").status_code,
    ]
    out.append(ok(
        s1_codes == [403, 403, 403, 403],
        "L2",
        "student role gets 403 on teacher /trends, /sessions, and /briefing routes",
        f"got {s1_codes}",
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

    is_sqlite = engine.dialect.name == "sqlite"
    raw_conn = None
    prev_isolation = None
    if is_sqlite:
        raw_conn = connection.connection.dbapi_connection
        prev_isolation = raw_conn.isolation_level
        raw_conn.isolation_level = None
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
    saved_llm = personalization.get_llm_provider

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
            personalization.get_llm_provider = lambda: ctx.llm
            section("Data to test on", check_data)
            if ctx.book_a is not None:
                section("Throwaway world (rolled back at the end)", setup_world)
                if ctx.room_a is not None:
                    section("Rolling-window mastery, single-off-day smoothing & explainable propagation", check_rolling_mastery_and_propagation)
                    section("Longitudinal trend analytics (GET /teacher/students/{id}/trends)", check_trends_api, needs=("concepts_used",))
                    section("Teacher session logs & Personalization Agent briefing", check_sessions_and_briefing, needs=("concepts_used",))
                    section("Tenancy & role isolation", check_tenancy)
    finally:
        personalization.briefing_cache.clear()
        personalization.get_llm_provider = saved_llm
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(session_dependency, None)
        db.close()
        outer.rollback()
        if is_sqlite and raw_conn is not None:
            raw_conn.isolation_level = prev_isolation
        connection.close()

    lines.append(f"\nRESULT: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['REVIEW']} REVIEW")
    lines.append(
        "Phase 5 & 6 can be closed once there is no FAIL and every REVIEW line has been judged."
        if not counts["FAIL"]
        else "Phase 5 & 6 is NOT finished: fix the FAIL lines and run this again."
    )
    lines.append("Everything this run created was rolled back.")
    return lines, counts["FAIL"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", help="official book ID to test on")
    parser.add_argument("--skip-model", action="store_true", help="no model calls: use FakeLLMProvider")
    parser.add_argument("--allow-fake", action="store_true", help="accept fake LLM / SQLite (for script tests)")
    args = parser.parse_args()
    from app.db.session import engine as real_engine

    text, fails = run(real_engine, args)
    print("\n".join(text))
    sys.exit(1 if fails else 0)