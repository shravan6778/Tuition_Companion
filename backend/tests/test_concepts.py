import uuid
import pytest
from sqlalchemy import select
from app.models.content import Book, Chapter, Page, Concept

def test_page_concept_hierarchy_and_prerequisites(session_factory):
    """Validate Phase 2 hierarchy: Book -> Chapter -> Page -> Concept"""
    with session_factory() as db:
        book = Book(board="CBSE", class_name="Class 10", subject="Science", publisher="NCERT", is_reference=True)
        db.add(book)
        db.flush()

        chapter = Chapter(book_id=book.id, title="Chemical Reactions", sequence_num=1)
        db.add(chapter)
        db.flush()

        page = Page(chapter_id=chapter.id, page_number=1, content_text="Equations.", verified=True)
        db.add(page)
        db.flush()

        c1 = Concept(page_id=page.id, name="Chemical Equation", prerequisites=["Changes"])
        c2 = Concept(page_id=page.id, name="Law of Mass", prerequisites=["Chemical Equation"])
        db.add_all([c1, c2])
        db.commit()

        saved_page = db.scalar(select(Page).where(Page.id == page.id))
        assert saved_page is not None
        assert len(saved_page.concepts) == 2
        concept_names = [c.name for c in saved_page.concepts]
        assert "Chemical Equation" in concept_names


def test_concepts_cascade_delete_with_page(session_factory):
    """Deleting a page should cascade and delete its associated concepts."""
    with session_factory() as db:
        book = Book(board="ICSE", class_name="Class 9", subject="Math", publisher="Selina", is_reference=True)
        db.add(book)
        db.flush()

        chapter = Chapter(book_id=book.id, title="Algebra", sequence_num=1)
        db.add(chapter)
        db.flush()

        page = Page(chapter_id=chapter.id, page_number=5, content_text="Equations", verified=True)
        db.add(page)
        db.flush()

        concept = Concept(page_id=page.id, name="Linear Equation")
        db.add(concept)
        db.commit()

        concept_id = concept.id

        # Delete page
        db.delete(page)
        db.commit()

        # Verify concept was deleted via cascade
        deleted_concept = db.scalar(select(Concept).where(Concept.id == concept_id))
        assert deleted_concept is None