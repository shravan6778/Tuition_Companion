"""Phase 3 step 6: the append-only mastery log, weak flags and propagation along prerequisite edges."""
import json
import re
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.assessment import mastery
from app.assessment.checks import plan_check
from app.core.config import settings
from app.models import ConceptEdge, CrossChapterEdge, MasteryEvent, Role
from tests.test_book_access import make_user
from tests.test_phase3_step2 import TISSUE_Q, assign, world  # noqa: F401  (world is a fixture)
from tests.test_phase3_step3 import GOOD, Scripted, use_model


class CheckLLM:
    model_name = "scripted"

    def __init__(self):
        self.n = 0

    def complete_json(self, system, user):
        self.n += 1
        name = re.search(r"^CONCEPT: (.+)$", user, flags=re.M).group(1)
        return json.dumps({"question": f"About {name} (v{self.n})?", "options": [f"{name} true {self.n}", f"{name} false A", f"{name} false B", f"{name} false C"],
                           "correct_index": 0, "explanation": f"because {name}"})


@pytest.fixture()
def graph(world, session_factory, monkeypatch):
    """Cell -> Tissue (same chapter) -> Force (next chapter): Tissue needs Cell, Force needs Tissue."""
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: CheckLLM())
    c = {k: uuid.UUID(v) for k, v in world["concepts"].items()}
    with session_factory() as db:
        db.add(ConceptEdge(chapter_id=uuid.UUID(world["ids"]["ch1"]), concept_id=c["Tissue"], prerequisite_id=c["Cell"], source="llm"))
        db.add(CrossChapterEdge(chapter_id=uuid.UUID(world["ids"]["ch2"]), concept_id=c["Force"], prerequisite_id=c["Tissue"], similarity=0.8))
        db.commit()
    return c


def take(client, w, concept_names, right):
    """Take a check over the named concepts. `right` = names answered correctly, everything else wrong. Returns the submitted check."""
    a = assign(client, w, level="concept", chapter=None, concept_ids=[w["concepts"][n] for n in concept_names])
    check = client.post(f"/student/assignments/{a['id']}/complete", headers=w["sh"]).json()
    return submit(client, w, check, right)


def submit(client, w, check, right):
    from tests.test_phase3_step5 import keys
    key = keys_for(check)
    answers = [{"question_id": q["id"], "chosen_index": key[q["id"]] if q["concept_name"] in right else (key[q["id"]] + 1) % 4} for q in check["questions"]]
    res = client.post(f"/student/checks/{check['id']}/submit", json={"answers": answers}, headers=w["sh"])
    assert res.status_code == 200, res.text
    return res.json()


_SF = {}


def keys_for(check):
    with _SF["f"]() as db:
        from app.models import CheckQuestion
        return {str(q.id): q.correct_index for q in db.scalars(select(CheckQuestion).where(CheckQuestion.check_id == uuid.UUID(check["id"])))}


@pytest.fixture(autouse=True)
def _sf(session_factory):
    _SF["f"] = session_factory


def events(session_factory, kind=None):
    with session_factory() as db:
        rows = db.scalars(select(MasteryEvent).order_by(MasteryEvent.id)).all()
        return [r for r in rows if kind is None or r.kind == kind]


def state(client, w):
    return {c["concept_name"]: c for c in client.get("/student/mastery", headers=w["sh"]).json()["concepts"]}


# ---- a check writes its events -------------------------------------------------------------------------------

def test_a_submitted_check_writes_one_scored_event_per_concept(client, session_factory, world, graph):
    done = take(client, world, ["Cell", "Tissue"], right={"Tissue"})
    rows = events(session_factory, "check")
    by_name = {r.concept_name: r for r in rows}
    assert set(by_name) == {"Cell", "Tissue"}
    assert (by_name["Cell"].score, by_name["Cell"].asked, by_name["Cell"].correct) == (0.0, 1, 0)
    assert (by_name["Tissue"].score, by_name["Tissue"].asked, by_name["Tissue"].correct) == (1.0, 1, 1)
    assert all(str(r.check_id) == done["id"] and r.student_id == world["student"].id for r in rows)


def test_a_concept_asked_twice_scores_the_share_correct(client, session_factory, world, graph):
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Tissue"]])  # one concept -> 2 questions
    check = client.post(f"/student/assignments/{a['id']}/complete", headers=world["sh"]).json()
    key = keys_for(check)
    first, second = check["questions"]
    answers = [{"question_id": first["id"], "chosen_index": key[first["id"]]}, {"question_id": second["id"], "chosen_index": (key[second["id"]] + 1) % 4}]
    client.post(f"/student/checks/{check['id']}/submit", json={"answers": answers}, headers=world["sh"])
    row = events(session_factory, "check")[0]
    assert (row.score, row.asked, row.correct) == (0.5, 2, 1)
    assert state(client, world)["Tissue"]["status"] == "weak"  # 0.5 < 0.6


# ---- weak flags and propagation ------------------------------------------------------------------------------

def test_a_weak_concept_flags_what_depends_on_it_with_the_reason_and_not_what_it_depends_on(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())  # Cell tests weak
    flagged = {e.concept_name: e for e in events(session_factory, "propagated")}
    assert set(flagged) == {"Tissue", "Force"}  # Tissue needs Cell; Force needs Tissue (2 steps, across chapters)
    assert flagged["Tissue"].reason == "flagged because it depends on Cell, which tested weak"
    assert flagged["Force"].reason == "flagged because it depends on Tissue, which depends on Cell, which tested weak"
    assert all(e.score is None and e.asked is None and e.source_concept_id == graph["Cell"] for e in flagged.values())
    s = state(client, world)
    assert s["Cell"]["status"] == "weak" and s["Tissue"]["status"] == "at_risk" and s["Force"]["status"] == "at_risk"
    assert s["Tissue"]["score"] is None and s["Tissue"]["reason"].startswith("flagged because") and s["Tissue"]["flagged_by_concept_id"] == str(graph["Cell"])


def test_propagation_only_goes_towards_dependents(client, session_factory, world, graph):
    take(client, world, ["Tissue"], right=set())  # Tissue weak: Cell is its PREREQUISITE and must not be flagged
    assert {e.concept_name for e in events(session_factory, "propagated")} == {"Force"}
    assert "Cell" not in state(client, world)


def test_a_strong_result_flags_nothing(client, session_factory, world, graph):
    take(client, world, ["Cell", "Tissue"], right={"Cell", "Tissue"})
    assert events(session_factory, "propagated") == []
    assert {c["status"] for c in state(client, world).values()} == {"ok"}


def test_a_dependent_measured_in_the_same_check_is_not_flagged(client, session_factory, world, graph):
    take(client, world, ["Cell", "Tissue"], right={"Tissue"})  # Cell weak, Tissue measured fine in the same check
    assert {e.concept_name for e in events(session_factory, "propagated")} == {"Force"}
    assert state(client, world)["Tissue"]["status"] == "ok"


def test_the_depth_cap_limits_how_far_a_weak_result_reaches(client, session_factory, world, graph, monkeypatch):
    monkeypatch.setattr(settings, "propagate_max_depth", 1)
    take(client, world, ["Cell"], right=set())
    assert {e.concept_name for e in events(session_factory, "propagated")} == {"Tissue"}


def test_a_later_measured_check_clears_the_flag_and_nothing_is_rewritten(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())
    before = [(e.id, e.kind, e.concept_name, e.score, e.reason) for e in events(session_factory)]
    assert state(client, world)["Tissue"]["status"] == "at_risk"
    take(client, world, ["Tissue"], right={"Tissue"})  # Tissue measured fine
    after = events(session_factory)
    assert [(e.id, e.kind, e.concept_name, e.score, e.reason) for e in after[:len(before)]] == before  # append-only: old rows untouched
    assert len(after) > len(before)
    s = state(client, world)
    assert s["Tissue"]["status"] == "ok" and s["Tissue"]["score"] == 1.0 and s["Tissue"]["reason"] is None
    assert s["Force"]["status"] == "at_risk" and s["Cell"]["status"] == "weak"  # unrelated flags stay until their own check


def test_current_mastery_is_the_latest_check_not_an_average(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())
    take(client, world, ["Cell"], right={"Cell"})
    assert state(client, world)["Cell"]["score"] == 1.0 and state(client, world)["Cell"]["status"] == "ok"
    assert len([e for e in events(session_factory, "check") if e.concept_name == "Cell"]) == 2


def test_a_second_weak_result_on_the_same_cause_does_not_pile_up_duplicate_flags(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())
    first = len(events(session_factory, "propagated"))
    take(client, world, ["Cell"], right=set())  # Tissue and Force are still at risk because of Cell
    assert len(events(session_factory, "propagated")) == first


def test_the_weak_concept_and_the_at_risk_ones_are_asked_about_first_in_the_next_big_check(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())
    with session_factory() as db:
        from app.assessment.service import _ask_first
        ids = [world["concepts"][n] for n in ("Force", "Tissue", "Cell")]
        order = _ask_first(db, world["student"], [uuid.UUID(i) for i in ids])
    assert order[0] == world["concepts"]["Cell"] and set(order) == set(ids)  # weak first, then the flagged ones


# ---- the transaction and the table's own rules -----------------------------------------------------------------

def test_a_failure_while_recording_leaves_the_check_open_and_no_events(client, session_factory, world, graph, monkeypatch):
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Cell"]])
    check = client.post(f"/student/assignments/{a['id']}/complete", headers=world["sh"]).json()
    monkeypatch.setattr(mastery, "dependents", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("graph unavailable")))
    key = keys_for(check)
    answers = [{"question_id": q["id"], "chosen_index": (key[q["id"]] + 1) % 4} for q in check["questions"]]
    try:
        res = client.post(f"/student/checks/{check['id']}/submit", json={"answers": answers}, headers=world["sh"])
        assert res.status_code == 500
    except RuntimeError:
        pass
    assert events(session_factory) == []
    again = client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()
    assert again["status"] == "open" and again["score"] is None and again["concept_results"] is None  # nothing half-written, and it can be retried


def test_the_table_refuses_a_flag_without_a_reason_or_a_score_on_a_doubt(session_factory, world):
    base = dict(student_id=world["student"].id, concept_name="x")
    for bad in (dict(kind="propagated"), dict(kind="propagated", reason=""), dict(kind="check", score=0.5), dict(kind="doubt", score=0.5), dict(kind="check", score=1.5, asked=1, correct=1), dict(kind="nope")):
        with session_factory() as db:
            db.add(MasteryEvent(**base, **bad))
            with pytest.raises(IntegrityError):
                db.commit()


# ---- doubt events ------------------------------------------------------------------------------------------------

def test_a_grounded_doubt_writes_a_doubt_event_and_an_ungrounded_one_does_not(client, session_factory, world, graph, monkeypatch):
    use_model(monkeypatch, Scripted(GOOD))
    a = assign(client, world)
    assert client.post("/student/doubts", json={"text": TISSUE_Q, "assignment_id": a["id"]}, headers=world["sh"]).json()["status"] == "grounded"
    rows = events(session_factory, "doubt")
    assert len(rows) == 1 and rows[0].concept_name == "Tissue" and rows[0].score is None and str(rows[0].assignment_id) == a["id"]
    assert client.post("/student/doubts", json={"text": "zebra quantum jukebox harmonica zebra quantum jukebox"}, headers=world["sh"]).json()["status"] == "not_in_book"
    assert len(events(session_factory, "doubt")) == 1
    assert state(client, world) == {}  # a doubt is not a measurement and never changes mastery


# ---- what the student sees -------------------------------------------------------------------------------------------

def test_the_submitted_check_shows_concept_results_and_what_it_put_at_risk_and_an_open_check_shows_neither(client, world, graph):
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Cell"]])
    check = client.post(f"/student/assignments/{a['id']}/complete", headers=world["sh"]).json()
    assert check["concept_results"] is None and check["at_risk"] is None
    done = submit(client, world, check, right=set())
    assert [(r["concept_name"], r["score"], r["weak"]) for r in done["concept_results"]] == [("Cell", 0.0, True)]
    assert {(r["concept_name"], r["reason"]) for r in done["at_risk"]} == {
        ("Tissue", "flagged because it depends on Cell, which tested weak"),
        ("Force", "flagged because it depends on Tissue, which depends on Cell, which tested weak")}
    assert client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()["at_risk"] == done["at_risk"]


def test_the_mastery_summary_orders_weak_then_at_risk_then_ok_and_filters(client, world, graph):
    take(client, world, ["Cell"], right=set())
    take(client, world, ["Tissue"], right={"Tissue"})
    body = client.get("/student/mastery", headers=world["sh"]).json()
    assert [(c["concept_name"], c["status"]) for c in body["concepts"]] == [("Cell", "weak"), ("Force", "at_risk"), ("Tissue", "ok")]
    assert (body["weak"], body["at_risk"], body["ok"]) == (1, 1, 1)
    assert [c["concept_name"] for c in client.get("/student/mastery?status=weak", headers=world["sh"]).json()["concepts"]] == ["Cell"]


def test_the_event_history_is_newest_first_filterable_and_private(client, session_factory, world, graph):
    take(client, world, ["Cell"], right=set())
    log = client.get("/student/mastery/events", headers=world["sh"]).json()
    assert [e["kind"] for e in log] == ["propagated", "propagated", "check"] and all(e["id"] for e in log)
    assert all(e["reason"] for e in log if e["kind"] == "propagated")
    only_cell = client.get(f"/student/mastery/events?concept_id={world['concepts']['Cell']}", headers=world["sh"]).json()
    assert [e["kind"] for e in only_cell] == ["check"]
    _, other = make_user(session_factory, Role.student, "studentb")
    assert client.get("/student/mastery", headers=other).json()["concepts"] == [] and client.get("/student/mastery/events", headers=other).json() == []
    assert client.get("/student/mastery", headers=world["th"]).status_code in (401, 403)


# ---- the plan spreads across the scope (real-data finding) ---------------------------------------------------------------

def test_a_big_scope_with_nothing_to_prioritise_is_sampled_across_the_whole_scope_not_its_first_ten():
    ids = [f"c{i}" for i in range(44)]
    plan = plan_check(ids)
    positions = [ids.index(c) for c in plan]
    assert len(plan) == 10 and positions == sorted(positions) and positions[0] < 5 and positions[-1] > 38
    assert max(b - a for a, b in zip(positions, positions[1:])) <= 5  # no long stretch of the chapter left unasked


# ---- the real-data helper -----------------------------------------------------------------------------------------------

def test_try_mastery_shows_who_would_be_flagged_and_why_without_writing(client, session_factory, world, graph):
    from app.db import try_mastery
    with session_factory() as db:
        lines = try_mastery.run(db, uuid.UUID(world["ids"]["ch1"]), "Cell")
        assert db.scalars(select(MasteryEvent)).all() == []
    text = "\n".join(lines)
    assert "Tissue: flagged because it depends on Cell, which tested weak" in text and "Force:" in text
    with session_factory() as db:
        assert "Cell" in "\n".join(try_mastery.run(db, uuid.UUID(world["ids"]["ch1"])))
