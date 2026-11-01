"""Manual (school homework) tasks: no book, no AI-written check, verified by a photo or spoken answer + the teacher's verdict.

World: one teacher with a room, two students in it (A and B), and a second teacher who owns nothing here.
"""
import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.assessment import checks
from app.core.config import settings
from app.models import Assignment, AssignmentCheck, ManualSubmission, Role
from tests.test_book_access import join_room_of, make_user

PNG = b"\x89PNG\r\n\x1a\n" + b"fake-image-bytes" * 8
SPOKEN = "the answer to question three is twelve because six times two"


@pytest.fixture()
def world(client, session_factory):
    _, th = make_user(session_factory, Role.teacher, "teachera")
    _, other = make_user(session_factory, Role.teacher, "teacherb")
    student_a, sa = make_user(session_factory, Role.student, "studenta")
    student_b, sb = make_user(session_factory, Role.student, "studentb")
    room = join_room_of(client, session_factory, th, sa)
    outsider = make_user(session_factory, Role.student, "studentc")[1]  # in nobody's room
    return dict(th=th, other=other, sa=sa, sb=sb, outsider=outsider, a=student_a, b=student_b, room=room)


def create(client, w, **extra):
    body = dict(level="manual", subject="Hindi", title="Chapter 4 questions", description="Answer Q1 to Q5 in your notebook.",
                room_id=w["room"]["id"]) | extra
    return client.post("/teacher/assignments", json=body, headers=w["th"])


def hand_in_voice(client, w, task, text=SPOKEN, who="sa"):
    return client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "voice", "text": text}, headers=w[who])


def hand_in_photo(client, w, task, data=PNG, who="sa", **form):
    return client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "photo", **form},
                       files={"photo": ("work.png", data, "image/png")}, headers=w[who])


def review(client, w, sub, verdict, feedback=None, who="th"):
    return client.post(f"/teacher/submissions/{sub['id']}/review", json={"verdict": verdict, "feedback": feedback}, headers=w[who])


# ---- creating the task --------------------------------------------------------------------------------------------------

def test_a_manual_task_needs_no_book_and_stores_a_free_text_subject_and_description(client, session_factory, world):
    res = create(client, world)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["level"] == "manual" and body["subject"] == "Hindi" and body["description"] == "Answer Q1 to Q5 in your notebook."
    assert body["chapter_title"] is None and body["concept_count"] == 0 and body["item_count"] == 0
    assert body["pending_review"] == 0
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Assignment)) == 1


def test_a_manual_task_defaults_its_title_and_can_target_one_student(client, world):
    body = client.post("/teacher/assignments", headers=world["th"], json=dict(
        level="manual", subject="  Social   Studies ", student_id=str(world["a"].id))).json()
    assert body["title"] == "Social Studies homework" and body["subject"] == "Social Studies" and body["student_id"] == str(world["a"].id)


def test_manual_task_validation(client, world):
    assert create(client, world, subject="").status_code == 422                       # a subject is required
    assert create(client, world, subject="   ").status_code == 422
    assert create(client, world, book_id="7c1a0000-0000-4000-8000-000000000000").status_code == 422   # it has no book
    assert create(client, world, chapter_id="7c1a0000-0000-4000-8000-000000000000").status_code == 422
    assert create(client, world, concept_names=["Cell"]).status_code == 422
    assert create(client, world, items=[dict(kind="example", label="Example 1")]).status_code == 422
    assert client.post("/teacher/assignments", headers=world["th"], json=dict(
        level="manual", subject="Hindi", room_id=world["room"]["id"], student_id=str(world["a"].id))).status_code == 422  # one target only


def test_only_the_rooms_teacher_can_set_manual_work_there(client, world):
    assert create(client, world | {"th": world["other"]}).status_code == 404


def test_the_other_levels_still_need_a_book_and_refuse_the_manual_only_fields(client, world):
    no_book = client.post("/teacher/assignments", headers=world["th"], json=dict(level="chapter", room_id=world["room"]["id"]))
    assert no_book.status_code == 422 and "book" in no_book.json()["detail"].lower()
    subject_only = client.post("/teacher/assignments", headers=world["th"], json=dict(
        level="chapter", book_id="7c1a0000-0000-4000-8000-000000000000", room_id=world["room"]["id"], subject="Hindi"))
    assert subject_only.status_code == 422


def test_the_database_itself_refuses_a_manual_task_with_a_chapter_target(session_factory, world):
    with session_factory() as db:
        db.add(Assignment(teacher_id=world["a"].id, room_id=None, student_id=world["a"].id, subject="Hindi", level="manual",
                          title="x", chapter_title="Cells"))
        with pytest.raises(IntegrityError):
            db.commit()


# ---- /complete: no AI-generated check -----------------------------------------------------------------------------------

def test_complete_on_a_manual_task_opens_no_check_and_calls_no_model(client, session_factory, world, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("a manual task must never reach the check generator")
    monkeypatch.setattr(checks, "generate_question", boom)
    monkeypatch.setattr(checks, "plan_check", boom)
    task = create(client, world).json()
    res = client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"])
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["kind"] == "manual" and body["state"] == "todo" and body["can_submit"] is True and body["latest"] is None
    assert "questions" not in body
    again = client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"])  # idempotent
    assert again.status_code == 200
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(AssignmentCheck)) == 0


def test_the_check_service_itself_refuses_a_manual_task(session_factory, world, client):
    from fastapi import HTTPException
    from app.assessment import service
    task = create(client, world).json()
    with session_factory() as db:
        with pytest.raises(HTTPException) as err:
            service.start_check(db, db.get(type(world["a"]), world["a"].id), db.get(Assignment, __import__("uuid").UUID(task["id"])))
        assert err.value.status_code == 409


def test_complete_does_not_spend_the_check_rate_limit(client, world, monkeypatch):
    monkeypatch.setattr(settings, "rate_checks_per_hour", 1)
    task = create(client, world).json()
    for _ in range(3):
        assert client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"]).status_code == 200


def test_book_tasks_for_other_students_stay_invisible(client, world):
    task = create(client, world).json()
    assert client.post(f"/student/assignments/{task['id']}/complete", headers=world["outsider"]).status_code == 404


# ---- handing in: voice and photo ----------------------------------------------------------------------------------------

def test_a_spoken_answer_is_kept_as_text_and_moves_the_task_to_submitted(client, world):
    task = create(client, world).json()
    res = hand_in_voice(client, world, task)
    assert res.status_code == 201, res.text
    sub = res.json()
    assert sub["source"] == "voice" and sub["text"] == SPOKEN and sub["has_photo"] is False and sub["verdict"] is None
    done = client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"]).json()
    assert done["state"] == "submitted" and done["latest"]["id"] == sub["id"]
    mine = client.get(f"/student/assignments/{task['id']}", headers=world["sa"]).json()
    assert mine["manual_state"] == "submitted" and mine["pending_review"] is None


def test_a_spoken_answer_that_is_too_short_or_comes_with_a_photo_is_refused(client, world):
    task = create(client, world).json()
    assert hand_in_voice(client, world, task, text="yes ok").status_code == 422
    assert hand_in_voice(client, world, task, text="   ").status_code == 422
    mixed = client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "voice", "text": SPOKEN},
                        files={"photo": ("w.png", PNG, "image/png")}, headers=world["sa"])
    assert mixed.status_code == 422
    too_long = hand_in_voice(client, world, task, text="word " * (settings.manual_text_max_chars // 4))
    assert too_long.status_code == 422


def test_a_photo_is_checked_by_content_stored_and_never_sent_to_ocr(client, world, monkeypatch):
    import app.ocr as ocr
    monkeypatch.setattr(ocr, "get_ocr_provider", lambda: (_ for _ in ()).throw(AssertionError("no OCR for homework photos")))
    task = create(client, world).json()
    res = hand_in_photo(client, world, task, text="my notebook page")
    assert res.status_code == 201, res.text
    sub = res.json()
    assert sub["source"] == "photo" and sub["has_photo"] is True and sub["text"] == "my notebook page"
    back = client.get(f"/student/submissions/{sub['id']}/photo", headers=world["sa"])
    assert back.status_code == 200 and back.content == PNG and back.headers["content-type"] == "image/png"
    assert back.headers["cache-control"] == "private, no-store" and back.headers["x-content-type-options"] == "nosniff"


def test_a_photo_must_be_a_real_image_and_a_photo_submission_needs_one(client, world):
    task = create(client, world).json()
    assert hand_in_photo(client, world, task, data=b"just some text pretending to be a picture").status_code == 415
    assert hand_in_photo(client, world, task, data=b"%PDF-1.4 not an image").status_code == 415
    assert client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "photo"}, headers=world["sa"]).status_code == 422
    assert client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "email"}, headers=world["sa"]).status_code == 422


def test_an_oversized_photo_is_refused_before_it_is_stored(client, world, monkeypatch):
    monkeypatch.setattr(settings, "max_manual_photo_mb", 1)
    task = create(client, world).json()
    assert hand_in_photo(client, world, task, data=PNG + b"0" * (1024 * 1024)).status_code == 413


def test_hand_ins_are_rate_limited_per_student(client, world, monkeypatch):
    monkeypatch.setattr(settings, "rate_manual_submissions_per_hour", 2)
    task = create(client, world).json()
    assert hand_in_voice(client, world, task).status_code == 201
    assert hand_in_voice(client, world, task).status_code == 201
    assert hand_in_voice(client, world, task).status_code == 429
    assert hand_in_voice(client, world, task, who="sa").status_code == 429


def test_only_a_student_who_was_given_the_task_can_hand_in(client, world):
    task = create(client, world).json()
    assert hand_in_voice(client, world, task, who="outsider").status_code == 404
    assert hand_in_voice(client, world, task, who="sb").status_code == 404   # not in the room either
    assert client.post(f"/student/assignments/{task['id']}/submissions", data={"source": "voice", "text": SPOKEN},
                       headers=world["th"]).status_code == 403


def test_only_manual_tasks_take_a_hand_in(client, session_factory, world):
    with session_factory() as db:
        book_task = Assignment(teacher_id=world["a"].id, student_id=world["a"].id, subject="Science", level="subject", title="Whole book")
        db.add(book_task); db.commit(); db.refresh(book_task)
        task_id = str(book_task.id)
    res = client.post(f"/student/assignments/{task_id}/submissions", data={"source": "voice", "text": SPOKEN}, headers=world["sa"])
    assert res.status_code == 409


# ---- the teacher's side: seeing the work, the verdict ---------------------------------------------------------------------

def test_the_teacher_sees_each_students_work_with_a_pending_count_and_fetches_the_photo(client, world):
    task = create(client, world).json()
    voice = hand_in_voice(client, world, task).json()
    photo = hand_in_photo(client, world, task).json()
    listing = client.get(f"/teacher/assignments/{task['id']}/submissions", headers=world["th"]).json()
    assert {s["id"] for s in listing} == {voice["id"], photo["id"]} and listing[0]["student_name"] == "studenta"
    assert client.get("/teacher/assignments", params={"room_id": world["room"]["id"]}, headers=world["th"]).json()[0]["pending_review"] == 1
    shown = client.get(f"/teacher/submissions/{photo['id']}/photo", headers=world["th"])
    assert shown.status_code == 200 and shown.content == PNG
    assert client.get(f"/teacher/submissions/{voice['id']}/photo", headers=world["th"]).status_code == 404   # spoken: no photo


def test_another_teacher_cannot_see_review_or_download_anything(client, world):
    task = create(client, world).json()
    sub = hand_in_photo(client, world, task).json()
    other = world["other"]
    assert client.get(f"/teacher/assignments/{task['id']}/submissions", headers=other).status_code == 404
    assert client.get(f"/teacher/submissions/{sub['id']}/photo", headers=other).status_code == 404
    assert review(client, world, sub, "good", who="other").status_code == 404


def test_another_student_cannot_read_a_photo_or_the_history(client, world):
    task = create(client, world).json()
    sub = hand_in_photo(client, world, task).json()
    assert client.get(f"/student/submissions/{sub['id']}/photo", headers=world["sb"]).status_code == 404
    assert client.get(f"/student/assignments/{task['id']}/submissions", headers=world["sb"]).status_code == 404
    assert client.get(f"/teacher/submissions/{sub['id']}/photo", headers=world["sa"]).status_code == 403


def test_good_closes_the_task_and_stops_further_hand_ins(client, world):
    task = create(client, world).json()
    sub = hand_in_voice(client, world, task).json()
    res = review(client, world, sub, "good", "Well done")
    assert res.status_code == 200, res.text
    assert res.json()["verdict"] == "good" and res.json()["feedback"] == "Well done" and res.json()["reviewed_at"]
    done = client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"]).json()
    assert done["state"] == "good" and done["can_submit"] is False
    assert hand_in_voice(client, world, task).status_code == 409
    mine = client.get(f"/student/assignments/{task['id']}", headers=world["sa"]).json()
    assert mine["manual_state"] == "good" and mine["manual_feedback"] == "Well done"
    assert client.get("/teacher/assignments", params={"room_id": world["room"]["id"]}, headers=world["th"]).json()[0]["pending_review"] == 0


@pytest.mark.parametrize("verdict", ["needs_work", "redo"])
def test_needs_work_and_redo_reopen_the_task_and_every_attempt_is_kept(client, session_factory, world, verdict):
    task = create(client, world).json()
    first = hand_in_voice(client, world, task).json()
    assert review(client, world, first, verdict, "Show your working").status_code == 200
    state = client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"]).json()
    assert state["state"] == verdict and state["can_submit"] is True and state["latest"]["feedback"] == "Show your working"
    second = hand_in_photo(client, world, task)
    assert second.status_code == 201
    assert client.post(f"/student/assignments/{task['id']}/complete", headers=world["sa"]).json()["state"] == "submitted"
    history = client.get(f"/student/assignments/{task['id']}/submissions", headers=world["sa"]).json()
    assert [h["id"] for h in history] == [second.json()["id"], first["id"]]       # newest first, both kept
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ManualSubmission)) == 2


def test_only_the_newest_attempt_can_be_judged_and_a_verdict_can_be_changed(client, world):
    task = create(client, world).json()
    first = hand_in_voice(client, world, task).json()
    second = hand_in_voice(client, world, task).json()
    assert review(client, world, first, "good").status_code == 409                  # superseded
    assert review(client, world, second, "needs_work").status_code == 200
    changed = review(client, world, second, "good")
    assert changed.status_code == 200 and changed.json()["verdict"] == "good"


def test_the_verdict_must_be_one_of_the_three(client, world):
    task = create(client, world).json()
    sub = hand_in_voice(client, world, task).json()
    for bad in ("excellent", "", "GOOD", "pass"):
        assert review(client, world, sub, bad).status_code == 422
    assert client.post(f"/teacher/submissions/{sub['id']}/review", json={}, headers=world["th"]).status_code == 422
    assert review(client, world, sub, "good", "x" * 1001).status_code == 422


def test_a_room_task_is_judged_per_student(client, session_factory, world):
    _, sb = world["a"], world["sb"]
    # student B joins the same room
    room = world["room"]
    joined = client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sb)
    pending = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=world["th"]).json()
    assert joined.status_code == 202 and len(pending) == 1
    client.post(f"/teacher/rooms/{room['id']}/join-requests/{pending[0]['id']}/approve", headers=world["th"])
    task = create(client, world).json()
    mine = hand_in_voice(client, world, task).json()
    theirs = hand_in_voice(client, world, task, who="sb").json()
    assert client.get("/teacher/assignments", params={"room_id": room["id"]}, headers=world["th"]).json()[0]["pending_review"] == 2
    review(client, world, mine, "good")
    assert client.get(f"/student/assignments/{task['id']}", headers=sb).json()["manual_state"] == "submitted"
    assert client.get(f"/student/assignments/{task['id']}", headers=world["sa"]).json()["manual_state"] == "good"
    only_b = client.get(f"/teacher/assignments/{task['id']}/submissions", params={"student_id": str(world["b"].id)}, headers=world["th"]).json()
    assert [s["id"] for s in only_b] == [theirs["id"]]


# ---- things that must not apply to a homework task ------------------------------------------------------------------------

def test_the_doubt_button_does_not_apply_to_a_manual_task(client, world):
    task = create(client, world).json()
    res = client.post("/student/doubts", json={"text": "what is a noun", "assignment_id": task["id"]}, headers=world["sa"])
    assert res.status_code == 409 and "homework" in res.json()["detail"].lower()
    photo = client.post("/student/doubts/photo", data={"assignment_id": task["id"]}, files={"file": ("d.png", PNG, "image/png")}, headers=world["sa"])
    assert photo.status_code == 409


def test_a_manual_task_appears_in_todays_work_available_and_unresolved(client, world):
    task = create(client, world).json()
    row = client.get("/student/assignments", headers=world["sa"]).json()[0]
    assert row["id"] == task["id"] and row["available"] is True and row["resolved_book_id"] is None
    assert row["manual_state"] == "todo" and row["description"] == "Answer Q1 to Q5 in your notebook."


def test_deleting_the_task_removes_its_submissions(client, session_factory, world):
    task = create(client, world).json()
    hand_in_voice(client, world, task)
    assert client.delete(f"/teacher/assignments/{task['id']}", headers=world["th"]).status_code == 204
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(ManualSubmission)) == 0
