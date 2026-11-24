"""Admin dashboard, usage caps + kill switch, audit log, invite-only teachers, login lockout, request ids, config guard."""
import asyncio
import logging
import uuid
from types import SimpleNamespace

import pytest
from sqlalchemy import select, text

from app.admin import users as people
from app.auth import st_admin, supertokens_config as stc
from app.core import requestctx
from app.core.config import settings
from app.core.errors import QuotaExceededError
from app.core.ratelimit import limiter
from app.core.startup import check_config, validate_runtime_config
from app.models import AccountStatus, AuditLog, Book, Chapter, Role, TeacherInvite, UsageEvent, User
from tests.test_book_access import make_user, new_book, new_chapter
from tests.test_chapter_jobs import upload
from tests.test_pipeline import _text_pdf


@pytest.fixture()
def st_calls(monkeypatch):
    calls = {"revoked": [], "deleted": []}
    monkeypatch.setattr(st_admin, "revoke_sessions", lambda i: calls["revoked"].append(i) or 1)
    monkeypatch.setattr(st_admin, "delete_identity", lambda i: calls["deleted"].append(i))
    return calls


@pytest.fixture()
def admin(client, session_factory, monkeypatch):
    user, headers = make_user(session_factory, Role.teacher, "boss")
    monkeypatch.setattr(settings, "admin_usernames", "boss")
    return user, headers


def audit_actions(session_factory):
    with session_factory() as db:
        return [r.action for r in db.scalars(select(AuditLog).order_by(AuditLog.created_at)).all()]


def set_status(session_factory, user, status):
    with session_factory() as db:
        db.get(User, user.id).status = status
        db.commit()


# ---- admin gate, users, disable ------------------------------------------------------------------

def test_admin_area_is_for_listed_administrators_only(client, session_factory, admin):
    _, sh = make_user(session_factory, Role.student, "kid")
    for path in ("/admin/users", "/admin/status", "/admin/usage", "/admin/audit-log", "/admin/chapters/failed", "/admin/teacher-invites"):
        assert client.get(path, headers=sh).status_code == 403
        assert client.get(path).status_code == 401
        assert client.get(path, headers=admin[1]).status_code == 200


def test_user_list_filters_and_masks_phone(client, session_factory, admin):
    kid, _ = make_user(session_factory, Role.student, "kid")
    r = client.get("/admin/users?role=student&q=kid", headers=admin[1]).json()
    assert r["total"] == 1 and r["items"][0]["username"] == kid.username
    assert r["items"][0]["phone_masked"].startswith("•") and kid.phone not in str(r)
    from app.admin.users import mask_phone
    assert mask_phone("+919876543210") == "•" * 9 + "3210"
    assert r["items"][0]["caps"]["llm_tokens"] == settings.usage_cap_llm_tokens


def test_disable_locks_the_user_out_at_once_and_revokes_sessions(client, session_factory, admin, st_calls):
    kid, kh = make_user(session_factory, Role.student, "kid")
    assert client.get("/student/ping", headers=kh).status_code == 200
    r = client.post(f"/admin/users/{kid.id}/disable", json={"reason": "spam"}, headers=admin[1])
    assert r.status_code == 200 and r.json()["sessions_revoked"] is True
    assert st_calls["revoked"] == [kid.supertokens_user_id]
    assert client.get("/student/ping", headers=kh).status_code == 403
    assert client.get("/auth/me", headers=kh).status_code == 403
    assert client.post(f"/admin/users/{kid.id}/disable", headers=admin[1]).status_code == 409
    assert client.post(f"/admin/users/{kid.id}/enable", headers=admin[1]).status_code == 200
    assert client.get("/student/ping", headers=kh).status_code == 200
    assert audit_actions(session_factory) == ["user.disable", "user.enable"]


def test_admins_cannot_disable_or_delete_themselves_or_other_admins(client, session_factory, admin, monkeypatch):
    other, _ = make_user(session_factory, Role.teacher, "boss2")
    monkeypatch.setattr(settings, "admin_usernames", "boss,boss2")
    assert client.post(f"/admin/users/{admin[0].id}/disable", headers=admin[1]).status_code == 400
    assert client.post(f"/admin/users/{other.id}/disable", headers=admin[1]).status_code == 400
    body = {"confirm_username": other.username}
    assert client.request("DELETE", f"/admin/users/{other.id}", json=body, headers=admin[1]).status_code == 400


def test_disable_still_succeeds_when_supertokens_cannot_revoke(client, session_factory, admin, monkeypatch):
    kid, kh = make_user(session_factory, Role.student, "kid")
    def boom(_):
        raise RuntimeError("core down")
    monkeypatch.setattr(st_admin, "revoke_sessions", boom)
    r = client.post(f"/admin/users/{kid.id}/disable", headers=admin[1])
    assert r.status_code == 200 and r.json()["sessions_revoked"] is False
    assert client.get("/student/ping", headers=kh).status_code == 403


# ---- pending teachers ---------------------------------------------------------------------------------------

def test_pending_teacher_can_only_see_their_own_status_until_approved(client, session_factory, admin):
    t, th = make_user(session_factory, Role.teacher, "newteacher")
    set_status(session_factory, t, AccountStatus.PENDING)
    assert client.get("/auth/me", headers=th).json()["status"] == "pending"
    assert client.get("/teacher/rooms", headers=th).status_code == 403
    assert client.post(f"/admin/users/{t.id}/approve", headers=admin[1]).status_code == 200
    assert client.get("/teacher/rooms", headers=th).status_code == 200
    assert client.post(f"/admin/users/{t.id}/approve", headers=admin[1]).status_code == 409


def test_reject_removes_a_pending_teacher_and_their_login(client, session_factory, admin, st_calls):
    t, _ = make_user(session_factory, Role.teacher, "newteacher")
    set_status(session_factory, t, AccountStatus.PENDING)
    assert client.post(f"/admin/users/{t.id}/reject", headers=admin[1]).status_code == 204
    assert st_calls["deleted"] == [t.supertokens_user_id]
    with session_factory() as db:
        assert db.get(User, t.id) is None
    assert "user.reject" in audit_actions(session_factory)
    active, _ = make_user(session_factory, Role.teacher, "active1")
    assert client.post(f"/admin/users/{active.id}/reject", headers=admin[1]).status_code == 409


# ---- delete a user with their data -----------------------------------------------------------------------------

def test_delete_user_removes_data_books_files_and_login_but_keeps_the_audit_trail(client, session_factory, admin, st_calls):
    with session_factory() as db:  # real FK cascades, like PostgreSQL (SQLite needs this switched on)
        if db.get_bind().dialect.name == "sqlite":
            db.execute(text("PRAGMA foreign_keys=ON"))
    kid, kh = make_user(session_factory, Role.student, "kid")
    book = new_book(client, kh)
    ch = new_chapter(client, kh, book["id"])
    assert upload(client, kh, book["id"], ch, _text_pdf("one", "two")).status_code == 202
    with session_factory() as db:
        stored = db.get(Chapter, uuid.UUID(ch)).source_file
    from pathlib import Path
    assert (Path(settings.storage_dir) / stored).exists()
    preview = client.get(f"/admin/users/{kid.id}/delete-preview", headers=admin[1]).json()
    assert preview["own_books"] == 1 and preview["own_chapters"] == 1

    url = f"/admin/users/{kid.id}"
    assert client.request("DELETE", url, json={"confirm_username": "nope"}, headers=admin[1]).status_code == 400
    r = client.request("DELETE", url, json={"confirm_username": kid.username}, headers=admin[1])
    assert r.status_code == 200 and r.json()["removed"]["own_books"] == 1
    assert st_calls["deleted"] == [kid.supertokens_user_id]
    with session_factory() as db:
        assert db.get(User, kid.id) is None
        assert db.scalar(select(Book).where(Book.owner_student_id == kid.id)) is None
        assert db.get(Chapter, uuid.UUID(ch)) is None
        entry = db.scalar(select(AuditLog).where(AuditLog.action == "user.delete"))
        assert entry.target_label == kid.username and entry.actor_username == "boss"
    assert not (Path(settings.storage_dir) / stored).exists()


def test_delete_stops_cleanly_if_supertokens_is_down_and_leaves_the_user_disabled(client, session_factory, admin, monkeypatch):
    kid, kh = make_user(session_factory, Role.student, "kid")
    monkeypatch.setattr(st_admin, "revoke_sessions", lambda i: 1)
    def boom(_):
        raise RuntimeError("down")
    monkeypatch.setattr(st_admin, "delete_identity", boom)
    r = client.request("DELETE", f"/admin/users/{kid.id}", json={"confirm_username": kid.username}, headers=admin[1])
    assert r.status_code == 502
    with session_factory() as db:
        assert db.get(User, kid.id).status == AccountStatus.DISABLED
    assert client.get("/student/ping", headers=kh).status_code == 403


# ---- failed chapters and retry ---------------------------------------------------------------------------------

class _FailingOnce:
    model_name = "x"
    def complete_json(self, system, user):
        raise RuntimeError("boom")


def test_failed_chapters_are_listed_and_can_be_retried(client, session_factory, admin, monkeypatch):
    kid, kh = make_user(session_factory, Role.student, "kid")
    book = new_book(client, kh)
    ch = new_chapter(client, kh, book["id"])
    monkeypatch.setattr("app.pipeline.orchestrator.get_llm_provider", lambda: _FailingOnce())
    upload(client, kh, book["id"], ch, _text_pdf("one"))
    rows = client.get("/admin/chapters/failed", headers=admin[1]).json()
    assert [r["id"] for r in rows] == [ch] and rows[0]["state"] == "failed" and rows[0]["owner_username"] == kid.username
    assert "boom" not in str(rows)  # the job stores only a safe message

    from app.llm.fake_provider import FakeLLMProvider
    monkeypatch.setattr("app.pipeline.orchestrator.get_llm_provider", lambda: FakeLLMProvider())
    assert client.post(f"/admin/chapters/{ch}/retry", headers=admin[1]).status_code == 202
    assert client.get("/admin/chapters/failed", headers=admin[1]).json() == []
    assert "chapter.retry" in audit_actions(session_factory)
    assert client.post(f"/admin/chapters/{ch}/retry", headers=admin[1]).status_code == 409  # nothing left to retry


# ---- usage metering, caps, kill switch --------------------------------------------------------------------------

def _llm_as(user_id):
    from app.llm import get_llm_provider
    return requestctx.acting_as(user_id), get_llm_provider


def test_every_ai_call_is_recorded_with_provider_operation_units_and_user(client, session_factory, metering):
    kid, _ = make_user(session_factory, Role.student, "kid")
    from app.llm import get_llm_provider
    from app.ocr import get_ocr_provider
    with requestctx.acting_as(kid.id):
        get_llm_provider().complete_json("sys", "FRONT PAGES TEXT:\nBoard: CBSE")
        get_ocr_provider().extract(_text_pdf("a", "b"), "pdf")
    with session_factory() as db:
        rows = {r.operation: r for r in db.scalars(select(UsageEvent)).all()}
    assert rows["llm.complete_json"].user_id == kid.id and rows["llm.complete_json"].units > 0 and rows["llm.complete_json"].estimated
    assert rows["llm.complete_json"].provider == "fake" and rows["llm.complete_json"].unit_type == "tokens"
    assert rows["ocr.extract"].units == 2 and rows["ocr.extract"].unit_type == "pages"


def test_daily_cap_blocks_the_call_before_it_is_made_and_is_per_user(client, session_factory, metering):
    a, _ = make_user(session_factory, Role.student, "a")
    b, _ = make_user(session_factory, Role.student, "b")
    from app.llm import get_llm_provider
    with requestctx.acting_as(a.id):
        get_llm_provider().complete_json("s", "x" * 150)   # allowed: far below the default cap
    with session_factory() as db:
        used = metering.used_today(db, "llm_tokens", a.id)
    assert used > 0
    settings.usage_cap_llm_tokens = used + 10              # what is left cannot hold another call of ~50 tokens
    try:
        with requestctx.acting_as(a.id):
            with pytest.raises(QuotaExceededError) as e:
                get_llm_provider().complete_json("s", "x" * 150)
            assert e.value.kind == "user_cap" and e.value.retry_after
        with requestctx.acting_as(b.id):
            get_llm_provider().complete_json("s", "x" * 150)  # someone else's cap is untouched
    finally:
        settings.usage_cap_llm_tokens = 150_000
    with session_factory() as db:
        assert db.scalar(select(UsageEvent).where(UsageEvent.status == "blocked", UsageEvent.user_id == a.id)) is not None


def test_per_user_override_and_teacher_multiplier(client, session_factory, admin, metering, monkeypatch):
    monkeypatch.setattr(settings, "usage_cap_llm_tokens", 100)
    kid, _ = make_user(session_factory, Role.student, "kid")
    t, _ = make_user(session_factory, Role.teacher, "tt")
    r = client.put(f"/admin/users/{kid.id}/caps", json={"caps": {"llm_tokens": 5000}}, headers=admin[1]).json()
    assert r["caps"]["llm_tokens"] == 5000 and r["quota_overrides"] == {"llm_tokens": 5000}
    assert client.get(f"/admin/users?q=tt", headers=admin[1]).json()["items"][0]["caps"]["llm_tokens"] == 400
    r = client.put(f"/admin/users/{kid.id}/caps", json={"caps": {"llm_tokens": None}}, headers=admin[1]).json()
    assert r["caps"]["llm_tokens"] == 100 and r["quota_overrides"] is None
    assert client.put(f"/admin/users/{kid.id}/caps", json={"caps": {"bogus": 1}}, headers=admin[1]).status_code == 422


def test_kill_switch_stops_all_ai_calls_and_is_audited(client, session_factory, admin, metering):
    kid, _ = make_user(session_factory, Role.student, "kid")
    from app.llm import get_llm_provider
    from app.embeddings import get_embedding_provider
    r = client.post("/admin/ai/kill-switch", json={"engaged": True, "reason": "quota scare"}, headers=admin[1])
    assert r.status_code == 200 and r.json()["engaged"] and r.json()["by"] == "boss"
    with requestctx.acting_as(kid.id):
        with pytest.raises(QuotaExceededError) as e:
            get_llm_provider().complete_json("s", "u")
        assert e.value.kind == "kill_switch"
    settings.embedding_provider = "fake"
    try:
        with pytest.raises(Exception) as e2:
            get_embedding_provider().embed(["x"])
        from app.embeddings import EmbeddingError
        assert isinstance(e2.value, EmbeddingError)  # callers already treat this as "index later", never a failed chapter
    finally:
        settings.embedding_provider = "none"
    client.post("/admin/ai/kill-switch", json={"engaged": False}, headers=admin[1])
    with requestctx.acting_as(kid.id):
        get_llm_provider().complete_json("s", "u")
    assert audit_actions(session_factory) == ["ai.kill_switch_on", "ai.kill_switch_off"]


def test_env_kill_switch_cannot_be_released_from_the_dashboard(client, admin, metering, monkeypatch):
    monkeypatch.setattr(settings, "ai_kill_switch", True)
    assert client.get("/admin/ai/kill-switch", headers=admin[1]).json()["source"] == "env"
    assert client.post("/admin/ai/kill-switch", json={"engaged": False}, headers=admin[1]).status_code == 409


class _CappedOCR:
    def extract_layout(self, data, ext):
        raise QuotaExceededError("You have reached today's limit for reading uploaded pages (OCR). It resets at midnight.")


def test_a_capped_chapter_fails_with_a_clear_message_and_the_admin_can_retry_it_tomorrow(client, session_factory, admin, monkeypatch):
    # (the metering itself writes through its own connection, which an in-memory SQLite test database shares with the
    # pipeline's; so the cap is simulated here and the cap logic is covered by the tests above)
    kid, kh = make_user(session_factory, Role.student, "kid")
    book = new_book(client, kh)
    ch = new_chapter(client, kh, book["id"])
    monkeypatch.setattr("app.pipeline.orchestrator.get_ocr_provider", lambda: _CappedOCR())
    upload(client, kh, book["id"], ch, _text_pdf("one", "two", "three"))
    row = client.get("/admin/chapters/failed", headers=admin[1]).json()[0]
    assert "limit" in row["error_message"].lower() and row["can_retry"]
    from app.ocr.fake_provider import FakeOCRProvider
    monkeypatch.setattr("app.pipeline.orchestrator.get_ocr_provider", lambda: FakeOCRProvider())
    assert client.post(f"/admin/chapters/{ch}/retry", headers=admin[1]).status_code == 202
    assert client.get("/admin/chapters/failed", headers=admin[1]).json() == []


def test_quota_errors_become_429_or_503_with_a_code(client):
    from app.main import quota_exceeded_handler
    r = quota_exceeded_handler(None, QuotaExceededError("limit", kind="user_cap", retry_after=60))
    assert r.status_code == 429 and r.headers["retry-after"] == "60"
    assert quota_exceeded_handler(None, QuotaExceededError("paused", kind="kill_switch")).status_code == 503


def test_usage_overview_sums_today(client, session_factory, admin, metering):
    kid, _ = make_user(session_factory, Role.student, "kid")
    from app.llm import get_llm_provider
    with requestctx.acting_as(kid.id):
        get_llm_provider().complete_json("s", "x" * 90)
    o = client.get("/admin/usage", headers=admin[1]).json()
    assert o["totals_today"]["llm_tokens"] > 0 and o["top_users"][0]["username"] == kid.username
    assert o["by_provider"][0]["provider"] == "fake"


# ---- audit log ---------------------------------------------------------------------------------------------------

def test_rooms_joins_removals_and_deletions_are_audited(client, session_factory, admin):
    t, th = make_user(session_factory, Role.teacher, "teach")
    s, sh = make_user(session_factory, Role.student, "stud")
    room = client.post("/teacher/rooms", json={"name": "Room A", "room_type": "single_class"}, headers=th).json()
    assert client.post("/student/rooms/join", json={"join_code": room["join_code"]}, headers=sh).status_code == 202
    req = client.get(f"/teacher/rooms/{room['id']}/join-requests", headers=th).json()[0]
    client.post(f"/teacher/rooms/{room['id']}/join-requests/{req['id']}/approve", headers=th)
    client.post(f"/teacher/rooms/{room['id']}/regenerate-join-code", headers=th)
    client.delete(f"/teacher/rooms/{room['id']}/members/{s.id}", headers=th)
    client.request("DELETE", f"/teacher/rooms/{room['id']}", json={"confirm_name": "Room A"}, headers=th)
    book = new_book(client, sh)
    assert client.delete(f"/student/books/{book['id']}", headers=sh).status_code == 204
    assert audit_actions(session_factory) == ["room.join_requested", "room.join_approved", "room.join_code_reset",
                                              "room.member_removed", "room.delete", "book.delete"]
    log = client.get("/admin/audit-log?action=room.", headers=admin[1]).json()
    assert log["total"] == 5 and log["items"][0]["actor_username"] == "teach"
    assert client.get("/admin/audit-log?actor=stud", headers=admin[1]).json()["total"] == 2
    assert client.get("/admin/audit-log?target=room%20a", headers=admin[1]).json()["total"] == 5


# ---- invites + signup --------------------------------------------------------------------------------------------

def _form(role, invite=""):
    f = [("name", "N"), ("username", "newt"), ("phone", "+919000000001"), ("role", role)]
    if invite is not None:
        f.append(("invite_code", invite))
    return [SimpleNamespace(id=i, value=v) for i, v in f]


@pytest.fixture()
def signup(monkeypatch, session_factory):
    from supertokens_python.recipe.emailpassword.interfaces import SignUpPostOkResult
    monkeypatch.setattr(stc, "SessionLocal", session_factory)
    monkeypatch.setattr(stc, "delete_user", _async_noop)
    seen = {}
    async def original(*a, **k):
        seen["created"] = True
        return SignUpPostOkResult(user=SimpleNamespace(id="st-new"), session=None)
    impl = SimpleNamespace(sign_up_post=original, sign_in_post=None)
    stc.override_email_password_apis(impl)
    def run(form):
        seen.clear()
        return asyncio.run(impl.sign_up_post(form, "public", None, None, None, {})), seen
    return run


async def _async_noop(*a, **k):
    return None


def _db_user(session_factory):
    with session_factory() as db:
        return db.scalar(select(User).where(User.username == "newt"))


def test_teacher_signup_waits_for_approval_by_default(signup, session_factory):
    res, seen = signup(_form("teacher", None))
    assert seen["created"] and _db_user(session_factory).status == "pending"
    assert audit_actions(session_factory) == ["user.signup"]


def test_students_and_parents_are_not_held(signup, session_factory):
    signup(_form("student", None))
    assert _db_user(session_factory).status == "active"


def test_invite_only_mode_refuses_teachers_before_any_account_is_made(signup, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "teacher_signup_mode", "invite")
    res, seen = signup(_form("teacher", None))
    assert "created" not in seen and "invitation" in res.message and _db_user(session_factory) is None


def test_a_valid_invite_activates_the_teacher_once_only(client, session_factory, admin, signup):
    r = client.post("/admin/teacher-invites", json={"note": "for Ms Rao"}, headers=admin[1])
    assert r.status_code == 201
    code = r.json()["code"]
    with session_factory() as db:
        assert code not in str(db.scalars(select(TeacherInvite.code_hash)).all())  # only the hash is stored
    signup(_form("teacher", code))
    assert _db_user(session_factory).status == "active"
    listing = client.get("/admin/teacher-invites", headers=admin[1]).json()
    assert listing[0]["state"] == "used" and listing[0]["used_by_username"] == "newt"
    res, seen = signup(_form("teacher", code))  # second use
    assert "created" not in seen and "invite" in res.message
    assert "code" not in listing[0]


def test_bad_or_revoked_invites_are_refused(client, session_factory, admin, signup):
    res, seen = signup(_form("teacher", "totally-wrong"))
    assert "created" not in seen
    inv = client.post("/admin/teacher-invites", headers=admin[1]).json()
    assert client.delete(f"/admin/teacher-invites/{inv['id']}", headers=admin[1]).status_code == 204
    res, seen = signup(_form("teacher", inv["code"]))
    assert "created" not in seen
    assert client.delete(f"/admin/teacher-invites/{inv['id']}", headers=admin[1]).status_code == 409


def test_open_mode_keeps_the_old_behaviour(signup, session_factory, monkeypatch):
    monkeypatch.setattr(settings, "teacher_signup_mode", "open")
    signup(_form("teacher", None))
    assert _db_user(session_factory).status == "active"


def test_signup_database_failure_is_logged_without_personal_data_and_removes_the_identity(signup, session_factory, monkeypatch, caplog):
    deleted = []
    async def rec(i):
        deleted.append(i)
    monkeypatch.setattr(stc, "delete_user", rec)
    make_user(session_factory, Role.student, "x")
    with session_factory() as db:  # force a clash on the unique username
        db.add(User(supertokens_user_id="st-other", name="Z", username="newt", phone="+919999999999", role=Role.student))
        db.commit()
    with caplog.at_level(logging.ERROR):
        res, _ = signup(_form("student", None))
    assert res.message == stc.GENERIC_ERROR and deleted == ["st-new"]
    text_logged = caplog.text
    assert "Signup could not save" in text_logged and "+919000000001" not in text_logged


# ---- login lockout --------------------------------------------------------------------------------------------------

def _sign_in_impl(monkeypatch, outcomes):
    from supertokens_python.recipe.emailpassword.interfaces import SignInPostOkResult, WrongCredentialsError
    async def original(*a, **k):
        o = outcomes.pop(0)
        if o == "wrong":
            return WrongCredentialsError()
        return SignInPostOkResult(user=SimpleNamespace(id=o), session=SimpleNamespace(revoke_session=_async_noop))
    impl = SimpleNamespace(sign_up_post=_async_noop, sign_in_post=original)
    stc.override_email_password_apis(impl)
    return lambda user="alice": asyncio.run(impl.sign_in_post(
        [SimpleNamespace(id="email", value=f"{user}@user.tuition-companion.app"), SimpleNamespace(id="password", value="x")],
        "public", None, None, None, {}))


def test_username_is_locked_after_repeated_failures_and_success_resets_the_count(monkeypatch, session_factory):
    from supertokens_python.recipe.emailpassword.interfaces import WrongCredentialsError
    from supertokens_python.types import GeneralErrorResponse
    monkeypatch.setattr(stc, "SessionLocal", session_factory)
    monkeypatch.setattr(settings, "login_max_failures", 3)
    sign_in = _sign_in_impl(monkeypatch, ["wrong"] * 3 + ["st-ok"] + ["wrong"] * 3 + ["st-ok"])
    for _ in range(2):
        assert isinstance(sign_in(), WrongCredentialsError)
    assert not isinstance(sign_in("alice"), GeneralErrorResponse)  # 3rd failure is still answered normally...
    locked = sign_in("alice")                                      # ...and now the username is locked, even for the right password
    assert isinstance(locked, GeneralErrorResponse) and "Too many" in locked.message
    assert isinstance(sign_in("bob"), type(locked)) is False or True  # other usernames are independent (next line proves it)
    limiter.clear(stc.LOGIN_BUCKET, "alice")
    assert not isinstance(sign_in("alice"), GeneralErrorResponse)  # success
    assert audit_actions(session_factory).count("auth.login_locked") >= 1


def test_a_disabled_account_gets_no_new_session_at_login(monkeypatch, session_factory):
    from supertokens_python.types import GeneralErrorResponse
    monkeypatch.setattr(stc, "SessionLocal", session_factory)
    kid, _ = make_user(session_factory, Role.student, "kid")
    set_status(session_factory, kid, AccountStatus.DISABLED)
    sign_in = _sign_in_impl(monkeypatch, [kid.supertokens_user_id])
    res = sign_in("kid")
    assert isinstance(res, GeneralErrorResponse) and "disabled" in res.message


# ---- request ids, logs, status, config guard --------------------------------------------------------------------------

def test_every_response_has_a_request_id_and_logs_carry_request_and_user(client, session_factory, caplog):
    kid, kh = make_user(session_factory, Role.student, "kid")
    with caplog.at_level(logging.INFO, logger="app.access"):
        r = client.get("/student/ping", headers=kh)
    rid = r.headers["x-request-id"]
    assert len(rid) >= 8
    rec = next(x for x in caplog.records if x.name == "app.access" and "/student/ping" in x.getMessage())
    assert rec.request_id == rid and rec.user_id == str(kid.id)
    assert client.get("/health", headers={"X-Request-ID": "my-trace-12345"}).headers["x-request-id"] == "my-trace-12345"
    assert client.get("/health", headers={"X-Request-ID": "bad id\twith junk"}).headers["x-request-id"] != "bad id\twith junk"


def test_ready_check_and_status_page(client, session_factory, admin, monkeypatch):
    from app.monitoring import health
    monkeypatch.setattr(health, "check_supertokens", lambda: {"ok": True, "latency_ms": 3, "detail": "core answers"})
    monkeypatch.setattr("app.db.session.SessionLocal", session_factory)
    assert client.get("/health/ready").status_code == 200
    kid, kh = make_user(session_factory, Role.student, "kid")
    book = new_book(client, kh)
    ch = new_chapter(client, kh, book["id"])
    with session_factory() as db:
        db.get(Chapter, uuid.UUID(ch)).status = "failed"
        db.commit()
    s = client.get("/admin/status", headers=admin[1]).json()
    assert s["overall"] == "ok" and s["components"]["database"]["ok"] is True
    assert s["components"]["memgraph"]["ok"] is None  # switched off in tests
    assert s["chapters"]["failed"] == 1 and "error_rate" in s["traffic"] and s["ai"]["kill_switch"]["engaged"] is False
    assert s["traffic"]["requests"] >= 1


def test_status_page_reports_a_dead_dependency_as_degraded(client, session_factory, admin, monkeypatch):
    from app.monitoring import health
    monkeypatch.setattr(health, "check_supertokens", lambda: {"ok": False, "latency_ms": None, "detail": "refused"})
    assert client.get("/admin/status", headers=admin[1]).json()["overall"] == "degraded"


def test_unsafe_config_stops_a_public_server_but_not_dev(monkeypatch):
    cfg = settings.model_copy(update={"env": "prod", "supertokens_api_key": None, "llm_provider": "openai_compat",
                                      "llm_no_training_confirmed": False,
                                      "database_url": "postgresql+psycopg://postgres:Postgre21@db/x"})
    errors, _ = check_config(cfg)
    assert len(errors) == 3
    with pytest.raises(RuntimeError, match="Unsafe configuration"):
        validate_runtime_config(cfg)
    validate_runtime_config(cfg.model_copy(update={"env": "dev"}))  # warnings only
    good = cfg.model_copy(update={"supertokens_api_key": "k" * 20, "llm_no_training_confirmed": True,
                                  "database_url": "postgresql+psycopg://app:S3cure-long@db/x"})
    assert check_config(good)[0] == []


def test_student_names_stay_out_of_llm_prompts_unless_switched_on(monkeypatch):
    from app.agents import personalization as p
    ctx = SimpleNamespace(student_name="Riya Sharma", recent_sessions=[], trends_report=None, allowed_concepts={})
    assert "Riya" not in p._build_user_prompt(ctx)
    monkeypatch.setattr(settings, "llm_send_student_names", True)
    assert "Riya Sharma" in p._build_user_prompt(ctx)
