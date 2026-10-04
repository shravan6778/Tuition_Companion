"""Build concept graphs for chapters that were processed before the graph existed.

    python -m app.db.relink_chapters            # real LLM per your .env (one call per chapter)

Re-uses the concepts already stored (no OCR, no per-page LLM calls)."""
from sqlalchemy import select

from app.db.session import SessionLocal
from app.llm import get_llm_provider
from app.models.content import Chapter, ChapterStatus
from app.pipeline.graph import build_chapter_graph


def main() -> None:
    llm = get_llm_provider()
    with SessionLocal() as db:
        chapters = db.scalars(
            select(Chapter).where(Chapter.status == ChapterStatus.READY, Chapter.graph_report.is_(None))
        ).all()
        for chapter in chapters:
            try:
                report = build_chapter_graph(db, chapter, llm)
                db.commit()
                print(f"{chapter.title!r}: {report['concepts']} concepts, {report['edges']} edges")
            except Exception as exc:  # keep going; one bad chapter shouldn't block the rest
                db.rollback()
                print(f"{chapter.title!r}: FAILED ({exc})")
        print(f"Done. {len(chapters)} chapter(s) checked.")


if __name__ == "__main__":
    main()
