"""Phase 3 step 5: mark complete -> comprehension check (scripted model; a real one is judged with `try_check`)."""
import json
import re
import uuid

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models import AssignmentCheck, CheckQuestion, Concept, MasteryEvent, Page, Role
from tests.test_book_access import make_user
from tests.test_phase3_step2 import assign, world  # noqa: F401  (world is a fixture)


class CheckLLM:
    """Writes a valid question about whatever CONCEPT it is asked for. `fail_for` concept names get garbage / errors."""
    model_name = "scripted"

    def __init__(self, bad=(), error=False, garbage_first=0):
        self.bad, self.error, self.garbage_first = set(bad), error, garbage_first
        self.prompts = []

    def complete_json(self, system, user):
        self.prompts.append(user)
        if self.error:
            raise RuntimeError("model down")
        name = re.search(r"^CONCEPT: (.+)$", user, flags=re.M).group(1)
        if name in self.bad or self.garbage_first > 0:
            self.garbage_first = max(0, self.garbage_first - 1)
            return "not json"
        n = len(self.prompts)
        return json.dumps({"question": f"Which statement about {name} is right (variant {n})?",
                           "options": [f"{name}: the true statement {n}", f"{name}: a false statement A{n}", f"{name}: a false statement B{n}", f"{name}: a false statement C{n}"],
                           "correct_index": 0, "explanation": f"EXPLAIN-{name}-{n}"})


@pytest.fixture()
def llm(monkeypatch):
    model = CheckLLM()
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: model)
    return model


def complete(client, w, a, headers=None):
    return client.post(f"/student/assignments/{a['id']}/complete", headers=headers or w["sh"])


def keys(session_factory, check_id):
    with session_factory() as db:
        return {str(q.id): q.correct_index for q in db.scalars(select(CheckQuestion).where(CheckQuestion.check_id == uuid.UUID(check_id)))}


def answers(check, key, right=True):
    return {"answers": [{"question_id": q["id"], "chosen_index": key[q["id"]] if right else (key[q["id"]] + 1) % 4} for q in check["questions"]]}


# ---- opening the check ---------------------------------------------------------------------------------

def test_marking_complete_opens_a_check_with_one_question_per_concept_and_no_key(client, session_factory, world, llm):
    a = assign(client, world)  # chapter level: Cell, Tissue
    res = complete(client, world, a)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "open" and body["assignment_title"] == "Cells" and body["can_submit"] is True
    assert [q["concept_name"] for q in body["questions"]] == ["Cell", "Tissue"] and all(q["status"] == "ready" and len(q["options"]) == 4 for q in body["questions"])
    for q in body["questions"]:  # nothing that reveals the answer, before submission
        assert q["correct_index"] is None and q["explanation"] is None and q["correct"] is None and q["chosen_index"] is None
    assert "EXPLAIN-" not in res.text
    assert "EXPLAIN-" not in client.get(f"/student/checks/{body['id']}", headers=world["sh"]).text  # resuming leaks nothing either
    assert "EXPLAIN-" not in client.get("/student/checks", headers=world["sh"]).text


def test_the_page_a_question_is_written_from_is_its_concepts_own_page(client, world, llm):
    complete(client, world, assign(client, world))
    cell_prompt = next(p for p in llm.prompts if "CONCEPT: Cell\n" in p)
    assert "The cell is the basic structural unit" in cell_prompt and "A tissue is a group" not in cell_prompt


def test_one_concept_still_gets_the_floor_of_two_questions_about_different_aspects(client, world, llm):
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Tissue"]])
    body = complete(client, world, a).json()
    assert len(body["questions"]) == settings.check_min_questions == 2
    assert "QUESTIONS ALREADY ASKED" in llm.prompts[1] and "variant 1" in llm.prompts[1]  # the second asks about another aspect


def test_a_big_assignment_is_capped_and_the_concepts_the_student_asked_about_come_first(client, session_factory, world, llm):
    with session_factory() as db:
        page = db.scalars(select(Page).where(Page.content_text.like("Force is a push%"))).first()
        for i in range(25):
            db.add(Concept(page_id=page.id, name=f"Extra {i}", description="an extra idea", position=10 + i))
        db.commit()
        extra = [str(c.id) for c in db.scalars(select(Concept).where(Concept.name.like("Extra %")).order_by(Concept.position))]
        db.add(MasteryEvent(student_id=world["student"].id, concept_id=uuid.UUID(extra[2]), concept_name="Extra 2", kind="doubt"))
        db.commit()
    a = assign(client, world, level="concept", chapter=None, concept_ids=extra)
    body = complete(client, world, a).json()
    names = [q["concept_name"] for q in body["questions"]]
    assert len(names) == settings.check_max_questions == 10 and "Extra 2" in names  # the doubted concept made the cut (an even spread alone would skip it)


def test_marking_complete_again_resumes_the_same_check_without_new_model_calls(client, world, llm):
    a = assign(client, world)
    first = complete(client, world, a).json()
    calls = len(llm.prompts)
    again = complete(client, world, a).json()
    assert again["id"] == first["id"] and len(llm.prompts) == calls


# ---- a question the model cannot write -------------------------------------------------------------------

def test_an_invalid_reply_is_corrected_twice_then_the_question_is_failed_not_blank(client, session_factory, world, monkeypatch):
    model = CheckLLM(garbage_first=2)  # two bad replies, then fine: still ready
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: model)
    body = complete(client, world, assign(client, world)).json()
    assert all(q["status"] == "ready" for q in body["questions"]) and len(model.prompts) == 4  # 3 tries for the first, 1 for the second
    bad = CheckLLM(bad={"Tissue"})
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: bad)
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Tissue"], world["concepts"]["Cell"], world["concepts"]["Force"]])
    body = complete(client, world, a).json()
    failed = next(q for q in body["questions"] if q["concept_name"] == "Tissue")
    assert failed["status"] == "failed" and failed["question"] is None and failed["options"] is None and "couldn't" in failed["message"]
    assert len([p for p in bad.prompts if "CONCEPT: Tissue\n" in p]) == 3  # the first try and two corrections


def test_a_check_with_a_failed_question_can_be_submitted_when_the_floor_is_still_met_and_the_failed_one_is_not_graded(client, session_factory, world, monkeypatch):
    bad = CheckLLM(bad={"Tissue"})
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: bad)
    a = assign(client, world, level="concept", chapter=None, concept_ids=[world["concepts"]["Tissue"], world["concepts"]["Cell"], world["concepts"]["Force"]])
    check = complete(client, world, a).json()
    assert check["can_submit"] is True
    ready = [q for q in check["questions"] if q["status"] == "ready"]
    key = keys(session_factory, check["id"])
    done = client.post(f"/student/checks/{check['id']}/submit", json=answers({"questions": ready}, key), headers=world["sh"]).json()
    assert done["score"] == 1.0 and [q["status"] for q in done["questions"]].count("failed") == 1


def test_too_few_questions_cannot_be_submitted_and_marking_complete_again_retries_the_failed_ones(client, session_factory, world, monkeypatch):
    bad = CheckLLM(bad={"Tissue"})
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: bad)
    check = complete(client, world, assign(client, world)).json()  # Cell ok, Tissue failed: 1 < floor 2
    assert check["can_submit"] is False
    refused = client.post(f"/student/checks/{check['id']}/submit", json={"answers": []}, headers=world["sh"])
    assert refused.status_code == 409
    good = CheckLLM()
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: good)
    a = client.get("/student/assignments", headers=world["sh"]).json()[0]
    retried = complete(client, world, a).json()
    assert retried["id"] == check["id"] and retried["can_submit"] is True and all(q["status"] == "ready" for q in retried["questions"])
    assert len(good.prompts) == 1  # only the failed question was written again


def test_a_model_that_is_down_gives_failed_questions_not_a_500(client, world, monkeypatch):
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: CheckLLM(error=True))
    res = complete(client, world, assign(client, world))
    assert res.status_code == 200 and {q["status"] for q in res.json()["questions"]} == {"failed"} and res.json()["can_submit"] is False


def test_a_model_that_cannot_start_reads_the_same_way(client, world, monkeypatch):
    def boom():
        raise RuntimeError("not configured")
    monkeypatch.setattr("app.assessment.service.get_llm_provider", boom)
    assert complete(client, world, assign(client, world)).json()["can_submit"] is False


# ---- grading ----------------------------------------------------------------------------------------------

def test_submitting_grades_in_code_and_only_then_reveals_the_key_and_explanations(client, session_factory, world, llm):
    check = complete(client, world, assign(client, world)).json()
    key = keys(session_factory, check["id"])
    done = client.post(f"/student/checks/{check['id']}/submit", json=answers(check, key), headers=world["sh"]).json()
    assert done["status"] == "submitted" and done["score"] == 1.0 and done["can_submit"] is False
    assert all(q["correct"] is True and q["correct_index"] == key[q["id"]] and q["explanation"].startswith("EXPLAIN-") for q in done["questions"])
    assert client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()["score"] == 1.0  # still readable afterwards
    with session_factory() as db:
        row = db.get(AssignmentCheck, uuid.UUID(check["id"]))
        assert row.score == 1.0 and row.submitted_at is not None


def test_wrong_and_missing_answers_are_simply_wrong(client, session_factory, world, llm):
    check = complete(client, world, assign(client, world)).json()
    key = keys(session_factory, check["id"])
    one_right_one_missing = {"answers": [{"question_id": check["questions"][0]["id"], "chosen_index": key[check["questions"][0]["id"]]}]}
    done = client.post(f"/student/checks/{check['id']}/submit", json=one_right_one_missing, headers=world["sh"]).json()
    assert done["score"] == 0.5 and [q["correct"] for q in done["questions"]] == [True, False] and done["questions"][1]["chosen_index"] is None


def test_all_wrong_scores_zero(client, session_factory, world, llm):
    check = complete(client, world, assign(client, world)).json()
    done = client.post(f"/student/checks/{check['id']}/submit", json=answers(check, keys(session_factory, check["id"]), right=False), headers=world["sh"]).json()
    assert done["score"] == 0.0 and all(q["correct"] is False for q in done["questions"])


def test_a_check_is_submitted_once_and_answers_must_belong_to_it(client, session_factory, world, llm):
    check = complete(client, world, assign(client, world)).json()
    key = keys(session_factory, check["id"])
    assert client.post(f"/student/checks/{check['id']}/submit", json={"answers": [{"question_id": str(uuid.uuid4()), "chosen_index": 0}]}, headers=world["sh"]).status_code == 422
    assert client.post(f"/student/checks/{check['id']}/submit", json={"answers": [{"question_id": check["questions"][0]["id"], "chosen_index": 7}]}, headers=world["sh"]).status_code == 422
    body = answers(check, key)
    assert client.post(f"/student/checks/{check['id']}/submit", json=body, headers=world["sh"]).status_code == 200
    assert client.post(f"/student/checks/{check['id']}/submit", json=answers(check, key, right=False), headers=world["sh"]).status_code == 409
    assert client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()["score"] == 1.0  # the first grading stands


def test_after_a_submitted_check_marking_complete_again_opens_a_new_one(client, session_factory, world, llm):
    a = assign(client, world)
    first = complete(client, world, a).json()
    client.post(f"/student/checks/{first['id']}/submit", json=answers(first, keys(session_factory, first["id"])), headers=world["sh"])
    second = complete(client, world, a).json()
    assert second["id"] != first["id"] and second["status"] == "open"
    assert len(client.get("/student/checks", headers=world["sh"]).json()) == 2


# ---- who may do what -----------------------------------------------------------------------------------------

def test_someone_elses_assignment_or_check_is_404_and_costs_no_model_call(client, session_factory, world, llm):
    a = assign(client, world)
    _, other = make_user(session_factory, Role.student, "studentb")
    assert complete(client, world, a, headers=other).status_code == 404
    assert complete(client, world, {"id": str(uuid.uuid4())}).status_code == 404
    assert llm.prompts == []
    mine = complete(client, world, a).json()
    assert client.get(f"/student/checks/{mine['id']}", headers=other).status_code == 404
    assert client.post(f"/student/checks/{mine['id']}/submit", json={"answers": []}, headers=other).status_code == 404
    assert client.get("/student/checks", headers=other).json() == []


def test_a_teacher_cannot_use_the_student_check_routes(client, world, llm):
    a = assign(client, world)
    assert complete(client, world, a, headers=world["th"]).status_code in (401, 403)


def test_the_check_limit_is_per_student_and_checked_after_the_404(client, session_factory, world, llm, monkeypatch):
    monkeypatch.setattr(settings, "rate_checks_per_hour", 2)
    a = assign(client, world)
    assert [complete(client, world, a).status_code for _ in range(3)] == [200, 200, 429]


def test_deleting_the_assignment_keeps_the_students_check_record(client, session_factory, world, llm):
    a = assign(client, world)
    check = complete(client, world, a).json()
    assert client.delete(f"/teacher/assignments/{a['id']}", headers=world["th"]).status_code == 204
    kept = client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()
    assert kept["assignment_id"] is None and kept["assignment_title"] == "Cells" and len(kept["questions"]) == 2


def test_try_check_prints_the_plan_the_questions_and_the_grading_without_writing(client, session_factory, world, llm):
    from app.db import try_check
    with session_factory() as db:
        before = db.scalars(select(AssignmentCheck)).all()
        lines = try_check.run(db, llm, uuid.UUID(world["ids"]["ch1"]))
        assert db.scalars(select(AssignmentCheck)).all() == before == []
    text = "\n".join(lines)
    assert "2 concepts -> 2 questions" in text and "KEY (hidden" in text and "all right -> 2/2, all wrong -> 0/2" in text and "2/2 valid questions" in text
