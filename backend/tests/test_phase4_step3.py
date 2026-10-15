"""Phase 4 Step 3 tests: Student self-triggered practice quizzes weighted toward weak and at-risk concepts."""
from app.assessment import mastery
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, Role, User


def _seed_practice_world(db):
    t1 = User(supertokens_user_id="st-t1-p4s3", name="Teacher 1", username="t1p4s3", phone="9300000001", role=Role.teacher)
    s1 = User(supertokens_user_id="st-s1-p4s3", name="Student 1", username="s1p4s3", phone="9300000002", role=Role.student, link_code="P4S3CD01")
    s2 = User(supertokens_user_id="st-s2-p4s3", name="Student 2", username="s2p4s3", phone="9300000003", role=Role.student, link_code="P4S3CD02")
    db.add_all([t1, s1, s2])
    db.flush()

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    priv_book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="Private", is_reference=False, owner_teacher_id=t1.id)
    db.add_all([book, priv_book])
    db.flush()

    ch = Chapter(book_id=book.id, title="Work and Energy", sequence_num=1, status=ChapterStatus.READY)
    priv_ch = Chapter(book_id=priv_book.id, title="Private Chapter", sequence_num=1, status=ChapterStatus.READY)
    db.add_all([ch, priv_ch])
    db.flush()

    pages = []
    for i in range(1, 11):
        p = Page(
            chapter_id=ch.id,
            page_number=i,
            content_text=f"Page {i} explains concept {i} in Work and Energy with clear physical definitions and formulas.",
        )
        pages.append(p)
    priv_p = Page(chapter_id=priv_ch.id, page_number=1, content_text="Private teacher page about hidden energy concepts.")
    db.add_all(pages + [priv_p])
    db.flush()

    concepts = []
    for i, p in enumerate(pages, start=1):
        c = Concept(
            page_id=p.id,
            name=f"Energy Concept {i}",
            description=f"Definition and formula for Energy Concept {i}",
            name_key=f"energy concept {i}",
            is_canonical=True,
            position=0,
        )
        concepts.append(c)
    priv_c = Concept(page_id=priv_p.id, name="Private Concept", description="Hidden", name_key="private concept", is_canonical=True, position=0)
    db.add_all(concepts + [priv_c])
    db.flush()

    # Prerequisite chain: Concept 4 depends on Concept 1 (weak), Concept 5 depends on Concept 2 (weak)
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=concepts[3].id, prerequisite_id=concepts[0].id, source="llm"))
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=concepts[4].id, prerequisite_id=concepts[1].id, source="llm"))
    db.flush()

    # Record mastery for S1:
    # - Concept 1 (score 0.0) and Concept 2 (score 0.5) are WEAK (< 0.6) -> propagates AT_RISK to Concept 4 and Concept 5
    # - Concept 3 (score 1.0) is OK
    # - Concepts 6..10 are untested revision concepts
    mastery.record_check(
        db,
        student_id=s1.id,
        check_id=None,
        assignment_id=None,
        results={
            concepts[0].id: (2, 0),  # 0.0 -> weak
            concepts[1].id: (2, 1),  # 0.5 -> weak
            concepts[2].id: (2, 2),  # 1.0 -> ok
        },
    )

    out = {
        "s1": {"Authorization": f"Bearer {s1.supertokens_user_id}"},
        "s2": {"Authorization": f"Bearer {s2.supertokens_user_id}"},
        "book_id": str(book.id),
        "ch_id": str(ch.id),
        "priv_book_id": str(priv_book.id),
        "priv_ch_id": str(priv_ch.id),
        "weak_ids": {str(concepts[0].id), str(concepts[1].id)},
        "at_risk_ids": {str(concepts[3].id), str(concepts[4].id)},
        "revision_ids": {str(c.id) for c in [concepts[2]] + concepts[5:]},
    }
    db.commit()
    return out


def test_student_practice_quiz_weights_60_weak_20_at_risk_20_revision(client, session_factory):
    with session_factory() as db:
        w = _seed_practice_world(db)

    s1, s2 = w["s1"], w["s2"]
    # Link official book for S1
    client.post(f"/student/books/{w['book_id']}/link", headers=s1)

    # S1 generates a default (10-question) practice quiz
    res = client.post("/student/practice/generate", headers=s1, json={"book_id": w["book_id"]})
    assert res.status_code == 201, res.text
    quiz = res.json()

    assert quiz["kind"] == "practice"
    assert quiz["question_count"] == 10
    assert len(quiz["questions"]) == 10

    # Verify 60% weak (6 questions), 20% at_risk (2 questions), 20% revision (2 questions)
    q_cids = [q["concept_id"] for q in quiz["questions"]]
    weak_count = sum(cid in w["weak_ids"] for cid in q_cids)
    at_risk_count = sum(cid in w["at_risk_ids"] for cid in q_cids)
    revision_count = sum(cid in w["revision_ids"] for cid in q_cids)

    assert weak_count == 6
    assert at_risk_count == 2
    assert revision_count == 2

    # Question difficulty mix is still 5 recall, 3 application, 2 cross_concept
    qtypes = [q["question_type"] for q in quiz["questions"]]
    assert qtypes.count("recall") == 5
    assert qtypes.count("application") == 3
    assert qtypes.count("cross_concept") == 2

    # No answer key or explanation is leaked to the student before submission
    for q in quiz["questions"]:
        assert q["status"] == "ready"
        assert q["correct_index"] is None
        assert q["expected_answer"] is None
        assert q["explanation"] is None

    # S1 sees the practice quiz in GET /student/quizzes; S2 gets 404
    assert any(item["id"] == quiz["id"] for item in client.get("/student/quizzes", headers=s1).json())
    assert client.get(f"/student/quizzes/{quiz['id']}", headers=s2).status_code == 404


def test_student_practice_spillover_when_no_weak_concepts_and_tenancy_guards(client, session_factory):
    with session_factory() as db:
        w = _seed_practice_world(db)

    s1, s2 = w["s1"], w["s2"]

    # S2 has NOT linked any book yet -> 409 when asking for a general practice quiz, 404 for an unlinked book/chapter
    assert client.post("/student/practice/generate", headers=s2, json={}).status_code == 409
    assert client.post("/student/practice/generate", headers=s2, json={"book_id": w["book_id"]}).status_code == 404
    assert client.post("/student/practice/generate", headers=s1, json={"book_id": w["priv_book_id"]}).status_code == 404
    assert client.post("/student/practice/generate", headers=s1, json={"chapter_id": w["priv_ch_id"]}).status_code == 404

    # Now S2 links the official book (S2 has 0 weak and 0 at-risk concepts -> all 10 slots spill over to revision)
    client.post(f"/student/books/{w['book_id']}/link", headers=s2)
    res = client.post("/student/practice/generate", headers=s2, json={"chapter_id": w["ch_id"]})
    assert res.status_code == 201, res.text
    quiz = res.json()
    assert quiz["question_count"] == 10
    assert len(quiz["questions"]) == 10
    assert len({q["concept_id"] for q in quiz["questions"]}) == 10