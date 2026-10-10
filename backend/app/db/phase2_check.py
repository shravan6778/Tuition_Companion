"""Phase 2 exit check: one command that tests every Phase 2 piece on the REAL database and prints PASS / FAIL / REVIEW.

    python -m app.db.phase2_check                 # everything (makes about 10 LLM + 10 embedding calls for Layer 4)
    python -m app.db.phase2_check --skip-probe    # no LLM / embedding calls (Layer 4 shows as REVIEW)

PASS = verified by a rule. FAIL = must be fixed (the line says how), then run it again. REVIEW = a person has to look at the
printed lines (extracted metadata, cross-chapter links). Phase 2 is finished when there is no FAIL and every REVIEW was judged.
Writes nothing: checks that need throwaway rows (Layers 3 and 5) run inside a transaction that is always rolled back."""
import argparse
import sys
import uuid
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.content_library import feedback
from app.core.config import settings
from app.db.match_feedback import FIELDS, _same
from app.db.session import SessionLocal
from app.models import Book, Chapter, ChapterStatus, Concept, CrossChapterEdge, MatchFeedback, Page, Role, User
from app.pipeline import structure

Result = tuple[str, str, str]  # (PASS | FAIL | REVIEW, id, message)
MIN_CONCEPTS = 5  # an official chapter with fewer concepts is a test leftover or a failed extraction
UNRESOLVED_SHARE = 0.05  # unresolved prerequisites up to 5% of a chapter's concepts are tolerated (and shown for review)
MIN_READY_CHAPTERS = 3  # fewer cannot show cross-chapter links or judge graph quality across a book


def _official(db: Session) -> list[Book]:
    return list(db.scalars(select(Book).where(Book.is_reference.is_(True)).order_by(Book.publisher, Book.class_name, Book.subject)))


def _label(book: Book) -> str:
    return f"{book.publisher} {book.class_name} {book.subject}"


def check_migrations(db: Session) -> list[Result]:
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory
    backend = Path(__file__).resolve().parents[2]
    head = ScriptDirectory.from_config(Config(str(backend / "alembic.ini"))).get_current_head()
    current = MigrationContext.configure(db.connection()).get_current_revision()
    if current == head:
        return [("PASS", "M1", f"database is at the latest migration ({head})")]
    return [("FAIL", "M1", f"database is at {current}, code expects {head}: run `alembic upgrade head`")]


def check_official_books(db: Session) -> list[Result]:
    books = _official(db)
    if not books:
        return [("FAIL", "D1", "no official book in the database: ingest one with `python -m app.db.ingest_reference`")]
    out: list[Result] = []
    for book in books:
        chapters = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sequence_num)))
        ready = [c for c in chapters if c.status == ChapterStatus.READY]
        if not chapters:
            out.append(("FAIL", "D2", f"{_label(book)} (edition {book.edition or '-'}, id {book.id}) has no chapters at all: an empty leftover. "
                                      f"Remove it with `python -m app.db.drop_book --book {book.id} --yes` (or as an administrator in the app)"))
            continue
        out.append(("PASS" if len(ready) >= MIN_READY_CHAPTERS else "FAIL", "D2",
                    f"{_label(book)}: {len(ready)} ready chapters of {len(chapters)}"
                    + ("" if len(ready) >= MIN_READY_CHAPTERS else f" (need at least {MIN_READY_CHAPTERS}: ingest more with `ingest_reference ... --append`)")))
        for c in chapters:
            r = c.graph_report or {}
            pages = db.scalar(select(func.count()).select_from(Page).where(Page.chapter_id == c.id))
            name = f"chapter {c.sequence_num} '{c.title}'"
            problems = []
            if c.status != ChapterStatus.READY:
                problems.append(f"status is {c.status}" + (f" ({c.error_message})" if c.error_message else ""))
            else:
                if r.get("model") == "fake":
                    problems.append("concepts were made by the fake LLM (placeholders)")
                if r.get("concepts", 0) < MIN_CONCEPTS:
                    problems.append(f"only {r.get('concepts', 0)} concepts on {pages} pages: a test leftover or a failed extraction "
                                    f"(remove with `python -m app.db.drop_chapter --book {book.id} --number {c.sequence_num} --yes`, or re-ingest it)")
                if c.embedding_status != "done":
                    problems.append(f"embeddings {c.embedding_status}" + (f" ({c.index_error})" if c.index_error else "") + ": run `python -m app.db.sync_graph`")
                if c.graph_sync_status != "done" and settings.graph_store_provider.lower() != "none":
                    problems.append(f"graph store copy {c.graph_sync_status}: run `python -m app.db.sync_graph`")
                unresolved = r.get("unresolved_prerequisites") or []
                if len(unresolved) > max(1, int(UNRESOLVED_SHARE * r.get("concepts", 0))):  # a stray one is normal, many means the linking failed
                    problems.append(f"{len(unresolved)} unresolved prerequisites among {r.get('concepts', 0)} concepts (more than {UNRESOLVED_SHARE:.0%})")
                if r.get("llm_linking") not in ("done",):
                    problems.append(f"concept linking is '{r.get('llm_linking', '-')}', not done")
            if problems:
                out.append(("FAIL", "D3", f"{name}: " + "; ".join(problems)))
            else:
                out.append(("PASS", "D3", f"{name}: {r.get('concepts', 0)} concepts, {r.get('edges', 0)} edges, {pages} pages, embeddings and graph copy done"))
                if unresolved:
                    out.append(("REVIEW", "D4", f"{name}: the text names prerequisites that are not concepts of the chapter (no edge made): "
                                                + "; ".join(f"'{u['concept']}' needs '{u['prerequisite']}'" for u in unresolved[:5])))
                if r.get("review_pages"):
                    out.append(("REVIEW", "D4", f"{name}: pages flagged for review: {[p['page'] for p in r['review_pages']]}"))
    return out


def check_cross_chapter(db: Session) -> list[Result]:
    out: list[Result] = []
    for book in _official(db):
        ready = list(db.scalars(select(Chapter).where(Chapter.book_id == book.id, Chapter.status == ChapterStatus.READY).order_by(Chapter.sequence_num)))
        if len(ready) < 2:
            continue
        missing = [c for c in ready[1:] if ((c.graph_report or {}).get("cross_chapter") or {}).get("status") not in ("done",)]
        if missing:
            out.append(("FAIL", "X1", f"{_label(book)}: cross-chapter step not done for chapter(s) {[c.sequence_num for c in missing]}: "
                                      f"run `python -m app.db.crosslink --book {book.id} --force`"))
            continue
        out.append(("PASS", "X1", f"{_label(book)}: cross-chapter step done for all {len(ready) - 1} later chapters"))
        names = {c.id: c.title for c in ready}
        edges = db.execute(
            select(CrossChapterEdge, Concept).join(Concept, Concept.id == CrossChapterEdge.concept_id)
            .where(CrossChapterEdge.chapter_id.in_(names))
        ).all()
        for edge, concept in edges:
            prereq = db.get(Concept, edge.prerequisite_id)
            pc = db.scalar(select(Chapter).join(Page, Page.chapter_id == Chapter.id).where(Page.id == prereq.page_id))
            out.append(("REVIEW", "X2", f"link to judge (sim {edge.similarity}): '{concept.name}' [{names[edge.chapter_id]}] needs '{prereq.name}' [{pc.title}]"))
        if not edges:
            out.append(("REVIEW", "X2", f"{_label(book)}: no cross-chapter links among {len(ready)} chapters; see candidates with "
                                        f"`python -m app.db.crosslink --book {book.id} --explain` and judge whether zero is right"))
    return out or [("FAIL", "X1", "no official book with two ready chapters, so cross-chapter links cannot be judged")]


def check_front_pages(db: Session) -> list[Result]:
    books = list(db.scalars(select(Book).where(Book.extracted_metadata.is_not(None))))
    if not books:
        return [("FAIL", "L1", "no book was ever created from front pages: upload a teacher book with front pages once")]
    out: list[Result] = [("PASS", "L1", f"{len(books)} book(s) confirmed from front pages")]
    for f in FIELDS:
        for b in books:
            read, final = (b.extracted_metadata or {}).get(f), getattr(b, f)
            if not _same(f, read, final):
                out.append(("REVIEW", "L2", f"front-page field '{f}': read {read!r}, teacher confirmed {final!r} (extraction wrong, or a harmless formatting difference?)"))
    return out


def _throwaway_teacher(db: Session) -> User:
    tag = uuid.uuid4().hex[:10]
    teacher = User(supertokens_user_id=f"check-{tag}", name="phase2 check", username=f"chk{tag}"[:30], phone="0" + tag[:9], role=Role.teacher)
    db.add(teacher)
    db.flush()
    return teacher


def _shortened(title: str, i: int) -> str:
    words = [w for w in title.replace(":", " ").split() if w.lower() not in structure.STOP]
    return " ".join(words[:2]) if len(words) > 2 else title


def check_structure(db: Session) -> list[Result]:
    """SIMULATED editions built from the real official chapter titles (a real second edition is not needed)."""
    out: list[Result] = []
    nested = db.begin_nested()
    try:
        teacher = _throwaway_teacher(db)
        books = [b for b in _official(db) if len(structure._titles(db, b.id, ready_only=True)) >= 2]
        if not books:
            return [("FAIL", "S1", "no official book with two ready chapters to compare titles against")]
        for official in books:
            titles = structure._titles(db, official.id, ready_only=True)
            variants = {
                "shortened titles": [_shortened(t, i) for i, t in enumerate(titles, 1)],
                "titles with 'Unit n:' and a subtitle": [f"Unit {i}: {t} (a complete overview)" for i, t in enumerate(titles, 1)],
            }
            for label, edition in variants.items():
                book = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
                db.add(book)
                db.flush()
                for i, t in enumerate(edition, 1):
                    db.add(Chapter(book_id=book.id, title=t, sequence_num=i, status=ChapterStatus.EMPTY))
                db.flush()
                hit = next((h for h in structure.suggest(db, book, teacher.id) if h["book"].id == official.id), None)
                out.append(("PASS" if hit else "FAIL", "S1", f"{_label(official)}: simulated edition with {label} -> "
                            + (f"suggested ({hit['matched_chapters']}/{hit['chapters_checked']} chapters)" if hit else "NOT suggested")))
            control = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
            db.add(control)
            db.flush()
            for i, t in enumerate(["Gravitation and Free Fall", "Work, Power and Energy", "Sound Waves"], 1):
                db.add(Chapter(book_id=control.id, title=t, sequence_num=i, status=ChapterStatus.EMPTY))
            db.flush()
            wrong = any(h["book"].id == official.id for h in structure.suggest(db, control, teacher.id))
            out.append(("FAIL" if wrong else "PASS", "S2", f"{_label(official)}: book with unrelated chapter titles -> " + ("WRONGLY suggested" if wrong else "not suggested")))
        out.append(("REVIEW", "S3", "Layer 3 was tested on SIMULATED editions made from the real titles; it will not match an edition that rewords titles "
                                    "heavily (e.g. 'Matter in Our Surroundings' vs 'Matter around us'); the page signals cover that case"))
    except Exception as exc:
        out.append(("FAIL", "S1", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}"))
    finally:
        nested.rollback()
    return out


def check_feedback(db: Session) -> list[Result]:
    """Layer 5 round trip on the real database (columns, JSON, unique and check constraints), then rolled back."""
    out: list[Result] = []
    nested = db.begin_nested()
    try:
        official = next(iter(_official(db)), None)
        if official is None:
            return [("FAIL", "F1", "no official book to use as a base")]
        teacher = _throwaway_teacher(db)
        mine = Book(board="X", class_name="9", subject="check", publisher="check", is_reference=False, owner_teacher_id=teacher.id)
        db.add(mine)
        db.flush()
        evidence = {"signal": "pages", "coverage": 0.5, "avg_similarity": 0.91}
        feedback.record(db, mine.id, official.id, "dismissed", evidence)
        ok_dismiss = official.id in feedback.dismissed_ids(db, mine.id)
        feedback.record(db, mine.id, official.id, "confirmed")
        rows = list(db.scalars(select(MatchFeedback).where(MatchFeedback.book_id == mine.id)))
        db.expire_all()
        row = db.scalar(select(MatchFeedback).where(MatchFeedback.book_id == mine.id))
        ok_replace = len(rows) == 1 and row.decision == "confirmed" and row.evidence == evidence and not feedback.dismissed_ids(db, mine.id)
        try:
            with db.begin_nested():
                db.add(MatchFeedback(book_id=mine.id, base_book_id=mine.id, decision="confirmed"))
                db.flush()
            self_pair_blocked = False
        except IntegrityError:
            self_pair_blocked = True
        for ok, what in ((ok_dismiss, "a dismissal is stored and hides the suggestion"),
                         (ok_replace, "a later confirmation replaces it, keeps the evidence, one row per pair"),
                         (self_pair_blocked, "the database refuses a book being its own base")):
            out.append(("PASS" if ok else "FAIL", "F1", what))
        real = db.scalar(select(func.count()).select_from(MatchFeedback).where(MatchFeedback.book_id != mine.id))
        out.append(("REVIEW", "F2", f"{real} real teacher decision(s) recorded so far; thresholds cannot be tuned from decisions until there are "
                                    f"some (`python -m app.db.match_feedback`), the first guesses stay in force until then"))
    except Exception as exc:
        out.append(("FAIL", "F1", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}"))
    finally:
        nested.rollback()
    return out


def check_embedding(db: Session, skip_probe: bool, pages: int = 10) -> list[Result]:
    if skip_probe:
        return [("REVIEW", "E1", "Layer 4 calibration skipped (--skip-probe): run without it")]
    if settings.llm_provider.lower() == "fake" or settings.embedding_provider.lower() in ("fake", "none"):
        return [("FAIL", "E1", "Layer 4 calibration needs the real LLM and the real embedding model (LLM_PROVIDER / EMBEDDING_PROVIDER are fake or none)")]
    from app.embeddings import get_embedding_provider
    from app.llm import get_llm_provider
    from app.pipeline.embedprobe import probe
    r = probe(db, get_llm_provider(), get_embedding_provider(), pages)
    if r["status"] != "done":
        return [("FAIL", "E1", f"calibration could not run: {r}")]
    detail = (f"{r['pages']} pages; reworded copy similarity min {r['same_min']:.3f} / median {r['same_median']:.3f} "
              f"(phrases kept from the original: {r['kept_phrases_median']:.0%}); different pages up to {r['other_max']:.3f} / median {r['other_median']:.3f}"
              + ("" if r["several_chapters"] else " (only one chapter available: 'different' pages come from the same chapter)"))
    if r["pass"]:
        return [("PASS", "E1", f"EMBED_MATCH_SIMILARITY={r['threshold']} finds {r['recall']:.0%} of reworded pages and {r['false_rate']:.0%} of different pages; {detail}")]
    advice = (f"set EMBED_MATCH_SIMILARITY={r['recommended']} in .env and run again" if r["separable"]
              else "reworded and different pages overlap: page embeddings cannot separate them reliably (set EMBED_MATCH_ENABLED=false or raise VARIANT_MIN_COVERAGE)")
    return [("FAIL", "E1", f"EMBED_MATCH_SIMILARITY={r['threshold']} finds {r['recall']:.0%} of reworded pages and {r['false_rate']:.0%} of different pages; "
                           f"{detail}. {advice}")]


def run(db_factory, skip_probe: bool = False) -> tuple[list[str], int]:
    lines: list[str] = []
    counts = {"PASS": 0, "FAIL": 0, "REVIEW": 0}
    sections = [
        ("Database", check_migrations), ("Official books: chapters, graph, embeddings", check_official_books),
        ("Cross-chapter prerequisites", check_cross_chapter), ("Layer 1: front-page metadata", check_front_pages),
        ("Layer 3: chapter-title sequence", check_structure), ("Layer 4: embedding similarity", lambda db: check_embedding(db, skip_probe)),
        ("Layer 5: teacher decisions", check_feedback),
    ]
    with db_factory() as db:
        for title, fn in sections:
            lines.append(f"\n== {title}")
            try:
                results = fn(db)
            except Exception as exc:
                results = [("FAIL", "?", f"check crashed: {type(exc).__name__}: {str(exc)[:200]}")]
            finally:
                db.rollback()  # nothing this script does is ever kept
            for status, tag, message in results:
                counts[status] += 1
                lines.append(f"{status:<6} {tag:<3} {message}")
    lines.append(f"\nRESULT: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['REVIEW']} REVIEW")
    lines.append("Phase 2 can be closed once there is no FAIL and every REVIEW line has been judged." if not counts["FAIL"]
                 else "Phase 2 is NOT finished: fix the FAIL lines (each says how) and run this again.")
    return lines, counts["FAIL"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skip-probe", action="store_true")
    a = parser.parse_args()
    text, fails = run(SessionLocal, a.skip_probe)
    print("\n".join(text))
    sys.exit(1 if fails else 0)
