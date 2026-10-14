"""Phase 3 step 8: the exit check (`python -m app.db.phase3_check`) itself is tested here, on a small seeded database with
placeholder embeddings, a fake model and the in-memory store. It must run clean, keep nothing, and actually catch a leak."""
import types

import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db import phase3_check
from app.models import Assignment, Base, Book, Concept, ConceptEdge, CrossChapterEdge, Doubt, MasteryEvent, PageKind, User
from app.pipeline.indexing import index_chapter
from tests.test_phase3_settle import add_chapter

TEXT = lambda *w: " ".join(w) * 3  # noqa: E731


@pytest.fixture()
def real_savepoints_engine(tmp_path):
    """A file SQLite engine whose savepoints behave (pysqlite needs the documented workaround), like PostgreSQL."""
    engine = create_engine(f"sqlite:///{tmp_path / 'p3.db'}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _connect(dbapi_connection, _):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _begin(conn):
        conn.exec_driver_sql("BEGIN")

    Base.metadata.create_all(engine)
    return engine


def seed(factory):
    with factory() as db:
        maths = Book(board="CBSE", class_name="9", subject="Mathematics", publisher="NCERT", is_reference=True)
        sci = Book(board="CBSE", class_name="9", subject="Science", publisher="NCERT", is_reference=True)
        db.add_all([maths, sci])
        db.flush()
        coords = add_chapter(db, maths, "Coordinates", 1, [
            (1, TEXT("A coordinate system uses a grid of horizontal x axis and vertical y axis lines to locate any point in the plane "), PageKind.CONTENT),
            (2, TEXT("The origin is the point where the x axis and y axis meet and its coordinates are zero zero "), PageKind.CONTENT),
            (3, TEXT("Quadrants are the four regions the axes divide the plane into and points have signs by quadrant "), PageKind.CONTENT),
            (4, "Exercises 1. What are the coordinates of the origin 2. Name the quadrant of a point with negative x axis value " * 2, PageKind.EXERCISE)],
            [(1, "Coordinate system", "a grid of x axis and y axis lines to locate points"), (2, "Origin", "the point where the axes meet with coordinates zero zero"),
             (3, "Quadrants", "four regions of the plane divided by the axes")])
        lines = add_chapter(db, maths, "Linear equations", 2, [
            (1, TEXT("A linear equation in two variables has the form a x plus b y plus c equals zero and its graph is a straight line "), PageKind.CONTENT)],
            [(1, "Linear equation", "equation of the form ax plus by plus c equals zero")])
        cells = add_chapter(db, sci, "Cells", 1, [
            (1, TEXT("The cell is the basic unit of life and a cell has a membrane a nucleus and cytoplasm inside it "), PageKind.CONTENT)],
            [(1, "Cell", "basic unit of life with membrane nucleus and cytoplasm")])
        for ch in (coords, lines, cells):
            ch.graph_report = {"concepts": 3, "model": "x", "llm_linking": "done"}
        db.flush()
        c = {x.name: x for x in db.scalars(select(Concept))}
        db.add(ConceptEdge(chapter_id=coords.id, concept_id=c["Origin"].id, prerequisite_id=c["Coordinate system"].id, source="llm"))
        db.add(ConceptEdge(chapter_id=coords.id, concept_id=c["Quadrants"].id, prerequisite_id=c["Origin"].id, source="llm"))
        db.add(CrossChapterEdge(chapter_id=lines.id, concept_id=c["Linear equation"].id, prerequisite_id=c["Quadrants"].id, similarity=0.6))
        db.commit()
        ids = [coords.id, lines.id, cells.id]
    for i in ids:
        index_chapter(factory, i)


def opts(**kw):
    return types.SimpleNamespace(**{**dict(book=None, other_book=None, skip_model=True, allow_fake=True), **kw})


@pytest.fixture()
def world(real_savepoints_engine, indexing_on, monkeypatch):
    monkeypatch.setattr(settings, "retrieval_min_similarity", 0.12)
    factory = sessionmaker(bind=real_savepoints_engine, autoflush=False)
    seed(factory)
    return real_savepoints_engine, factory


def lines_with(lines, status):
    return [ln for ln in lines if ln.startswith(status)]


def test_the_exit_check_runs_without_a_fail_and_keeps_nothing(world):
    engine, factory = world
    lines, fails = phase3_check.run(engine, opts())
    real_fails = [ln for ln in lines_with(lines, "FAIL") if " M1 " not in ln]  # the test database is not built by alembic
    assert not real_fails, "\n".join(real_fails)
    text = "\n".join(lines)
    for tag in ("A1", "A9", "K6", "K8", "K12", "K14", "L1", "L7", "R9"):
        assert any(ln.startswith("PASS") and f" {tag} " in ln for ln in lines), f"{tag} did not pass:\n{text}"
    with factory() as db:  # everything was rolled back
        for model in (User, Assignment, Doubt, MasteryEvent):
            assert db.scalar(select(func.count()).select_from(model)) == 0
        assert db.scalar(select(func.count()).select_from(Book)) == 2  # only the seeded official books


def test_the_exit_check_catches_a_tenancy_leak(world, monkeypatch):
    """Break the rule that a student only sees assignments on books they linked: the check must FAIL, not pass."""
    from app.assignments import service
    from app.models import Assignment as A
    from sqlalchemy import or_
    from app.models import RoomMember

    def leaky(student):
        my_rooms = select(RoomMember.room_id).where(RoomMember.user_id == student.id)
        return select(A).where(or_(A.student_id == student.id, A.room_id.in_(my_rooms)))  # no 'linked book' condition

    monkeypatch.setattr(service, "student_assignments_query", leaky)
    engine, _ = world
    lines, fails = phase3_check.run(engine, opts())
    assert any(ln.startswith("FAIL") and (" A10 " in ln or " L7 " in ln) for ln in lines), "\n".join(lines)


def test_the_exit_check_fails_clearly_without_real_providers(world):
    engine, _ = world
    lines, fails = phase3_check.run(engine, opts(allow_fake=False, skip_model=True))
    assert fails >= 1 and any("EMBEDDING_PROVIDER" in ln and ln.startswith("FAIL") for ln in lines)


def test_a_measured_rate_only_fails_far_below_the_probe_and_never_with_placeholders():
    assert phase3_check.graded(1.0, 1.0, 0.6, "R1", "ok", "", False)[0] == "PASS"
    assert phase3_check.graded(0.7, 1.0, 0.6, "R1", "ok", "", False)[0] == "REVIEW"
    assert phase3_check.graded(0.3, 1.0, 0.6, "R1", "ok", "", False)[0] == "FAIL"
    assert phase3_check.graded(0.0, 1.0, 0.6, "R1", "ok", "", True)[0] == "REVIEW"


def test_spread_samples_the_whole_list_not_its_start():
    assert phase3_check.spread(list(range(100)), 4) == [12, 37, 62, 87]
    assert phase3_check.spread([1, 2], 5) == [1, 2]
