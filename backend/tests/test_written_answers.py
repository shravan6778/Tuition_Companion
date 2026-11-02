"""Written and spoken answers: rubric grading, long answers, voice rules, the speech seam (fake providers), the teacher's override."""
import io
import json
import struct
import wave

import pytest
from sqlalchemy import select

from app.assessment import answers as answer_rules, llm_grader, mastery, rubric, subject_policy
from app.assessment.checks import plan_formats
from app.assessment.quiz_agent import PlannedQuizItem, apply_long_share
from app.core.config import settings
from app.models import (Assignment, AssignmentCheck, CheckQuestion, MasteryEvent, QuizQuestion, QuizResponse)
from app.llm.fake_provider import FakeLLMProvider
from tests.test_phase3_step2 import assign, world  # noqa: F401  (world is a fixture)
from tests.test_phase4_step2 import _request_and_approve_room, _seed_world

POINTS = [{"point": "Cells are the basic unit of life", "marks": 2}, {"point": "Tissues are groups of similar cells", "marks": 1},
          {"point": "Organs are made of tissues", "marks": 1}]


class Scripted:
    model_name = "scripted"

    def __init__(self, *replies):
        self.replies, self.prompts = list(replies), []

    def complete_json(self, system, user):
        self.prompts.append((system, user))
        return self.replies.pop(0)


# ---- rubric and grader ----------------------------------------------------------------------------------------------

def test_the_score_comes_from_the_marks_of_the_hit_points_not_from_the_model():
    assert rubric.score_from_hits(POINTS, [0]) == 0.5 and rubric.score_from_hits(POINTS, [0, 1, 2]) == 1.0 and rubric.score_from_hits(POINTS, []) == 0.0
    assert rubric.clean_indexes([2, 2, 9, -1, True, "1"], 3) == [2]  # junk is dropped
    llm = Scripted(json.dumps({"points_hit": [0, 1], "points_missed": [2], "feedback": "Good, but organs are missing.", "score": 1.0}))
    g = llm_grader.grade_written_answer(llm, "Q?", POINTS, "cells are the unit of life, tissues are groups", "Cells")
    assert g.score == 0.75 and g.points_hit == [0, 1] and g.points_missed == [2] and g.marks_awarded == 3 and g.marks_available == 4 and not g.correct


def test_the_grader_is_told_the_answer_may_be_english_hindi_telugu_or_mixed_and_to_grade_meaning():
    llm = Scripted(json.dumps({"points_hit": [0], "points_missed": [1, 2], "feedback": "Only the first idea is there."}))
    llm_grader.grade_written_answer(llm, "Q?", POINTS, "కణం జీవానికి ప్రాథమిక యూనిట్", "Cells", input_method="voice")
    system, user = llm.prompts[0]
    assert "English, Hindi, Telugu" in system and "MEANING" in system and "(key points, in English)" in user
    assert "INPUT: voice" in user and "కణం" in user


def test_blank_answers_score_zero_without_a_model_call_and_inconsistent_replies_are_retried_then_fail():
    llm = Scripted()
    g = llm_grader.grade_written_answer(llm, "Q?", POINTS, "   ", "Cells")
    assert g.score == 0.0 and g.points_missed == [0, 1, 2] and llm.prompts == []
    bad = json.dumps({"points_hit": [0], "points_missed": [0, 1], "feedback": "points overlap here"})  # 0 listed twice, 2 never
    llm = Scripted(bad, bad, bad)
    with pytest.raises(llm_grader.WrittenGradeError):
        llm_grader.grade_written_answer(llm, "Q?", POINTS, "something", "Cells")
    assert len(llm.prompts) == 3


def test_older_short_answers_without_key_points_still_grade_as_one_score():
    out = answer_rules.grade(FakeLLMProvider(), question="Q", key_points=None, expected_answer="Cells are the basic unit of life",
                             text="cells are the basic unit", concept_name="Cell", input_method="typed", fmt="short_answer")
    assert out.points_hit is None and out.score_source == "ai" and out.score is not None


# ---- subjects, shares ------------------------------------------------------------------------------------------------

def test_maths_type_subjects_get_no_long_and_no_spoken_answers():
    for s in ("Mathematics", "Maths (Class 9)", "applied mathematics", "గణితం", "गणित"):
        assert subject_policy.policy_for(s) == subject_policy.AnswerPolicy(False, False), s
    for s in ("Science", "Social Studies", "Mathematical Reasoning", None):
        assert subject_policy.policy_for(s) == subject_policy.AnswerPolicy(True, True), s


def test_check_formats_follow_the_configurable_shares(monkeypatch):
    monkeypatch.setattr(settings, "check_short_share", 0.2)
    monkeypatch.setattr(settings, "check_long_share", 0.1)
    f = plan_formats(10)
    assert f.count("short_answer") == 2 and f.count("long_answer") == 1 and f.count("mcq") == 7
    assert plan_formats(2) == ["mcq", "mcq"]  # a tiny check rounds to no written question
    m = plan_formats(10, allow_long=False)
    assert "long_answer" not in m and m.count("short_answer") == 3  # a maths-type subject: the long one becomes short
    monkeypatch.setattr(settings, "check_short_share", 1.0)
    monkeypatch.setattr(settings, "check_long_share", 0.0)
    assert plan_formats(4).count("mcq") >= 1  # always some part marked in code


def test_the_quiz_long_share_upgrades_non_recall_slots_keeps_a_short_one_and_skips_recall_and_maths(monkeypatch):
    monkeypatch.setattr(settings, "quiz_long_share", 0.3)
    import uuid
    ids = [uuid.uuid4() for _ in range(4)]
    plan = [PlannedQuizItem(0, ids[0], None, "recall", "mcq"), PlannedQuizItem(1, ids[1], None, "application", "short_answer"),
            PlannedQuizItem(2, ids[2], None, "cross_concept", "short_answer"), PlannedQuizItem(3, ids[3], None, "application", "mcq")]
    apply_long_share(plan, 10, no_long=[ids[1]])  # 3 long wanted: only the application mcq is free, and one short is always kept
    assert [p.answer_format for p in plan] == ["mcq", "short_answer", "long_answer", "long_answer"]


# ---- assignment checks -----------------------------------------------------------------------------------------------

@pytest.fixture()
def written(monkeypatch):
    """Every check gets one long answer (a 2-concept check: the other stays multiple choice)."""
    monkeypatch.setattr(settings, "check_short_share", 0.0)
    monkeypatch.setattr(settings, "check_long_share", 1.0)


def open_check(client, w):
    a = assign(client, w)
    res = client.post(f"/student/assignments/{a['id']}/complete", headers=w["sh"])
    assert res.status_code == 200, res.text
    return a, res.json()


def written_q(check):
    return next(q for q in check["questions"] if q["answer_format"] == "long_answer")


def submit(client, w, check, text=None, **extra):
    answers = []
    for q in check["questions"]:
        if q["answer_format"] == "mcq":
            answers.append({"question_id": q["id"], "chosen_index": 0})
        else:
            body = text or f"{q['concept_name']} is described in the text and has an effect the text explains with an example"
            answers.append({"question_id": q["id"], "answer_text": body, **extra})
    return client.post(f"/student/checks/{check['id']}/submit", json={"answers": answers}, headers=w["sh"])


def test_a_long_question_hides_its_rubric_until_submitted_then_shows_hits_misses_and_an_ai_suggestion(client, world, written):
    _, check = open_check(client, world)
    q = written_q(check)
    assert q["options"] is None and q["voice_allowed"] is True and q["rubric"] is None and q["expected_answer"] is None
    assert "key_points" not in json.dumps(check) and "explanation" in q and q["explanation"] is None
    res = submit(client, world, check)
    assert res.status_code == 200, res.text
    out = written_q(res.json())
    assert out["input_method"] == "typed" and out["transcript_language"] is None and out["score_source"] == "ai"
    assert "suggestion" in out["score_label"].lower() and "is described in the text" in out["answer_text"]
    hits = [p["hit"] for p in out["rubric"]]
    assert True in hits and False in hits and out["marks_awarded"] < out["marks_available"] and out["expected_answer"]
    assert res.json()["score"] is not None


def test_a_spoken_answer_needs_the_students_confirmation_a_language_and_is_stored_as_text_only(client, world, written, session_factory, monkeypatch):
    _, check = open_check(client, world)
    seen = []
    monkeypatch.setattr("app.assessment.service.get_llm_provider", lambda: (seen.append(1), FakeLLMProvider())[1])
    res = submit(client, world, check, input_method="voice", language="te-IN")  # no confirmation: never graded straight from speech
    assert res.status_code == 422 and "tick" in res.json()["detail"] and seen == []
    assert submit(client, world, check, input_method="voice", language="fr-FR", transcript_confirmed=True).status_code == 422
    res = submit(client, world, check, input_method="voice", language="te-IN", transcript_confirmed=True)
    assert res.status_code == 200, res.text
    out = written_q(res.json())
    assert out["input_method"] == "voice" and out["transcript_language"] == "te-IN" and out["score_source"] == "ai" and not out["needs_confirm"]
    with session_factory() as db:
        row = db.scalars(select(CheckQuestion).where(CheckQuestion.answer_format == "long_answer")).one()
        assert row.input_method == "voice" and row.transcript_language == "te-IN" and "is described in the text" in row.answer_text


def test_multiple_choice_cannot_be_spoken(client, world, written):
    _, check = open_check(client, world)
    mcq = next(q for q in check["questions"] if q["answer_format"] == "mcq")
    res = client.post(f"/student/checks/{check['id']}/submit", headers=world["sh"],
                      json={"answers": [{"question_id": mcq["id"], "chosen_index": 1, "input_method": "voice", "language": "en-IN", "transcript_confirmed": True}]})
    assert res.status_code == 422


def test_a_maths_subject_gets_short_not_long_answers_and_refuses_voice(client, world, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "check_short_share", 0.0)
    monkeypatch.setattr(settings, "check_long_share", 1.0)
    a = assign(client, world)
    with session_factory() as db:
        from app.models import Book
        for book in db.scalars(select(Book)):
            book.subject = "Mathematics"  # tasks resolve to a book by subject, so the books are maths too
        db.get(Assignment, __import__("uuid").UUID(a["id"])).subject = "Mathematics"
        db.commit()
    res = client.post(f"/student/assignments/{a['id']}/complete", headers=world["sh"])
    assert res.status_code == 200, res.text
    check = res.json()
    formats = [q["answer_format"] for q in check["questions"]]
    assert "long_answer" not in formats and "short_answer" in formats
    q = next(q for q in check["questions"] if q["answer_format"] == "short_answer")
    assert q["voice_allowed"] is False
    res = submit(client, world, {**check, "questions": check["questions"]}, input_method="voice", language="en-IN", transcript_confirmed=True)
    assert res.status_code == 422 and "turned off" in res.json()["detail"]
    assert submit(client, world, check).status_code == 200  # typing still works


def held_world(monkeypatch):
    monkeypatch.setattr(settings, "speech_hold_languages", "te-IN")


def test_confirm_before_grading_holds_a_spoken_answer_until_the_teacher_confirms_the_transcript(client, world, written, session_factory, monkeypatch):
    held_world(monkeypatch)
    a, check = open_check(client, world)
    res = submit(client, world, check, input_method="voice", language="te-IN", transcript_confirmed=True)
    out = written_q(res.json())
    assert out["needs_confirm"] is True and out["score"] is None and out["score_source"] is None and "teacher" in out["score_label"].lower()
    with session_factory() as db:  # the held answer is not in the mastery log yet: only the multiple-choice question counted
        events = db.scalars(select(MasteryEvent).where(MasteryEvent.kind == "check")).all()
        assert len(events) == 1
    work = client.get(f"/teacher/assignments/{a['id']}/checks", headers=world["th"]).json()
    assert work[0]["waiting_for_you"] == 1
    held = next(x for x in work[0]["answers"] if x["needs_confirm"])
    assert held["input_method"] == "voice" and held["transcript_language"] == "te-IN" and held["answer_text"]
    done = client.post(f"/teacher/check-questions/{held['id']}/confirm", json={"transcript": "The cell is the basic unit of life and tissues are groups of cells"}, headers=world["th"])
    assert done.status_code == 200, done.text
    assert done.json()["needs_confirm"] is False and done.json()["score_source"] == "ai" and "tissues" in done.json()["answer_text"]
    with session_factory() as db:
        assert len(db.scalars(select(MasteryEvent).where(MasteryEvent.kind == "check", MasteryEvent.corrects_event_id.is_not(None))).all()) == 1


def test_teacher_override_marks_the_answer_as_theirs_keeps_the_ai_number_and_re_measures_mastery(client, world, written, session_factory):
    a, check = open_check(client, world)
    submit(client, world, check, text="I do not know idk")
    sid = world["student"].id
    with session_factory() as db:
        before = {s.name: s.score for s in mastery.current_state(db, sid).values()}
    work = client.get(f"/teacher/assignments/{a['id']}/checks", headers=world["th"]).json()[0]
    item = next(x for x in work["answers"] if x["answer_format"] == "long_answer")
    assert item["score_source"] == "ai" and item["score"] == 0.0 and item["can_override"] is True
    n = len(item["rubric"]) if item["rubric"] else 4
    res = client.post(f"/teacher/check-questions/{item['id']}/override", json={"points_hit": list(range(n)), "feedback": "I heard this in class."}, headers=world["th"])
    assert res.status_code == 200, res.text
    new = res.json()
    assert new["score_source"] == "teacher" and new["ai_score"] == 0.0 and new["score"] == 1.0 and new["marks_awarded"] == new["marks_available"]
    assert new["teacher_feedback"] == "I heard this in class." and "teacher" in new["score_label"].lower()
    after_work = client.get(f"/teacher/assignments/{a['id']}/checks", headers=world["th"]).json()[0]
    assert after_work["score"] > work["score"]
    mine = client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json()
    assert written_q(mine)["score_source"] == "teacher"
    with session_factory() as db:
        after = {s.name: s.score for s in mastery.current_state(db, sid).values()}
        assert any(after[n] > before[n] for n in before)  # the concept that was re-marked moved
        assert len(db.scalars(select(MasteryEvent).where(MasteryEvent.kind == "check", MasteryEvent.student_id == sid)).all()) >= 3  # the log kept the old row
    assert client.post(f"/teacher/check-questions/{item['id']}/override", json={}, headers=world["th"]).status_code == 422
    assert client.post(f"/teacher/check-questions/{item['id']}/override", json={"points_hit": [9]}, headers=world["th"]).status_code == 422
    mcq = next(x for x in work["answers"] if x["answer_format"] == "mcq")
    assert client.post(f"/teacher/check-questions/{mcq['id']}/override", json={"score": 1}, headers=world["th"]).status_code == 409


def test_only_the_teacher_who_set_the_assignment_can_see_or_change_written_answers(client, world, written, make_user, as_user):
    from app.models import Role
    a, check = open_check(client, world)
    submit(client, world, check)
    q = written_q(client.get(f"/student/checks/{check['id']}", headers=world["sh"]).json())
    other = make_user(Role.teacher)
    oh = {"Authorization": f"Bearer {other.supertokens_user_id}"}
    assert client.get(f"/teacher/assignments/{a['id']}/checks", headers=oh).status_code == 404
    assert client.post(f"/teacher/check-questions/{q['id']}/override", json={"score": 1}, headers=oh).status_code == 404
    assert client.post(f"/teacher/check-questions/{q['id']}/override", json={"score": 1}, headers=world["sh"]).status_code == 403


# ---- tests (quizzes) -------------------------------------------------------------------------------------------------

def quiz_world(client, session_factory, monkeypatch, subject=None):
    monkeypatch.setattr(settings, "quiz_long_share", 0.3)
    with session_factory() as db:
        w = _seed_world(db)
    room = client.post("/teacher/rooms", headers=w["t1"], json={"name": "9A", "room_type": "single_class"}).json()
    _request_and_approve_room(client, room, w["s1"], w["t1"])
    quiz = client.post("/teacher/quizzes/generate", headers=w["t1"], json={"book_id": w["book_id"], "chapter_id": w["ch_id"], "length": "short", "room_id": room["id"]}).json()
    return w, quiz


def test_quizzes_can_contain_long_answers_with_rubrics_the_student_never_sees_early(client, session_factory, monkeypatch):
    w, quiz = quiz_world(client, session_factory, monkeypatch)
    formats = [q["answer_format"] for q in quiz["questions"]]
    assert formats.count("long_answer") == 3
    longq = next(q for q in quiz["questions"] if q["answer_format"] == "long_answer")
    assert 3 <= len(longq["rubric"]) and longq["expected_answer"]  # the teacher sees the rubric
    shortq = next(q for q in quiz["questions"] if q["answer_format"] == "short_answer")
    assert len(shortq["rubric"]) >= 1  # short answers have key points too
    mine = client.get(f"/student/quizzes/{quiz['id']}", headers=w["s1"])
    assert "key_points" not in mine.text and all(q["rubric"] is None and q["expected_answer"] is None for q in mine.json()["questions"])


def answer_quiz(client, w, quiz, **extra):
    payload = []
    for q in quiz["questions"]:
        if q["answer_format"] == "mcq":
            payload.append({"question_id": q["id"], "chosen_index": 0})
        else:
            payload.append({"question_id": q["id"], "answer_text": "It is described in the text and has an effect the text explains with an example", **extra})
    return client.post(f"/student/quizzes/{quiz['id']}/submit", headers=w["s1"], json={"answers": payload})


def test_quiz_voice_rules_and_the_teacher_view_of_transcripts(client, session_factory, monkeypatch):
    w, quiz = quiz_world(client, session_factory, monkeypatch)
    assert answer_quiz(client, w, quiz, input_method="voice", language="hi-IN").status_code == 422  # not confirmed
    res = answer_quiz(client, w, quiz, input_method="voice", language="hi-IN", transcript_confirmed=True)
    assert res.status_code == 200, res.text
    graded = [q for q in res.json()["questions"] if q["answer_format"] != "mcq"]
    assert all(q["input_method"] == "voice" and q["transcript_language"] == "hi-IN" and q["score_source"] == "ai" and q["rubric"] for q in graded)
    work = client.get(f"/teacher/quizzes/{quiz['id']}/responses", headers=w["t1"]).json()
    assert work[0]["student_name"] == "Student 1"
    spoken = [a for a in work[0]["answers"] if a["input_method"] == "voice"]
    assert len(spoken) == len(graded) and all(a["answer_text"] and a["can_override"] for a in spoken)
    assert client.get(f"/teacher/quizzes/{quiz['id']}/responses", headers=w["t2"]).status_code == 404
    first = spoken[0]
    o = client.post(f"/teacher/quiz-responses/{first['id']}/override", headers=w["t1"], json={"score": 0.25})
    assert o.status_code == 200 and o.json()["score"] == 0.25 and o.json()["score_source"] == "teacher" and o.json()["ai_score"] == first["score"]
    assert client.post(f"/teacher/quiz-responses/{first['id']}/override", headers=w["t2"], json={"score": 1}).status_code == 404
    with session_factory() as db:
        row = db.get(QuizResponse, __import__("uuid").UUID(first["id"]))
        assert row.correct is False and row.reviewed_at is not None


def test_a_maths_book_gets_no_long_answers_in_a_quiz_and_no_voice(client, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "quiz_long_share", 0.5)
    with session_factory() as db:
        w = _seed_world(db)
        from app.models import Book
        for book in db.scalars(select(Book)):
            book.subject = "Mathematics"  # the teacher's book and the student's own copy
        db.commit()
    room = client.post("/teacher/rooms", headers=w["t1"], json={"name": "9A", "room_type": "single_class"}).json()
    _request_and_approve_room(client, room, w["s1"], w["t1"])
    quiz = client.post("/teacher/quizzes/generate", headers=w["t1"], json={"book_id": w["book_id"], "chapter_id": w["ch_id"], "length": "short", "room_id": room["id"]}).json()
    assert "long_answer" not in [q["answer_format"] for q in quiz["questions"]]
    assert all(q["voice_allowed"] is False for q in quiz["questions"])
    res = answer_quiz(client, w, quiz, input_method="voice", language="en-IN", transcript_confirmed=True)
    assert res.status_code == 422 and answer_quiz(client, w, quiz).status_code == 200


# ---- the speech seam -------------------------------------------------------------------------------------------------

def wav_bytes(seconds=1.0, rate=16000, channels=1):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes(struct.pack("<h", 100) * int(rate * seconds) * channels)
    return buf.getvalue()


def test_config_says_where_each_language_is_recognised_and_which_are_held(client, world, monkeypatch):
    cfg = client.get("/student/speech/config", headers=world["sh"]).json()
    assert [l["code"] for l in cfg["languages"]] == ["en-IN", "hi-IN", "te-IN"] and {l["source"] for l in cfg["languages"]} == {"browser"}
    assert cfg["server_available"] is False and not any(l["hold"] for l in cfg["languages"])
    monkeypatch.setattr(settings, "speech_provider", "fake")
    monkeypatch.setattr(settings, "speech_server_languages", "te-IN")
    monkeypatch.setattr(settings, "speech_hold_languages", "hi-IN")
    cfg = client.get("/student/speech/config", headers=world["sh"]).json()
    by = {l["code"]: l for l in cfg["languages"]}
    assert by["te-IN"]["source"] == "server" and by["en-IN"]["source"] == "browser" and by["hi-IN"]["hold"] is True and cfg["server_available"] is True


def test_in_browser_mode_the_server_has_no_speech_endpoint_to_receive_audio(client, world):
    res = client.post("/student/speech/transcribe?language=te-IN", content=wav_bytes(), headers={**world["sh"], "content-type": "audio/wav"})
    assert res.status_code == 404


def test_server_mode_transcribes_with_a_fake_provider_and_keeps_no_audio(client, world, session_factory, tmp_path, monkeypatch):
    from app.speech import FakeSpeechToText
    fake = FakeSpeechToText({"te-IN": "కణం జీవానికి ప్రాథమిక యూనిట్"})
    monkeypatch.setattr(settings, "speech_provider", "fake")
    monkeypatch.setattr("app.speech.routes.get_speech_provider", lambda: fake)
    res = client.post("/student/speech/transcribe?language=te-IN", content=wav_bytes(), headers={**world["sh"], "content-type": "audio/wav"})
    assert res.status_code == 200, res.text
    assert res.json()["text"] == "కణం జీవానికి ప్రాథమిక యూనిట్" and res.json()["language"] == "te-IN"
    assert fake.calls == [(len(wav_bytes()), "audio/wav", "te-IN")]
    stored = [p for p in (tmp_path / "storage").rglob("*") if p.is_file()] if (tmp_path / "storage").exists() else []
    assert stored == []  # no audio file anywhere under the storage folder
    with session_factory() as db:  # and the transcript itself is not saved by this call: it only fills the answer box
        assert db.scalars(select(QuizResponse)).first() is None and db.scalars(select(CheckQuestion).where(CheckQuestion.answer_text.is_not(None))).first() is None
    assert not any(hasattr(fake, a) and isinstance(getattr(fake, a), (bytes, bytearray)) for a in vars(fake))


def test_server_speech_refuses_bad_input_and_reports_provider_failures_as_try_again(client, world, monkeypatch):
    from app.speech import FakeSpeechToText
    fake = FakeSpeechToText()
    monkeypatch.setattr(settings, "speech_provider", "fake")
    monkeypatch.setattr("app.speech.routes.get_speech_provider", lambda: fake)
    wav = {**world["sh"], "content-type": "audio/wav"}
    post = lambda body, lang="en-IN", h=wav: client.post(f"/student/speech/transcribe?language={lang}", content=body, headers=h)
    assert post(wav_bytes(), "fr-FR").status_code == 422
    assert post(b"not audio").status_code == 415
    assert post(wav_bytes(rate=44100)).status_code == 415
    assert post(wav_bytes(seconds=settings.speech_max_audio_seconds + 1)).status_code == 413
    assert post(wav_bytes(), h={**world["sh"], "content-type": "audio/webm"}).status_code == 415
    assert fake.calls == []
    monkeypatch.setattr("app.speech.routes.get_speech_provider", lambda: FakeSpeechToText(fail=True))
    assert post(wav_bytes()).status_code == 422
    monkeypatch.setattr("app.speech.routes.get_speech_provider", lambda: FakeSpeechToText(silent=True))
    assert post(wav_bytes()).status_code == 422
    th = {"Authorization": "Bearer nobody", "content-type": "audio/wav"}
    assert post(wav_bytes(), h=th).status_code in (401, 403)


def test_the_azure_provider_reads_a_recognition_reply_without_keeping_anything(monkeypatch):
    import httpx
    from app.speech.azure_provider import AzureSpeechToText
    from app.speech.base import SpeechError

    class Resp:
        def __init__(self, code, body): self.status_code, self._b = code, body
        def json(self): return self._b

    sent = {}

    def fake_post(url, params=None, content=None, headers=None, timeout=None):
        sent.update(url=url, params=params, n=len(content), key=headers["Ocp-Apim-Subscription-Key"])
        return Resp(200, {"RecognitionStatus": "Success", "NBest": [{"Display": "కణం", "Confidence": 0.8}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    t = AzureSpeechToText("k", "centralindia").transcribe(b"x" * 10, "audio/wav", "te-IN")
    assert t.text == "కణం" and t.confidence == 0.8 and sent["params"]["language"] == "te-IN" and "centralindia" in sent["url"]
    monkeypatch.setattr(httpx, "post", lambda *a, **k: Resp(200, {"RecognitionStatus": "NoMatch"}))
    with pytest.raises(SpeechError):
        AzureSpeechToText("k", "r").transcribe(b"x", "audio/wav", "te-IN")
    with pytest.raises(RuntimeError):
        AzureSpeechToText("", "")


# ---- the pilot analysis ----------------------------------------------------------------------------------------------

def test_the_pilot_counts_wrong_key_terms_per_language_and_source_and_advises():
    from app.db.stt_pilot import advice, analyse, normalise
    items = {"cell": {"en-IN": {"terms": ["cell", "nucleus"]}, "te-IN": {"terms": ["కణం", "కేంద్రక"]}}}
    rows = [
        {"participant": "a", "language": "en-IN", "item": "cell", "source": "browser", "transcript": "The Cell is the unit and the nucleus controls it."},
        {"participant": "b", "language": "te-IN", "item": "cell", "source": "browser", "transcript": "కణం జీవానికి ప్రమాణం కేంద్రకం నియంత్రిస్తుంది"},  # stem match across the ending
        {"participant": "c", "language": "te-IN", "item": "cell", "source": "browser", "transcript": "కనం జీవానికి ప్రమాణం కేంద్రం నియంత్రిస్తుంది"},  # both terms heard wrong
        {"participant": "c", "language": "te-IN", "item": "cell", "source": "server", "transcript": "కణం కేంద్రకం"},
    ]
    r = analyse(rows, items, 0.15)
    assert r[("en-IN", "browser")]["wrong"] == 0 and r[("en-IN", "browser")]["ok"]
    te = r[("te-IN", "browser")]
    assert (te["terms"], te["wrong"], te["participants"]) == (4, 2, 2) and te["rate"] == 0.5 and not te["ok"]
    assert r[("te-IN", "server")]["ok"] and len(te["misses"]) == 2
    assert "SPEECH_HOLD_LANGUAGES=te-IN" in advice("te-IN", "browser", False, True) and "SPEECH_SERVER_LANGUAGES=te-IN" in advice("te-IN", "browser", False, False)
    assert normalise("Cell,  \u200cNucleus!") == "cell nucleus"


def test_the_shipped_pilot_items_cover_five_answers_in_all_three_languages():
    from app.db.stt_pilot import DEFAULT_ITEMS, load_items
    items = load_items(DEFAULT_ITEMS)
    assert len(items) == 5
    for item in items.values():
        for lang in ("en-IN", "hi-IN", "te-IN"):
            assert item[lang]["text"] and len(item[lang]["terms"]) >= 2
            assert all(t in item[lang]["text"] or t.casefold() in item[lang]["text"].casefold() or any(t in w for w in item[lang]["text"].split()) for t in item[lang]["terms"]), (item["id"], lang)
