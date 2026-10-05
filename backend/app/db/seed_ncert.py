"""
Pre-seed free official textbooks (NCERT Class 9 & 10 Science/Math)
into the reference corpus.
Run: python -m app.db.seed_ncert
"""
from app.db.session import SessionLocal
from app.models.content import Book, Chapter, ChapterStatus, Page, Concept
from app.pipeline.graph import build_chapter_graph
from app.pipeline.fingerprint import apply_fingerprint


class _NoLinksLLM:
    """The seeded concepts already name their prerequisites, so no model call is needed to link them."""

    def complete_json(self, system: str, user: str) -> str:
        return '{"edges": []}'


def seed_ncert_corpus():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Book).filter(Book.is_reference.is_(True), Book.publisher == "NCERT").first()
        if existing:
            print("NCERT reference corpus is already seeded.")
            return

        print("Seeding NCERT Reference Books...")

        # 1. Class 9 Science
        book_c9_sci = Book(
            board="CBSE",
            class_name="Class 9",
            subject="Science",
            publisher="NCERT",
            edition="2026",
            is_customized=False,
            is_reference=True,
        )
        db.add(book_c9_sci)
        db.flush()

        ch1 = Chapter(
            book_id=book_c9_sci.id,
            title="Matter in Our Surroundings",
            sequence_num=1,
        )
        db.add(ch1)
        db.flush()

        sample_p1_text = (
            "Matter in Our Surroundings: Everything in this universe is made up of material "
            "which scientists have named 'matter'. The air we breathe, the food we eat, stones, "
            "clouds, stars, plants and animals, even a small drop of water or a particle of sand "
            "— everything is matter. Physical Nature of Matter: Matter is made up of particles."
        )

        page1 = Page(
            chapter_id=ch1.id,
            page_number=1,
            content_text=sample_p1_text,
        )
        apply_fingerprint(page1, sample_p1_text)
        db.add(page1)
        db.flush()

        c1 = Concept(
            page_id=page1.id,
            name="Definition of Matter",
            description="Anything that occupies space and has mass is defined as matter.",
            learning_objectives=["Understand what constitutes matter", "Identify examples of physical matter"],
            prerequisites=[],
        )
        c2 = Concept(
            page_id=page1.id,
            name="Particulate Nature of Matter",
            description="Matter is not continuous; it is composed of tiny discrete particles.",
            learning_objectives=["Describe evidence for particulate nature of matter"],
            prerequisites=["Definition of Matter"],
        )
        db.add_all([c1, c2])
        db.flush()

        ch1.status = ChapterStatus.READY  # visible to students; pages + concepts are already in place
        build_chapter_graph(db, ch1, _NoLinksLLM())

        db.commit()
        print("NCERT Reference Corpus successfully seeded!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding NCERT corpus: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_ncert_corpus()