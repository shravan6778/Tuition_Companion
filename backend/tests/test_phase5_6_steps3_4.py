"""Tests for Phase 5 & 6 Steps 3 & 4:
  * Step 3: `agents/personalization.py` context assembly (last 3 session logs, weak/at-risk concepts with explainable
            reasons, and recent trends), schema validation, and anti-hallucination check on `focus_concepts`.
  * Step 4: `GET /teacher/students/{id}/briefing` real-time generation, 5-minute TTL caching (`cached=True` within 5 min
            with 0 extra LLM calls, expires after 300s, and invalidates immediately when a new session log is added),
            and strict tenant isolation."""
import json
from datetime import date, datetime, timedelta, timezone

import pytest

from app.agents import personalization
from app.assessment import mastery
from app.models import (
    Book, Chapter, ChapterStatus, Concept, ConceptEdge, MasteryEvent, Page, Role, Room, RoomMember, RoomType,
    SessionLog, User, student_book,
)


def _setup_briefing_world(db):
    personalization.briefing_cache.clear()
    now = datetime.now(timezone.utc)

    t_a = User(supertokens_user_id="st-t-brf-a", name="Teacher Briefing A", username="teacher_brf_a", phone="9300000001", role=Role.teacher)
    t_b = User(supertokens_user_id="st-t-brf-b", name="Teacher Briefing B", username="teacher_brf_b", phone="9300000002", role=Role.teacher)
    s_1 = User(supertokens_user_id="st-s-brf-1", name="Aarav Sharma", username="student_brf_1", phone="9300000003", role=Role.student, link_code="BRF00001")
    s_2 = User(supertokens_user_id="st-s-brf-2", name="Other Student", username="student_brf_2", phone="9300000004", role=Role.student, link_code="BRF00002")
    db.add_all([t_a, t_b, s_1, s_2])
    db.flush()

    room_a = Room(teacher_id=t_a.id, name="Class 9 Science", room_type=RoomType.single_class, join_code="BRFRMA")
    room_b = Room(teacher_id=t_b.id, name="Class 9 Other", room_type=RoomType.single_class, join_code="BRFRMB")
    db.add_all([room_a, room_b])
    db.flush()

    db.add(RoomMember(room_id=room_a.id, user_id=s_1.id))
    db.add(RoomMember(room_id=room_b.id, user_id=s_2.id))

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    db.add(book)
    db.flush()

    db.execute(student_book.insert().values(student_id=s_1.id, book_id=book.id))

    ch = Chapter(book_id=book.id, title="The Fundamental Unit of Life", sequence_num=1, status=ChapterStatus.READY)
    db.add(ch)
    db.flush()

    page = Page(
        chapter_id=ch.id,
        page_number=1,
        content_text="Cell Membrane regulates transport via osmosis. Plant Cell Wall depends on Cell Membrane structure.",
    )
    db.add(page)
    db.flush()

    c_weak = Concept(page_id=page.id, name="Cell Membrane", description="Selectively permeable membrane", name_key="cell membrane", position=0, is_canonical=True)
    c_risk = Concept(page_id=page.id, name="Plant Cell Wall", description="Structural layer outside membrane", name_key="plant cell wall", position=1, is_canonical=True)
    c_ok = Concept(page_id=page.id, name="Cytoplasm", description="Fluid inside the cell", name_key="cytoplasm", position=2, is_canonical=True)
    db.add_all([c_weak, c_risk, c_ok])
    db.flush()

    # Plant Cell Wall depends on Cell Membrane
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c_risk.id, prerequisite_id=c_weak.id, source="llm"))
    db.flush()

    # Seed historical check on Cytoplasm (improving: 0.5 -> 1.0)
    db.add(
        MasteryEvent(
            student_id=s_1.id,
            concept_id=c_ok.id,
            concept_name=c_ok.name,
            kind=mastery.CHECK,
            score=0.5,
            asked=2,
            correct=1,
            created_at=now - timedelta(days=20),
        )
    )
    db.add(
        MasteryEvent(
            student_id=s_1.id,
            concept_id=c_ok.id,
            concept_name=c_ok.name,
            kind=mastery.QUIZ,
            score=1.0,
            asked=2,
            correct=2,
            created_at=now - timedelta(days=1),
        )
    )
    db.flush()

    # Record failing check on Cell Membrane (0/2 = 0.0 -> weak, and propagates at_risk to Plant Cell Wall)
    mastery.record_check(db, s_1.id, None, None, {c_weak.id: (2, 0)})

    # Add 4 session logs (only the last 3 should be fetched into the briefing context)
    for i, (d_offset, note) in enumerate([
        (10, "Oldest session 4: introductory cell overview."),
        (7, "Session 3: covered Cytoplasm and organelles."),
        (3, "Session 2: started Cell Membrane diffusion."),
        (1, "Latest Session 1: student struggled with selective permeability in Cell Membrane."),
    ]):
        db.add(
            SessionLog(
                student_id=s_1.id,
                teacher_id=t_a.id,
                session_date=date.today() - timedelta(days=d_offset),
                notes=note,
                tags=[f"tag-{i}"],
            )
        )

    out = {
        "t_a_id": t_a.id,
        "s_1_id": s_1.id,
        "s_2_id": s_2.id,
        "th_a": {"Authorization": f"Bearer {t_a.supertokens_user_id}"},
        "th_b": {"Authorization": f"Bearer {t_b.supertokens_user_id}"},
        "sh_1": {"Authorization": f"Bearer {s_1.supertokens_user_id}"},
    }
    db.commit()
    return out


def test_personalization_context_assembly_and_anti_hallucination(session_factory):
    with session_factory() as db:
        w = _setup_briefing_world(db)
        teacher = db.get(User, w["t_a_id"])
        ctx = personalization.assemble_briefing_context(db, teacher, w["s_1_id"])

        # (a) Only the last 3 session logs are fetched, newest first
        assert len(ctx.recent_sessions) == 3
        assert "Latest Session 1" in ctx.recent_sessions[0].notes
        assert all("Oldest session 4" not in s.notes for s in ctx.recent_sessions)

        # (b) Weak & at-risk concepts + (c) trends present
        assert ctx.trends_report.weak_count == 1
        assert ctx.trends_report.at_risk_count == 1
        assert ctx.trends_report.improving_count == 1
        assert set(ctx.allowed_concepts.values()) == {"Cell Membrane", "Plant Cell Wall", "Cytoplasm"}

        # Test anti-hallucination retry: first LLM reply invents "Quantum Teleportation", second reply uses valid concepts
        calls = []

        class ScriptedLLM:
            model_name = "scripted-test"

            def complete_json(self, system, user):
                calls.append(user)
                if len(calls) == 1:
                    return json.dumps({
                        "last_covered": "Covered cell membrane transport in the last session.",
                        "weak_areas": "Cell Membrane tested weak directly and Plant Cell Wall is flagged at risk.",
                        "suggested_focus": "Review Quantum Teleportation and Cell Membrane.",
                        "focus_concepts": ["Quantum Teleportation", "Cell Membrane"],
                    })
                return json.dumps({
                    "last_covered": "Covered cell membrane transport in the last session.",
                    "weak_areas": "Cell Membrane tested weak directly (0%), putting Plant Cell Wall at risk.",
                    "suggested_focus": "Start with Cell Membrane before moving to Plant Cell Wall.",
                    "focus_concepts": ["Cell Membrane", "Plant Cell Wall"],
                })

        res = personalization.generate_briefing(ScriptedLLM(), ctx)
        assert len(calls) == 2
        assert "unknown/hallucinated concept" in calls[1]
        assert res.focus_concepts == ["Cell Membrane", "Plant Cell Wall"]
        assert "Cell Membrane" in res.weak_areas

        # If LLM persistently hallucinates across all retries, raises PersonalizationError
        class AlwaysHallucinatingLLM:
            model_name = "bad-llm"

            def complete_json(self, system, user):
                return json.dumps({
                    "last_covered": "Covered cell membrane transport in the last session.",
                    "weak_areas": "Cell Membrane tested weak directly.",
                    "suggested_focus": "Focus on General Relativity.",
                    "focus_concepts": ["General Relativity"],
                })

        with pytest.raises(personalization.PersonalizationError):
            personalization.generate_briefing(AlwaysHallucinatingLLM(), ctx)


def test_briefing_endpoint_5_minute_cache_and_invalidation(client, session_factory, monkeypatch):
    with session_factory() as db:
        w = _setup_briefing_world(db)

    llm_calls = 0
    orig_get_llm = personalization.get_llm_provider

    def counting_llm():
        inner = orig_get_llm()

        class Wrapper:
            model_name = inner.model_name

            def complete_json(self, s, u):
                nonlocal llm_calls
                llm_calls += 1
                return inner.complete_json(s, u)

        return Wrapper()

    monkeypatch.setattr(personalization, "get_llm_provider", counting_llm)

    # 1. First request generates fresh briefing (cached=False, 1 LLM call)
    r1 = client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["th_a"])
    assert r1.status_code == 200, r1.text
    b1 = r1.json()
    assert b1["cached"] is False
    assert llm_calls == 1
    assert "Latest Session 1" in b1["last_covered"]
    assert "Cell Membrane" in b1["weak_areas"]
    assert "Plant Cell Wall" in b1["weak_areas"]
    assert "Cell Membrane" in b1["focus_concepts"]

    # 2. Second request within 5 minutes returns cached response (cached=True, 0 new LLM calls)
    r2 = client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["th_a"])
    assert r2.status_code == 200
    b2 = r2.json()
    assert b2["cached"] is True
    assert b2["generated_at"] == b1["generated_at"]
    assert llm_calls == 1

    # 3. Simulate 5 minutes + 1 second passing -> cache expires and regenerates (cached=False, llm_calls == 2)
    key = (str(w["t_a_id"]), str(w["s_1_id"]))
    personalization.briefing_cache._entries[key].expires_at = 0.0
    r3 = client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["th_a"])
    assert r3.status_code == 200
    assert r3.json()["cached"] is False
    assert llm_calls == 2

    # 4. Posting a new session log changes the student's data signature -> next briefing call regenerates immediately!
    post_sess = client.post(
        f"/teacher/students/{w['s_1_id']}/sessions",
        headers=w["th_a"],
        json={"notes": "Brand new session: drilled osmosis diagrams.", "tags": ["osmosis"]},
    )
    assert post_sess.status_code == 201
    r4 = client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["th_a"])
    assert r4.status_code == 200
    b4 = r4.json()
    assert b4["cached"] is False
    assert llm_calls == 3
    assert "Brand new session" in b4["last_covered"]

    # 5. Tenant & role isolation: Teacher B gets 404 with 0 LLM calls; Student gets 403
    assert client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["th_b"]).status_code == 404
    assert client.get(f"/teacher/students/{w['s_2_id']}/briefing", headers=w["th_a"]).status_code == 404
    assert llm_calls == 3
    assert client.get(f"/teacher/students/{w['s_1_id']}/briefing", headers=w["sh_1"]).status_code == 403
    
def test_phase5_6_check_runs_clean_and_rolls_back(session_factory):
    from types import SimpleNamespace
    from sqlalchemy import func, select
    from app.db import phase5_6_check

    with session_factory() as db:
        w = _setup_briefing_world(db)
        users_before = db.scalar(select(func.count()).select_from(User))
        logs_before = db.scalar(select(func.count()).select_from(SessionLog))
        engine = db.get_bind()

    opts = SimpleNamespace(book=None, skip_model=True, allow_fake=True)
    lines, fails = phase5_6_check.run(engine, opts)
    output = "\n".join(lines)
    assert fails == 0, output
    assert "RESULT: 17 PASS, 0 FAIL" in output

    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(User)) == users_before
        assert db.scalar(select(func.count()).select_from(SessionLog)) == logs_before