from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Chapter, ChapterStatus, Concept, ConceptEdge, CrossChapterEdge, Page
from app.schemas import ChapterGraphOut, CrossChapterEdgeOut, GraphEdgeOut, GraphNodeOut


def chapter_graph(db: Session, chapter: Chapter) -> ChapterGraphOut:
    """The chapter's deduplicated concept graph: one node per distinct concept, edges prerequisite -> concept."""
    rows = db.execute(
        select(Concept, Page.page_number)
        .join(Page, Page.id == Concept.page_id)
        .where(Page.chapter_id == chapter.id)
        .order_by(Page.page_number, Concept.position)
    ).all()
    pages_by_key: dict[str, set[int]] = defaultdict(set)
    for concept, page_number in rows:
        pages_by_key[concept.name_key].add(page_number)

    nodes = [
        GraphNodeOut(id=c.id, name=c.name, description=c.description, pages=sorted(pages_by_key[c.name_key]))
        for c, _ in rows if c.is_canonical
    ]
    edges = db.scalars(select(ConceptEdge).where(ConceptEdge.chapter_id == chapter.id)).all()
    cross = db.execute(
        select(CrossChapterEdge, Concept, Chapter)
        .join(Concept, Concept.id == CrossChapterEdge.prerequisite_id)
        .join(Page, Page.id == Concept.page_id).join(Chapter, Chapter.id == Page.chapter_id)
        .where(CrossChapterEdge.chapter_id == chapter.id, Chapter.status == ChapterStatus.READY)  # same book by construction
        .order_by(Chapter.sequence_num, Concept.name)
    ).all()
    return ChapterGraphOut(
        chapter_id=chapter.id,
        cross_chapter=[
            CrossChapterEdgeOut(
                concept_id=e.concept_id, prerequisite_id=e.prerequisite_id, prerequisite_name=c.name,
                prerequisite_chapter_id=ch.id, prerequisite_chapter_title=ch.title, similarity=e.similarity,
            ) for e, c, ch in cross
        ],
        status=chapter.status,
        nodes=nodes,
        edges=[GraphEdgeOut(prerequisite_id=e.prerequisite_id, concept_id=e.concept_id, source=e.source) for e in edges],
        report=chapter.graph_report,
    )
