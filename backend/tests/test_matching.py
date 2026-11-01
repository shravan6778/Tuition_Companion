"""Fingerprints, LSH lookup, Layer-0 file reuse, and the book matches recorded in `chapter.match_report` (Rules.md §3).

Books are private to the student who uploaded them, so a match may only ever name an official book or the SAME student's
other book. The teacher-facing variant endpoints (variant-suggestions / variant-of / chapter-matches) no longer exist;
the report on the chapter is what remains, so these tests read it from the database."""
import uuid

import pytest
from sqlalchemy import select

from app.models import Book, Chapter, ChapterStatus, Page, PageBand, Role
from app.pipeline import matching
from app.pipeline.fingerprint import apply_fingerprint, band_keys, compute_jaccard_similarity, compute_minhash
from app.pipeline.orchestrator import PipelineOrchestrator
from app.ocr.fake_provider import FakeOCRProvider
from tests.test_book_access import make_user, new_book, new_chapter
from tests.test_chapter_jobs import chapter_status, upload, use_llm
from tests.test_pipeline import CountingLLM, _text_pdf


def page_text(prefix: str, n: int = 100, alter_every: int = 0) -> str:
    """n distinct words; with alter_every=25, every 25th word is replaced (~0.8 similarity to the original)."""
    words = [f"{prefix}{i}" for i in range(n)]
    if alter_every:
        words = [f"alt{w}" if (i + 1) % alter_every == 0 else w for i, w in enumerate(words)]
    return " ".join(words)


# ---- fingerprints ---------------------------------------------------------------------

def test_identical_text_scores_one_and_unrelated_scores_near_zero():
    a, b = compute_minhash(page_text("alpha")), compute_minhash(page_text("beta"))
    assert compute_jaccard_similarity(a, compute_minhash(page_text("alpha"))) == 1.0
    assert compute_jaccard_similarity(a, b) < 0.1


def test_word_order_matters_unlike_a_bag_of_words():
    words = page_text("gamma").split()
    assert compute_jaccard_similarity(compute_minhash(" ".join(words)), compute_minhash(" ".join(reversed(words)))) < 0.2


def test_non_ascii_text_is_fingerprinted_not_erased():
    hindi_1 = "भारत एक विशाल देश है जिसकी संस्कृति बहुत प्राचीन और समृद्ध है और यहाँ अनेक भाषाएँ बोली जाती हैं तथा अनेक त्योहार मनाए जाते हैं"
    hindi_2 = "पदार्थ वह है जो स्थान घेरता है और जिसका द्रव्यमान होता है हमारे चारों ओर की हर वस्तु पदार्थ से बनी है जैसे हवा पानी और पत्थर"
    telugu = "భారతదేశం ఒక విశాలమైన దేశం దీని సంస్కృతి చాలా ప్రాచీనమైనది మరియు సంపన్నమైనది ఇక్కడ అనేక భాషలు మాట్లాడతారు మరియు అనేక పండుగలు జరుపుకుంటారు"
    f1, f2, ft = compute_minhash(hindi_1), compute_minhash(hindi_2), compute_minhash(telugu)
    assert f1 and f2 and ft
    assert compute_jaccard_similarity(f1, compute_minhash(hindi_1)) == 1.0
    assert compute_jaccard_similarity(f1, f2) < 0.1 and compute_jaccard_similarity(f1, ft) < 0.1


def test_short_pages_get_no_fingerprint():
    assert compute_minhash("Chapter 3") is None
    assert compute_minhash(page_text("x", 14)) is None
    assert compute_minhash(page_text("x", 15)) is not None
    assert compute_jaccard_similarity(None, compute_minhash(page_text("x"))) == 0.0


def test_similar_pages_share_band_keys_and_unrelated_pages_do_not():
    base = compute_minhash(page_text("delta"))
    variant = compute_minhash(page_text("delta", alter_every=25))
    other = compute_minhash(page_text("omega"))
    assert 0.6 < compute_jaccard_similarity(base, variant) < 0.95
    assert set(band_keys(base)) & set(band_keys(variant))
    assert not set(band_keys(base)) & set(band_keys(other))
    assert set(band_keys(base)) == set(band_keys(compute_minhash(page_text("delta"))))


# ---- the index replaces the full scan --------------------------------------------------------

def make_book_chapter(db, owner=None):
    """A reference book, or a private book owned by `owner` (a student)."""
    book = Book(board="B", class_name="9", subject="S", publisher="P",
                is_reference=owner is None, owner_student_id=owner.id if owner else None)
    db.add(book)
    db.flush()
    ch = Chapter(book_id=book.id, title="C", sequence_num=1)
    db.add(ch)
    db.flush()
    return book, ch


def add_page(db, ch, number, text):
    page = Page(chapter_id=ch.id, page_number=number, content_text=text)
    apply_fingerprint(page, text)
    db.add(page)
    db.flush()
    return page


def test_lookup_only_scores_pages_that_share_a_band_key(session_factory, monkeypatch):
    with session_factory() as db:
        _, ch = make_book_chapter(db)
        for i in range(40):
            add_page(db, ch, i, page_text(f"filler{i}_"))
        target = add_page(db, ch, 99, page_text("delta"))
        calls = []
        real = matching.compute_jaccard_similarity
        monkeypatch.setattr(matching, "compute_jaccard_similarity", lambda a, b: calls.append(1) or real(a, b))

        sig = compute_minhash(page_text("delta", alter_every=25))
        found = matching.find_matches(db, sig, band_keys(sig))
        assert [m.page_id for m in found] == [target.id]
        assert len(calls) <= 3  # the target (and at most a stray collision), not all 41 pages


def test_rebuild_recomputes_fingerprints_and_index(session_factory):
    from app.db.rebuild_fingerprints import rebuild
    with session_factory() as db:
        _, ch = make_book_chapter(db)
        p = Page(chapter_id=ch.id, page_number=1, content_text=page_text("zeta"))
        short = Page(chapter_id=ch.id, page_number=2, content_text="Contents")
        db.add_all([p, short])
        db.flush()
        db.add(PageBand(page_id=p.id, key=12345))  # stale row from an older scheme
        db.commit()
        assert rebuild(db) == 1
        db.expire_all()
        assert p.fingerprint is not None and short.fingerprint is None
        keys = {b.key for b in db.scalars(select(PageBand).where(PageBand.page_id == p.id))}
        assert keys == set(band_keys(p.fingerprint)) and 12345 not in keys
        assert db.scalars(select(PageBand).where(PageBand.page_id == short.id)).all() == []


# ---- Layer 0: identical file anywhere -> no OCR -----------------------------------------------

class CountingOCR(FakeOCRProvider):
    calls = 0

    def extract_layout(self, data, ext):
        CountingOCR.calls += 1
        return super().extract_layout(data, ext)


def test_identical_file_skips_ocr_and_reuses_concepts_without_exposing_the_other_book(client, session_factory, monkeypatch):
    CountingOCR.calls = 0
    monkeypatch.setattr("app.pipeline.orchestrator.get_ocr_provider", lambda: CountingOCR())
    llm = CountingLLM()
    use_llm(monkeypatch, llm)
    pdf = _text_pdf(page_text("epsilon"), page_text("theta"))

    _, ah = make_user(session_factory, Role.student, "studenta")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    assert upload(client, ah, a_book["id"], a_ch, pdf).status_code == 202
    assert CountingOCR.calls == 1
    llm_calls_after_a = llm.calls

    _, bh = make_user(session_factory, Role.student, "studentb")
    b_book = new_book(client, bh)
    b_ch = new_chapter(client, bh, b_book["id"])
    assert upload(client, bh, b_book["id"], b_ch, pdf).status_code == 202
    assert chapter_status(client, bh, b_book["id"], b_ch)["status"] == "ready"
    assert CountingOCR.calls == 1  # second upload never reached OCR
    assert llm.calls == llm_calls_after_a  # ...nor the per-page LLM: its pages matched A's at >= 0.95

    with session_factory() as db:
        report = db.get(Chapter, uuid.UUID(b_ch)).match_report
        assert report["ocr_reused"] is True and report["pages_reused"] == 2
        assert report["suggestions"] == []  # A's private book is invisible to B...
        assert a_book["id"] not in str(report) and str(a_ch) not in str(report)  # ...and never named in B's report
        pages = db.scalars(select(Page).join(Chapter).where(Chapter.id == uuid.UUID(b_ch))).all()
        assert sorted(p.content_text for p in pages) == sorted([page_text("epsilon"), page_text("theta")])


# ---- book-level matches (recorded on the chapter) --------------------------------------------------

def processed_reference_book(session_factory, texts, publisher="NCERT"):
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 9", subject="Science", publisher=publisher, is_reference=True)
        db.add(book)
        db.flush()
        ch = Chapter(book_id=book.id, title="Ref ch", sequence_num=1)
        db.add(ch)
        db.flush()
        PipelineOrchestrator(db, llm_provider=CountingLLM()).process_chapter_file(ch, _text_pdf(*texts), "pdf", None)
        ch.status = ChapterStatus.READY
        db.commit()
        return str(book.id)


def report_of(session_factory, chapter_id) -> dict:
    with session_factory() as db:
        return dict(db.get(Chapter, uuid.UUID(str(chapter_id))).match_report or {})


def suggestions(session_factory, chapter_id) -> list[dict]:
    return report_of(session_factory, chapter_id)["suggestions"]


def test_edition_of_a_reference_book_is_suggested_as_a_variant(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("p1_"), page_text("p2_")])
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh, publisher="School Press")
    ch = new_chapter(client, sh, book["id"])
    upload(client, sh, book["id"], ch, _text_pdf(page_text("p1_", alter_every=25), page_text("p2_", alter_every=25)))

    [s] = suggestions(session_factory, ch)
    assert s["book_id"] == ref_id and s["kind"] == "variant" and s["matched_pages"] == 2 and s["pages_checked"] == 2
    assert 0.6 < s["avg_similarity"] < 0.95 and s["chapter_title"] == "Ref ch"


def test_near_identical_pages_are_reported_as_the_same_book(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("q1_"), page_text("q2_")])
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    ch = new_chapter(client, sh, book["id"])
    upload(client, sh, book["id"], ch, _text_pdf(page_text("q1_"), page_text("q2_")))
    [s] = suggestions(session_factory, ch)
    assert s["book_id"] == ref_id and s["kind"] == "same" and s["avg_similarity"] >= 0.95


def test_unrelated_or_barely_overlapping_uploads_get_no_suggestion(client, session_factory):
    processed_reference_book(session_factory, [page_text("r1_"), page_text("r2_"), page_text("r3_"), page_text("r4_")])
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    ch = new_chapter(client, sh, book["id"])
    upload(client, sh, book["id"], ch, _text_pdf(page_text("r1_", alter_every=25), page_text("n1_"), page_text("n2_"), page_text("n3_")))
    assert suggestions(session_factory, ch) == []  # only 1 of 4 pages matches: coverage 0.25 < 0.5


def test_suggestions_are_judged_chapter_by_chapter(client, session_factory):
    ref_id = processed_reference_book(session_factory, [page_text("s1_"), page_text("s2_"), page_text("s3_"), page_text("s4_")])
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    ch1 = new_chapter(client, sh, book["id"])
    upload(client, sh, book["id"], ch1, _text_pdf(page_text("s1_", alter_every=25), page_text("x1_")))
    [first] = suggestions(session_factory, ch1)
    assert first["book_id"] == ref_id and (first["matched_pages"], first["pages_checked"]) == (1, 2)  # 1 of 2: exactly the 0.5 bar

    ch2 = client.post(f"/student/books/{book['id']}/chapters", json={"title": "C2", "sequence_num": 2}, headers=sh).json()["id"]
    upload(client, sh, book["id"], ch2, _text_pdf(page_text("s2_", alter_every=25), page_text("s3_", alter_every=25)))
    [second] = suggestions(session_factory, ch2)
    assert second["book_id"] == ref_id and (second["matched_pages"], second["pages_checked"]) == (2, 2)
    assert suggestions(session_factory, ch1) == [first]  # the first chapter's report is untouched by the second upload


def test_a_partly_loaded_official_book_is_matched_by_chapter_not_by_page_count(client, session_factory):
    """The official book has only ONE chapter loaded so far, and the student's book has that chapter plus another.
    Each chapter is judged on its own pages: chapter 2 IS the official chapter; chapter 1 simply has no match."""
    ref_id = processed_reference_book(session_factory, [page_text("b1_"), page_text("b2_")])
    _, sh = make_user(session_factory, Role.student, "studenta")
    book = new_book(client, sh)
    c1 = new_chapter(client, sh, book["id"])
    upload(client, sh, book["id"], c1, _text_pdf(*[page_text(f"other{i}_") for i in range(6)]))  # long, unrelated
    c2 = client.post(f"/student/books/{book['id']}/chapters", json={"title": "The Building Block of Life", "sequence_num": 2}, headers=sh).json()["id"]
    upload(client, sh, book["id"], c2, _text_pdf(page_text("b1_"), page_text("b2_")))

    assert suggestions(session_factory, c1) == []
    [m] = suggestions(session_factory, c2)
    assert m["book_id"] == ref_id and m["kind"] == "same" and m["chapter_title"] == "Ref ch"
    assert (m["matched_pages"], m["pages_checked"]) == (2, 2)  # judged within the chapter, not out of 8


def test_other_students_private_books_are_never_suggested(client, session_factory):
    _, ah = make_user(session_factory, Role.student, "studenta")
    _, bh = make_user(session_factory, Role.student, "studentb")
    a_book = new_book(client, ah)
    a_ch = new_chapter(client, ah, a_book["id"])
    upload(client, ah, a_book["id"], a_ch, _text_pdf(page_text("u1_"), page_text("u2_")))

    b_book = new_book(client, bh)
    b_ch = new_chapter(client, bh, b_book["id"])
    upload(client, bh, b_book["id"], b_ch, _text_pdf(page_text("u1_", alter_every=25), page_text("u2_", alter_every=25)))
    assert suggestions(session_factory, b_ch) == []
    assert a_book["id"] not in str(report_of(session_factory, b_ch))

    # ...but the student's OWN other book is a valid base
    b_book2 = new_book(client, bh, subject="Other")
    ch2 = new_chapter(client, bh, b_book2["id"])
    upload(client, bh, b_book2["id"], ch2, _text_pdf(page_text("u1_", alter_every=25), page_text("u2_", alter_every=25)))
    [s] = suggestions(session_factory, ch2)
    assert s["book_id"] == b_book["id"] and s["kind"] == "same"
    assert a_book["id"] not in str(report_of(session_factory, ch2))


def test_an_official_chapter_is_never_matched_to_a_students_private_book(session_factory):
    """Processing a reference chapter records no student's book, even when a student's copy is identical."""
    with session_factory() as db:
        s = Book(board="B", class_name="9", subject="S", publisher="P", is_reference=False,
                 owner_student_id=make_user(session_factory, Role.student, "studenta")[0].id)
        db.add(s)
        db.flush()
        sch = Chapter(book_id=s.id, title="Mine", sequence_num=1)
        db.add(sch)
        db.flush()
        text = _text_pdf(page_text("v1_"), page_text("v2_"))
        PipelineOrchestrator(db, llm_provider=CountingLLM()).process_chapter_file(sch, text, "pdf", s.owner_student_id)
        sch.status = ChapterStatus.READY
        ref = Book(board="CBSE", class_name="Class 9", subject="Science", publisher="NCERT", is_reference=True)
        db.add(ref)
        db.flush()
        rch = Chapter(book_id=ref.id, title="Official", sequence_num=1)
        db.add(rch)
        db.flush()
        PipelineOrchestrator(db, llm_provider=CountingLLM()).process_chapter_file(rch, text, "pdf", None)
        db.commit()
        assert rch.match_report["suggestions"] == []
        assert str(s.id) not in str(rch.match_report)


def _m(book_id, score, reference=True, owner=None):
    return matching.PageMatch(uuid.uuid4(), score, book_id, reference, owner)


def test_summarize_book_matches_rules():
    mine, ref, other_private, own_private = (uuid.uuid4() for _ in range(4))
    student, someone_else = uuid.uuid4(), uuid.uuid4()
    pages = [
        [_m(ref, 0.80), _m(other_private, 0.99, False, someone_else), _m(own_private, 0.70, False, student), _m(mine, 0.99, False, student)],
        [_m(ref, 0.70), _m(ref, 0.65)],  # one page matching a book twice counts once (best score)
        [],
        [_m(other_private, 0.99, False, someone_else)],
    ]
    out = matching.summarize_book_matches(pages, pages_checked=4, own_book_id=mine, student_id=student)
    assert [s["book_id"] for s in out] == [str(ref)]  # ref covers 2/4; own_private only 1/4; the rest filtered
    assert out[0]["matched_pages"] == 2 and out[0]["avg_similarity"] == 0.75 and out[0]["kind"] == "variant"
    assert matching.summarize_book_matches([[_m(ref, 0.97)]], 1, mine, student)[0]["kind"] == "same"
    assert matching.summarize_book_matches([[_m(ref, 0.97)]], 0, mine, student) == []
    assert matching.summarize_book_matches([[_m(ref, 0.97)], [], [], []], 4, mine, student) == []  # coverage 0.25
    # a student's own other book counts; someone else's never does, however well it matches
    assert [s["book_id"] for s in matching.summarize_book_matches([[_m(own_private, 0.99, False, student)]], 1, mine, student)] == [str(own_private)]
    assert matching.summarize_book_matches([[_m(other_private, 0.99, False, someone_else)]], 1, mine, student) == []
