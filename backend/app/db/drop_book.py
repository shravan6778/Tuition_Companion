"""Remove a whole OFFICIAL book (for example an empty duplicate left behind by an ingest with a different --edition).

    python -m app.db.drop_book --book <book-id>          # dry run: shows what would go
    python -m app.db.drop_book --book <book-id> --yes    # really delete it

Deletes the book with all its chapters, pages, concepts, edges and embeddings, and its copy in the graph store.
Official books only; teachers' books are deleted by their owners in the app."""
import argparse
import uuid

from sqlalchemy import func, select

from app.content_library import deletion
from app.db.session import SessionLocal
from app.models import Book, Concept, Page, Chapter


def run(db_factory, book_id: uuid.UUID, confirm: bool) -> list[str]:
    with db_factory() as db:
        book = db.get(Book, book_id)
        if book is None:
            return ["Book not found."]
        if not book.is_reference:
            return ["Refused: this is not an official book. Teachers delete their own books in the app."]
        chapters = db.scalar(select(func.count()).select_from(Chapter).where(Chapter.book_id == book.id))
        pages = db.scalar(select(func.count()).select_from(Page).join(Chapter, Chapter.id == Page.chapter_id).where(Chapter.book_id == book.id))
        concepts = db.scalar(select(func.count()).select_from(Concept).join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id).where(Chapter.book_id == book.id))
        line = f"{book.publisher} {book.class_name} {book.subject} (edition {book.edition or '-'}): {chapters} chapters, {pages} pages, {concepts} concepts"
        if not confirm:
            return [f"would delete {line}", "dry run, nothing deleted (add --yes)"]
        deletion.delete_book(db, book)
        return [f"deleted {line}"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--book", required=True)
    parser.add_argument("--yes", action="store_true")
    a = parser.parse_args()
    print("\n".join(run(SessionLocal, uuid.UUID(a.book), a.yes)))
