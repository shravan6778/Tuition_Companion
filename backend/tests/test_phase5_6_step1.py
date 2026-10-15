"""Tests for Phase 5 & 6 Step 1:
  * `GET /teacher/students/{id}/trends` longitudinal trend analytics.
  * Accurate categorization of `improving`, `declining`, `stable`, and `insufficient_data` concepts and chapters
    over synthetic timestamped `mastery_events` across the last 4 weeks.
  * Explainable `weak` and `at_risk` flags included in the response.
  * Strict tenant isolation: a teacher gets 404 for a student not in their room, and never sees events from another
    teacher's private book."""
from datetime import datetime, timedelta, timezone

from app.assessment import mastery
from app.models import (
    Book, Chapter, ChapterStatus, Concept, ConceptEdge, MasteryEvent, Page, Role, Room, RoomMember, RoomType, User,
)


def _setup_trends_world(db):
    now = datetime.now(timezone.utc)
    t_a = User(supertokens_user_id="st-t-trend-a", name="Teacher A", username="teacher_trend_a", phone="9100000001", role=Role.teacher)
    t_b = User(supertokens_user_id="st-t-trend-b", name="Teacher B", username="teacher_trend_b", phone="9100000002", role=Role.teacher)
    s_1 = User(supertokens_user_id="st-s-trend-1", name="Student 1", username="student_trend_1", phone="9100000003", role=Role.student, link_code="TREND001")
    s_2 = User(supertokens_user_id="st-s-trend-2", name="Student 2", username="student_trend_2", phone="9100000004", role=Role.student, link_code="TREND002")
    db.add_all([t_a, t_b, s_1, s_2])
    db.flush()

    room_a = Room(teacher_id=t_a.id, name="Class 9 Maths", room_type=RoomType.single_class, join_code="TRENDA")
    room_b = Room(teacher_id=t_b.id, name="Other Room", room_type=RoomType.single_class, join_code="TRENDB")
    db.add_all([room_a, room_b])
    db.flush()

    db.add(RoomMember(room_id=room_a.id, user_id=s_1.id))
    db.add(RoomMember(room_id=room_b.id, user_id=s_2.id))

    book = Book(board="CBSE", class_name="Class 9", subject="Mathematics", publisher="NCERT", is_reference=True)
    private_b = Book(board="CBSE", class_name="Class 9", subject="Secret", publisher="Private", is_reference=False, owner_teacher_id=t_b.id)
    db.add_all([book, private_b])
    db.flush()

    ch = Chapter(book_id=book.id, title="Algebra & Factoring", sequence_num=1, status=ChapterStatus.READY)
    ch_priv = Chapter(book_id=private_b.id, title="Secret Chapter", sequence_num=1, status=ChapterStatus.READY)
    db.add_all([ch, ch_priv])
    db.flush()

    page = Page(chapter_id=ch.id, page_number=1, content_text="Factoring, Linear Equations, Quadratic Roots, and Polynomial Degree.")
    page_priv = Page(chapter_id=ch_priv.id, page_number=1, content_text="Secret content on private page.")
    db.add_all([page, page_priv])
    db.flush()

    c_improving = Concept(page_id=page.id, name="Factoring", description="Factoring expressions", name_key="factoring", position=0, is_canonical=True)
    c_declining = Concept(page_id=page.id, name="Linear Equations", description="Solving linear equations", name_key="linear equations", position=1, is_canonical=True)
    c_dependent = Concept(page_id=page.id, name="Quadratic Roots", description="Depends on Linear Equations", name_key="quadratic roots", position=2, is_canonical=True)
    c_stable = Concept(page_id=page.id, name="Polynomial Degree", description="Highest power", name_key="polynomial degree", position=3, is_canonical=True)
    c_priv = Concept(page_id=page_priv.id, name="Private Concept", description="Hidden", name_key="private concept", position=0, is_canonical=True)
    db.add_all([c_improving, c_declining, c_dependent, c_stable, c_priv])
    db.flush()

    # Quadratic Roots depends on Linear Equations
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c_dependent.id, prerequisite_id=c_declining.id, source="llm"))
    db.flush()

    def add_measured(concept, kind, score, days_ago):
        ev = MasteryEvent(
            student_id=s_1.id,
            concept_id=concept.id,
            concept_name=concept.name,
            kind=kind,
            score=score,
            asked=2,
            correct=int(round(score * 2)),
            created_at=now - timedelta(days=days_ago),
        )
        db.add(ev)
        db.flush()

    # 1. c_improving ("Factoring"): 25 days ago 0.0 -> 18 days ago 0.5 -> 2 days ago 1.0 -> today 1.0
    # Rolling score (last 3: 0.5, 1.0, 1.0) = 0.5*1.0 + 0.3*1.0 + 0.2*0.5 = 0.90 (OK, improving vs baseline 0.25)
    add_measured(c_improving, mastery.CHECK, 0.0, days_ago=25)
    add_measured(c_improving, mastery.QUIZ, 0.5, days_ago=18)
    add_measured(c_improving, mastery.CHECK, 1.0, days_ago=2)
    add_measured(c_improving, mastery.QUIZ, 1.0, days_ago=0)

    # 2. c_declining ("Linear Equations"): 24 days ago 1.0 -> 16 days ago 1.0 -> 3 days ago 0.5 -> today 0.0
    # Rolling score (last 3: 1.0, 0.5, 0.0) = 0.5*0.0 + 0.3*0.5 + 0.2*1.0 = 0.35 (WEAK, declining vs baseline 1.0)
    add_measured(c_declining, mastery.CHECK, 1.0, days_ago=24)
    add_measured(c_declining, mastery.QUIZ, 1.0, days_ago=16)
    add_measured(c_declining, mastery.CHECK, 0.5, days_ago=3)
    # Record final failing check via record_check so it also writes the propagated at_risk event on c_dependent!
    mastery.record_check(db, s_1.id, None, None, {c_declining.id: (2, 0)})

    # 3. c_stable ("Polynomial Degree"): 20 days ago 1.0 -> 1 day ago 1.0 (STABLE)
    add_measured(c_stable, mastery.CHECK, 1.0, days_ago=20)
    add_measured(c_stable, mastery.QUIZ, 1.0, days_ago=1)

    # 4. Event on Teacher B's private book (must be invisible to Teacher A)
    add_measured(c_priv, mastery.CHECK, 0.0, days_ago=1)

    # Capture IDs and headers BEFORE db.commit() because session_factory has expire_on_commit=True
    result = {
        "s_1_id": s_1.id,
        "s_2_id": s_2.id,
        "th_a": {"Authorization": f"Bearer {t_a.supertokens_user_id}"},
        "th_b": {"Authorization": f"Bearer {t_b.supertokens_user_id}"},
        "sh_1": {"Authorization": f"Bearer {s_1.supertokens_user_id}"},
        "concept_ids": {
            "improving": c_improving.id,
            "declining": c_declining.id,
            "dependent": c_dependent.id,
            "stable": c_stable.id,
            "private": c_priv.id,
        },
    }
    db.commit()
    return result


def test_teacher_student_trends_categorization_and_weekly_buckets(client, session_factory):
    with session_factory() as db:
        w = _setup_trends_world(db)

    res = client.get(f"/teacher/students/{w['s_1_id']}/trends", headers=w["th_a"])
    assert res.status_code == 200, res.text
    body = res.json()

    assert body["student_id"] == str(w["s_1_id"])
    assert body["weeks_window"] == 4
    assert body["weak_count"] == 1
    assert body["at_risk_count"] == 1
    assert body["ok_count"] == 2
    assert body["improving_count"] == 1
    assert body["declining_count"] == 1
    assert body["stable_count"] == 1

    by_name = {c["concept_name"]: c for c in body["concepts"]}
    assert "Private Concept" not in by_name  # Teacher B's private book is filtered out

    # Check Improving concept
    imp = by_name["Factoring"]
    assert imp["status"] == "ok"
    assert imp["current_score"] == 0.9
    assert imp["baseline_score"] == 0.25
    assert imp["delta"] == 0.65
    assert imp["trend"] == "improving"
    assert imp["reason"] is None

    # Check Declining (Weak) concept + explainable direct reason
    dec = by_name["Linear Equations"]
    assert dec["status"] == "weak"
    assert dec["current_score"] == 0.35
    assert dec["baseline_score"] == 1.0
    assert dec["delta"] == -0.65
    assert dec["trend"] == "declining"
    assert dec["reason"] is not None and "tested weak directly" in dec["reason"]

    # Check Propagated At-Risk concept + explainable prerequisite reason
    dep = by_name["Quadratic Roots"]
    assert dep["status"] == "at_risk"
    assert dep["current_score"] is None
    assert dep["trend"] == "insufficient_data"
    assert dep["reason"] == "flagged because it depends on Linear Equations, which tested weak"
    assert dep["flagged_by_concept_id"] == str(w["concept_ids"]["declining"])

    # Check Stable concept
    stb = by_name["Polynomial Degree"]
    assert stb["status"] == "ok"
    assert stb["current_score"] == 1.0
    assert stb["baseline_score"] == 1.0
    assert stb["delta"] == 0.0
    assert stb["trend"] == "stable"

    # Check 4-week subject & chapter buckets
    assert len(body["subjects"]) == 1
    math_subj = body["subjects"][0]
    assert math_subj["subject"] == "Mathematics"
    assert len(math_subj["weeks"]) == 4
    assert len(math_subj["chapters"]) == 1
    assert math_subj["chapters"][0]["chapter_title"] == "Algebra & Factoring"
    assert len(math_subj["chapters"][0]["weeks"]) == 4


def test_trends_tenant_and_role_isolation(client, session_factory):
    with session_factory() as db:
        w = _setup_trends_world(db)

    # Teacher A cannot view Student 2 (in Teacher B's room) -> 404
    r_other_student = client.get(f"/teacher/students/{w['s_2_id']}/trends", headers=w["th_a"])
    assert r_other_student.status_code == 404

    # Teacher B cannot view Student 1 (in Teacher A's room) -> 404
    r_tb = client.get(f"/teacher/students/{w['s_1_id']}/trends", headers=w["th_b"])
    assert r_tb.status_code == 404

    # Student cannot call teacher trends endpoint -> 403
    r_student_role = client.get(f"/teacher/students/{w['s_1_id']}/trends", headers=w["sh_1"])
    assert r_student_role.status_code == 403