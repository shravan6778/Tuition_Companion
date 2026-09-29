import json

import pytest
from pydantic import ValidationError

from app.llm.fake_provider import FakeLLMProvider
from app.models import ChapterConcepts, Role
from app.teacher import concepts, processing
from tests.test_chapters import PDF, PDF_2, make_subject, upload
from tests.test_library import add_user

GOOD = json.dumps({"concepts": [{"name": "Force", "summary": "A push or pull on an object.", "prerequisites": []}]})


def c(name, prereqs=()):
    return {"name": name, "summary": "Some summary text.", "prerequisites": list(prereqs)}


def test_graph_validation_rules():
    with pytest.raises(ValidationError, match="unknown prerequisite"):
        concepts.ConceptGraph(concepts=[c("Alpha", ["Beta"])])
    with pytest.raises(ValidationError, match="unique"):
        concepts.ConceptGraph(concepts=[c("Alpha"), c("alpha")])
    with pytest.raises(ValidationError, match="itself"):
        concepts.ConceptGraph(concepts=[c("Alpha", ["Alpha"])])
    with pytest.raises(ValidationError, match="cycle"):
        concepts.ConceptGraph(concepts=[c("Alpha", ["Beta"]), c("Beta", ["Alpha"])])
    assert concepts.ConceptGraph(concepts=[c("Alpha"), c("Beta", ["Alpha"])])

class Scripted:
    model_name = "scripted"

    def __init__(self, replies):
        self.replies, self.prompts = list(replies), []

    def complete_json(self, system, user):
        self.prompts.append(user)
        return self.replies.pop(0)


def test_retry_with_correction_then_success():
    p = Scripted(["not json at all", GOOD])
    graph, _, _ = concepts.extract_concepts(p, "x" * 300, 1000)
    assert len(p.prompts) == 2
    assert "valid JSON only" in p.prompts[1]
    assert graph["concepts"][0]["name"] == "Force"


def test_gives_up_after_two_retries():
    p = Scripted(["bad", "bad", "bad"])
    with pytest.raises(concepts.ConceptExtractionError):
        concepts.extract_concepts(p, "x" * 300, 1000)
    assert len(p.prompts) == 3


def test_upload_stores_concept_graph(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    upload(client, h, sid)
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]["status"] == "ready"
    with session_factory() as db:
        row = db.query(ChapterConcepts).one()
        assert row.graph["concepts"]


def test_concepts_generated_once_per_file_hash(client, session_factory, monkeypatch):
    calls = []

    class Counting(FakeLLMProvider):
        def complete_json(self, system, user):
            calls.append(1)
            return super().complete_json(system, user)

    monkeypatch.setattr(processing, "get_llm_provider", lambda: Counting())
    h = add_user(session_factory, Role.teacher)
    a, b = make_subject(client, h, "Maths"), make_subject(client, h, "Physics")
    upload(client, h, a)
    upload(client, h, b)  # identical bytes
    assert len(calls) == 1


def test_llm_failure_marks_failed_then_retry_succeeds(client, session_factory, monkeypatch):
    real = processing.get_llm_provider

    class Boom:
        model_name = "boom"

        def complete_json(self, system, user):
            raise RuntimeError("llm down")

    monkeypatch.setattr(processing, "get_llm_provider", lambda: Boom())
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    cid = upload(client, h, sid).json()["id"]
    chapter = client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]
    assert chapter["status"] == "failed" and chapter["error_message"]

    monkeypatch.setattr(processing, "get_llm_provider", real)
    assert client.post(f"/teacher/subjects/{sid}/chapters/{cid}/retry", headers=h).status_code == 202
    assert client.get(f"/teacher/subjects/{sid}/chapters", headers=h).json()[0]["status"] == "ready"


def test_deleting_last_chapter_clears_concepts(client, session_factory):
    h = add_user(session_factory, Role.teacher)
    sid = make_subject(client, h)
    cid = upload(client, h, sid).json()["id"]
    client.delete(f"/teacher/subjects/{sid}/chapters/{cid}", headers=h)
    with session_factory() as db:
        assert db.query(ChapterConcepts).count() == 0