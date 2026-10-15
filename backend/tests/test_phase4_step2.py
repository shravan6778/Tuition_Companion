"""Phase 4 Step 2 tests: Teacher-triggered test generation, room assignment linking, and tenant isolation."""
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, Role, User


def _seed_world(db):
    t1 = User(supertokens_user_id="st-t1-p4s2", name="Teacher 1", username="t1p4s2", phone="9200000001", role=Role.teacher)
    t2 = User(supertokens_user_id="st-t2-p4s2", name="Teacher 2", username="t2p4s2", phone="9200000002", role=Role.teacher)
    s1 = User(supertokens_user_id="st-s1-p4s2", name="Student 1", username="s1p4s2", phone="9200000003", role=Role.student, link_code="P4S2CD01")
    s2 = User(supertokens_user_id="st-s2-p4s2", name="Student 2", username="s2p4s2", phone="9200000004", role=Role.student, link_code="P4S2CD02")
    s3 = User(supertokens_user_id="st-s3-p4s2", name="Student 3", username="s3p4s2", phone="9200000005", role=Role.student, link_code="P4S2CD03")
    db.add_all([t1, t2, s1, s2, s3])
    db.flush()

    book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
    private_t2 = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="Private", is_reference=False, owner_teacher_id=t2.id)
    db.add_all([book, private_t2])
    db.flush()

    ch = Chapter(book_id=book.id, title="Atoms and Molecules", sequence_num=1, status=ChapterStatus.READY)
    priv_ch = Chapter(book_id=private_t2.id, title="Secret Chapter", sequence_num=1, status=ChapterStatus.READY)
    db.add_all([ch, priv_ch])
    db.flush()

    p1 = Page(chapter_id=ch.id, page_number=1, content_text="Law of conservation of mass states that mass can neither be created nor destroyed in a chemical reaction.")
    p2 = Page(chapter_id=ch.id, page_number=2, content_text="Law of constant proportions states that in a chemical substance the elements are always present in definite proportions by mass.")
    p3 = Page(chapter_id=ch.id, page_number=3, content_text="An atom is the smallest particle of an element that retains its chemical properties, and molecules are groups of atoms.")
    priv_p = Page(chapter_id=priv_ch.id, page_number=1, content_text="Private teacher 2 content on isotopes and isobars.")
    db.add_all([p1, p2, p3, priv_p])
    db.flush()

    c1 = Concept(page_id=p1.id, name="Conservation of Mass", description="Mass is conserved in reactions", name_key="conservation mass", is_canonical=True, position=0)
    c2 = Concept(page_id=p2.id, name="Constant Proportions", description="Definite mass ratios", name_key="constant proportions", is_canonical=True, position=0)
    c3 = Concept(page_id=p3.id, name="Atomic Theory", description="Atoms form molecules", name_key="atomic theory", is_canonical=True, position=0)
    priv_c = Concept(page_id=priv_p.id, name="Private Concept", description="Secret", name_key="private concept", is_canonical=True, position=0)
    db.add_all([c1, c2, c3, priv_c])
    db.flush()

    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c2.id, prerequisite_id=c1.id, source="llm"))
    db.add(ConceptEdge(chapter_id=ch.id, concept_id=c3.id, prerequisite_id=c2.id, source="llm"))

    result = {
        "t1": {"Authorization": f"Bearer {t1.supertokens_user_id}"},
        "t2": {"Authorization": f"Bearer {t2.supertokens_user_id}"},
        "s1": {"Authorization": f"Bearer {s1.supertokens_user_id}"},
        "s2": {"Authorization": f"Bearer {s2.supertokens_user_id}"},
        "s3": {"Authorization": f"Bearer {s3.supertokens_user_id}"},
        "book_id": str(book.id),
        "ch_id": str(ch.id),
        "concept_ids": [str(c1.id), str(c2.id), str(c3.id)],
        "private_t2_id": str(private_t2.id),
        "priv_ch_id": str(priv_ch.id),
        "priv_c_id": str(priv_c.id),
    }
    db.commit()
    return result


def test_teacher_generates_quiz_and_assigns_to_room_with_tenant_isolation(client, session_factory):
    with session_factory() as db:
        w = _seed_world(db)

    t1, t2, s1, s2, s3 = w["t1"], w["t2"], w["s1"], w["s2"], w["s3"]
    book_id, ch_id = w["book_id"], w["ch_id"]

    # T1 creates a room; S1 and S3 join T1's room, S1 links the book (S3 does not link the book)
    room_res = client.post("/teacher/rooms", headers=t1, json={"name": "Class 9A", "room_type": "single_class"})
    assert room_res.status_code == 201
    room = room_res.json()

    client.post("/student/rooms/join", headers=s1, json={"join_code": room["join_code"]})
    client.post("/student/rooms/join", headers=s3, json={"join_code": room["join_code"]})
    client.post(f"/student/books/{book_id}/link", headers=s1)

    # T1 generates a Short (10-question) chapter quiz and assigns it directly to the room
    gen = client.post(
        "/teacher/quizzes/generate",
        headers=t1,
        json={"book_id": book_id, "chapter_id": ch_id, "length": "short", "room_id": room["id"]},
    )
    assert gen.status_code == 201, gen.text
    quiz = gen.json()
    assert quiz["kind"] == "teacher"
    assert quiz["question_count"] == 10
    assert quiz["assignment_id"] is not None
    assert len(quiz["questions"]) == 10

    # Question mix: 5 recall, 3 application, 2 cross_concept
    qtypes = [q["question_type"] for q in quiz["questions"]]
    assert qtypes.count("recall") == 5
    assert qtypes.count("application") == 3
    assert qtypes.count("cross_concept") == 2

    # Teacher view includes the answer keys and explanations for review
    for q in quiz["questions"]:
        assert q["status"] == "ready"
        assert q["explanation"]
        if q["answer_format"] == "mcq":
            assert q["correct_index"] in (0, 1, 2, 3)
        else:
            assert q["expected_answer"]

    # Student S1 (in the room + book linked) sees the quiz in GET /student/quizzes
    s1_list = client.get("/student/quizzes", headers=s1).json()
    assert [q["id"] for q in s1_list] == [quiz["id"]]

    # Student S1 reading the quiz NEVER receives the answer key before submission
    s1_quiz = client.get(f"/student/quizzes/{quiz['id']}", headers=s1).json()
    for q in s1_quiz["questions"]:
        assert q["correct_index"] is None
        assert q["expected_answer"] is None
        assert q["explanation"] is None

    # Tenancy: S3 (same room, book NOT linked) and S2 (not in room) see nothing and get 404 on the quiz
    assert client.get("/student/quizzes", headers=s3).json() == []
    assert client.get(f"/student/quizzes/{quiz['id']}", headers=s3).status_code == 404
    assert client.get(f"/student/quizzes/{quiz['id']}", headers=s2).status_code == 404

    # Tenancy: Teacher 2 gets 404 trying to view, assign, or delete Teacher 1's quiz
    assert client.get(f"/teacher/quizzes/{quiz['id']}", headers=t2).status_code == 404
    assert client.post(f"/teacher/quizzes/{quiz['id']}/assign", headers=t2, json={"room_id": room["id"]}).status_code == 404
    assert client.delete(f"/teacher/quizzes/{quiz['id']}", headers=t2).status_code == 404

    # Tenancy: Teacher 1 gets 404 trying to generate a quiz from Teacher 2's private book or concept
    priv_res = client.post(
        "/teacher/quizzes/generate",
        headers=t1,
        json={"book_id": w["private_t2_id"], "chapter_id": w["priv_ch_id"], "length": "short"},
    )
    assert priv_res.status_code == 404
    foreign_concept_res = client.post(
        "/teacher/quizzes/generate",
        headers=t1,
        json={"book_id": book_id, "concept_ids": [w["priv_c_id"]], "length": "short"},
    )
    assert foreign_concept_res.status_code == 404


def test_teacher_concept_level_quiz_and_separate_assign_endpoint(client, session_factory):
    with session_factory() as db:
        w = _seed_world(db)

    t1, s1 = w["t1"], w["s1"]
    book_id = w["book_id"]
    cids = w["concept_ids"][:2]

    room = client.post("/teacher/rooms", headers=t1, json={"name": "Class 9B", "room_type": "single_class"}).json()
    client.post("/student/rooms/join", headers=s1, json={"join_code": room["join_code"]})
    client.post(f"/student/books/{book_id}/link", headers=s1)

    # Generate an unassigned Medium (20-question) concept-scoped quiz first
    gen = client.post(
        "/teacher/quizzes/generate",
        headers=t1,
        json={"book_id": book_id, "concept_ids": cids, "length": "medium", "title": "Laws of Chemical Combination Test"},
    )
    assert gen.status_code == 201, gen.text
    quiz = gen.json()
    assert quiz["question_count"] == 20
    assert quiz["assignment_id"] is None
    assert len(quiz["questions"]) == 20

    # Before assigning, S1 cannot see it yet
    assert client.get(f"/student/quizzes/{quiz['id']}", headers=s1).status_code == 404

    # Teacher assigns it to the room via POST /teacher/quizzes/{id}/assign
    assigned = client.post(
        f"/teacher/quizzes/{quiz['id']}/assign",
        headers=t1,
        json={"room_id": room["id"]},
    )
    assert assigned.status_code == 200
    assert assigned.json()["assignment_id"] is not None

    # Now S1 sees it
    assert client.get(f"/student/quizzes/{quiz['id']}", headers=s1).status_code == 200