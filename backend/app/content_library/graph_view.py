from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Chapter, Concept, ConceptEdge, Page
from app.schemas import ChapterGraphOut, GraphEdgeOut, GraphNodeOut


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
    return ChapterGraphOut(
        chapter_id=chapter.id,
        status=chapter.status,
        nodes=nodes,
        edges=[GraphEdgeOut(prerequisite_id=e.prerequisite_id, concept_id=e.concept_id, source=e.source) for e in edges],
        report=chapter.graph_report,
    )
