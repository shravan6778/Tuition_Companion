import uuid

from app.assessment import mastery
from app.models import Book, Chapter, ChapterStatus, Concept, ConceptEdge, Page, Role


def _seed_graph_and_events(db_session, student):
    book = Book(
        board="CBSE",
        class_name="Class 9",
        subject="Mathematics",
        publisher="NCERT",
        is_reference=True,
    )
    db_session.add(book)
    db_session.flush()

    chapter = Chapter(
        book_id=book.id,
        title="Linear Equations",
        sequence_num=1,
        status=ChapterStatus.READY,
    )
    db_session.add(chapter)
    db_session.flush()

    page = Page(
        chapter_id=chapter.id,
        page_number=1,
        content_text="Variables, linear equations in two variables, and graphing lines.",
    )
    db_session.add(page)
    db_session.flush()

    c_prereq = Concept(
        page_id=page.id,
        name="Variables and Constants",
        description="Basic algebraic variables",
        name_key="variables and constants",
        position=0,
        is_canonical=True,
    )
    c_dep = Concept(
        page_id=page.id,
        name="Graph of a Linear Equation",
        description="Plotting linear equations",
        name_key="graph of a linear equation",
        position=1,
        is_canonical=True,
    )
    c_ok = Concept(
        page_id=page.id,
        name="Solution of an Equation",
        description="Finding roots",
        name_key="solution of an equation",
        position=2,
        is_canonical=True,
    )
    db_session.add_all([c_prereq, c_dep, c_ok])
    db_session.flush()

    db_session.add(
        ConceptEdge(
            chapter_id=chapter.id,
            concept_id=c_dep.id,
            prerequisite_id=c_prereq.id,
            source="llm",
        )
    )
    db_session.flush()

    # Record a check where c_prereq is weak (0/2) and c_ok is strong (2/2); c_dep becomes at_risk via propagation
    mastery.record_check(
        db_session,
        student_id=student.id,
        check_id=None,
        assignment_id=None,
        results={
            c_prereq.id: (2, 0),
            c_ok.id: (2, 2),
        },
    )
    db_session.commit()
    return c_prereq, c_dep, c_ok


def test_parent_progress_unlinked_child_returns_404(client, make_user, as_user):
    parent = make_user(Role.parent)
    unlinked_student = make_user(Role.student)

    as_user(parent)
    res = client.get(f"/parent/children/{unlinked_student.id}/progress?days=7")
    assert res.status_code == 404

    # Unknown UUID also returns 404
    res_unknown = client.get(f"/parent/children/{uuid.uuid4()}/progress?days=7")
    assert res_unknown.status_code == 404


def test_parent_progress_forbidden_for_student_and_teacher(client, make_user, as_user):
    student = make_user(Role.student)
    teacher = make_user(Role.teacher)

    as_user(student)
    assert client.get(f"/parent/children/{student.id}/progress").status_code == 403

    as_user(teacher)
    assert client.get(f"/parent/children/{student.id}/progress").status_code == 403


def test_student_approval_required_before_parent_can_view_progress(client, db_session, make_user, as_user):
    parent = make_user(Role.parent)
    student = make_user(Role.student)
    _seed_graph_and_events(db_session, student)

    # 1. Parent submits the 8-character link code -> link starts as 'pending'
    as_user(parent)
    link_res = client.post("/parent/children/link", json={"link_code": student.link_code})
    assert link_res.status_code == 200
    assert link_res.json()["status"] == "pending"

    # 2. Before student approval, parent gets 404 on progress and child is not in approved children list
    assert client.get("/parent/children").json() == []
    assert client.get(f"/parent/children/{student.id}/progress?days=7").status_code == 404

    # 3. Another student cannot approve this student's link request
    other_student = make_user(Role.student)
    as_user(other_student)
    assert client.get("/student/parent-links").json() == []

    # 4. Student lists pending parent link requests and approves it
    as_user(student)
    links = client.get("/student/parent-links").json()
    assert len(links) == 1
    assert links[0]["parent_id"] == str(parent.id)
    assert links[0]["status"] == "pending"
    link_id = links[0]["id"]

    approve_res = client.post(f"/student/parent-links/{link_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
    assert approve_res.json()["approved_at"] is not None

    # 5. Now the parent sees the child and can fetch their progress
    as_user(parent)
    children = client.get("/parent/children").json()
    assert len(children) == 1
    assert children[0]["id"] == str(student.id)

    prog_res = client.get(f"/parent/children/{student.id}/progress?days=14")
    assert prog_res.status_code == 200
    body = prog_res.json()

    assert body["weak"] == 1
    assert body["at_risk"] == 1
    assert body["ok"] == 1

    assert body["digest"]["concepts_covered"] == 2
    assert body["digest"]["checks_taken"] >= 1
    assert body["digest"]["quizzes_taken"] == 0
    assert body["digest"]["pass_rate"] == 0.5
    assert body["digest"]["flagged_this_week"] == 2

    weak_names = {w["concept_name"]: w for w in body["weak_areas"]}
    assert "Variables and Constants" in weak_names
    assert weak_names["Variables and Constants"]["status"] == "weak"
    assert "Graph of a Linear Equation" in weak_names
    assert weak_names["Graph of a Linear Equation"]["status"] == "at_risk"
    assert "depends on Variables and Constants" in weak_names["Graph of a Linear Equation"]["reason"]

    assert len(body["recent"]) == 3

    # 6. Student can revoke the parent link at any time -> parent immediately gets 404 again
    as_user(student)
    del_res = client.delete(f"/student/parent-links/{link_id}")
    assert del_res.status_code == 204

    as_user(parent)
    assert client.get(f"/parent/children/{student.id}/progress").status_code == 404


def test_parent_progress_is_strictly_read_only(client, db_session, make_user, as_user):
    parent = make_user(Role.parent)
    student = make_user(Role.student)
    _seed_graph_and_events(db_session, student)

    as_user(parent)
    client.post("/parent/children/link", json={"link_code": student.link_code})

    as_user(student)
    link_id = client.get("/student/parent-links").json()[0]["id"]
    client.post(f"/student/parent-links/{link_id}/approve")

    as_user(parent)
    url = f"/parent/children/{student.id}/progress"
    for method in ("post", "put", "patch", "delete"):
        res = client.request(method.upper(), url, json={"weak": 0})
        assert res.status_code == 405

    # Parent cannot call student or teacher write endpoints either
    assert client.post("/student/doubts", json={"text": "test"}).status_code == 403
    assert client.post("/teacher/rooms", json={"name": "R", "room_type": "single_class"}).status_code == 403