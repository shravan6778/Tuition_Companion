import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SUPERTOKENS_CONNECTION_URI", "http://localhost:3567")

import pytest
from fastapi import HTTPException, Request, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import session_dependency
from app.db.session import get_db, get_session_factory
from app.main import app
from app.models import Base


class FakeSession:
    def __init__(self, user_id: str):
        self._user_id = user_id

    def get_user_id(self) -> str:
        return self._user_id


@pytest.fixture()
def session_factory():
    # Default: in-memory SQLite. Set TEST_DATABASE_URL (e.g. a throwaway local Postgres) to run the same
    # tests on the real database engine; tables are created and dropped around every test.
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        engine = create_engine(url)
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False)
    if url:
        engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_session(request: Request):
        # Stands in for a real session cookie: "Authorization: Bearer <supertokens_user_id>"
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        return FakeSession(auth.removeprefix("Bearer "))

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[session_dependency] = override_session
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    yield TestClient(app)
    app.dependency_overrides.clear()
    

@pytest.fixture()
def db_session(session_factory):
    with session_factory() as db:
        yield db


@pytest.fixture()
def make_user(session_factory):
    counter = {"n": 0}

    def _make(role, phone=None, name="Test User"):
        counter["n"] += 1
        suffix = f"{counter['n']:04d}"
        phone = phone or f"+91900000{suffix}"
        with session_factory() as db:
            user = __import__("app.models", fromlist=["User"]).User(
                supertokens_user_id=f"st-{phone}",
                name=name,
                username=f"{role.value}_fixture_{suffix}",
                phone=phone,
                role=role,
                link_code=(f"LINK{suffix}" if role.value == "student" else None),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db.expunge(user)
        return user

    return _make


@pytest.fixture()
def as_user(client):
    def _as_user(user_or_headers):
        headers = user_or_headers if isinstance(user_or_headers, dict) else {"Authorization": f"Bearer {user_or_headers.supertokens_user_id}"}
        client.headers.update(headers)
        return headers
    return _as_user

@pytest.fixture(autouse=True)
def tmp_storage(tmp_path, monkeypatch):
    """Uploads go to a throwaway folder, never the real storage dir."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "storage_dir", str(tmp_path / "storage"))


@pytest.fixture(autouse=True)
def fake_providers(monkeypatch):
    """Tests must never reach real Azure/LLM, even if a developer's .env sets
    OCR_PROVIDER=azure / LLM_PROVIDER=openai_compat (settings reads .env)."""
    from app.core.config import settings

    monkeypatch.setattr(settings, "ocr_provider", "fake")
    monkeypatch.setattr(settings, "llm_provider", "fake")
    # Same for embeddings and Memgraph: off unless a test switches them on (see the `indexing_on` fixture).
    monkeypatch.setattr(settings, "embedding_provider", "none")
    monkeypatch.setattr(settings, "graph_store_provider", "none")
    monkeypatch.setattr(settings, "embedding_dim", 64)


@pytest.fixture()
def indexing_on(monkeypatch):
    """Fake embeddings + the in-memory graph store, wired the way a configured deployment is."""
    from app.core.config import settings
    from app.graph_store import FAKE_STORE

    monkeypatch.setattr(settings, "embedding_provider", "fake")
    monkeypatch.setattr(settings, "graph_store_provider", "fake")
    FAKE_STORE.clear()
    FAKE_STORE.fail_with = None
    yield FAKE_STORE
    FAKE_STORE.clear()
    FAKE_STORE.fail_with = None


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Rate-limit counters are process-wide; every test starts with a clean slate."""
    from app.core.ratelimit import limiter

    limiter.reset()
    yield
    limiter.reset()
