import { Link, useParams } from "react-router-dom";
import { getChapterPages, getMyBook, getStudentChapterGraph } from "../api/learning";
import Header from "../shared/Header";
import { Async, useLoad } from "../shared/ui";
import DoubtBox from "./DoubtBox";

// Read a chapter page by page, see how its ideas depend on each other, and ask a doubt inside just this chapter.
export default function ChapterReader() {
  const { bookId, chapterId } = useParams();
  const state = useLoad(async () => {
    const [book, pages, graph] = await Promise.all([getMyBook(bookId), getChapterPages(bookId, chapterId), getStudentChapterGraph(bookId, chapterId)]);
    return { book, pages, graph };
  }, [bookId, chapterId]);

  return (
    <>
      <Async state={state}>
        {({ book, pages, graph }) => {
          const chapter = book.chapters.find((c) => c.id === chapterId);
          const name = Object.fromEntries(graph.nodes.map((n) => [n.id, n.name]));
          const needs = (id) => graph.edges.filter((e) => e.concept_id === id).map((e) => name[e.prerequisite_id]).filter(Boolean);
          return (
            <>
              <Header title={chapter ? `Ch ${chapter.sequence_num}: ${chapter.title}` : "Chapter"} subtitle={`${book.class_name} ${book.subject}`} />
              <div className="container">
                <Link to="/student/books" className="back-link">← My Books</Link>

                {graph.nodes.length > 0 && (
                  <div className="card">
                    <h2>Ideas in this chapter</h2>
                    <div className="items">
                      {graph.nodes.map((n) => (
                        <div className="item" key={n.id}>
                          <strong>{n.name}</strong> <span className="small">page{n.pages.length > 1 ? "s" : ""} {n.pages.join(", ")}</span>
                          {n.description && <div className="small">{n.description}</div>}
                          {needs(n.id).length > 0 && <div className="small">Builds on: {needs(n.id).join(", ")}</div>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="card">
                  <h2>Stuck on something here?</h2>
                  <DoubtBox chapterId={chapterId} />
                </div>

                <h2>Pages</h2>
                {pages.map((p) => (
                  <article className="card" key={p.id} id={`page-${p.page_number}`}>
                    <div className="small">Page {p.page_number}</div>
                    <p className="pre mb0">{p.content_text}</p>
                  </article>
                ))}
              </div>
            </>
          );
        }}
      </Async>
    </>
  );
}
