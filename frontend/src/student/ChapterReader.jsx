import { Link, useParams } from "react-router-dom";
import { useState } from "react";
import {
  getChapterPages,
  getMyBook,
  getStudentChapterGraph,
} from "../api/learning";
import Header from "../shared/Header";
import { Async, useLoad } from "../shared/ui";
import DoubtBox from "./DoubtBox";

// Read a chapter page by page, see how its ideas depend on each other, and ask a doubt inside just this chapter.
export default function ChapterReader() {
  const { bookId, chapterId } = useParams();
  const [tab, setTab] = useState("concepts");
  const state = useLoad(async () => {
    const [book, pages, graph] = await Promise.all([
      getMyBook(bookId),
      getChapterPages(bookId, chapterId),
      getStudentChapterGraph(bookId, chapterId),
    ]);
    return { book, pages, graph };
  }, [bookId, chapterId]);

  return (
    <>
      <Async state={state}>
        {({ book, pages, graph }) => {
          const chapter = book.chapters.find((c) => c.id === chapterId);
          const nameMap = Object.fromEntries(
            graph.nodes.map((n) => [n.id, n.name]),
          );
          const needs = (id) =>
            graph.edges
              .filter((e) => e.concept_id === id)
              .map((e) => nameMap[e.prerequisite_id])
              .filter(Boolean);

          const allItems = pages.flatMap((p) =>
            (p.items || []).map((i) => ({ ...i, page_number: p.page_number })),
          );
          const examples = allItems.filter((i) => i.kind === "example");
          const exercises = allItems.filter(
            (i) => i.kind === "exercise_question",
          );
          const figures = allItems.filter((i) => i.kind === "diagram");
          const activities = allItems.filter(
            (i) => i.kind === "activity" || i.kind === "sidebar",
          );

          const tabs = [
            ["concepts", `Concepts (${graph.nodes.length})`],
            ["examples", `Examples (${examples.length})`],
            ["exercises", `Exercises (${exercises.length})`],
            ["figures", `Figures (${figures.length})`],
            ["activities", `Activities (${activities.length})`],
          ];

          const shown =
            tab === "concepts"
              ? graph.nodes
              : tab === "examples"
                ? examples
                : tab === "exercises"
                  ? exercises
                  : tab === "figures"
                    ? figures
                    : activities;

          return (
            <>
              <Header
                title={
                  chapter
                    ? `Ch ${chapter.sequence_num}: ${chapter.title}`
                    : "Chapter"
                }
                subtitle={`${book.class_name} ${book.subject}`}
              />
              <div className="container">
                <Link to="/student/books" className="back-link">
                  ← My Books
                </Link>

                {/* ── Tabbed content card ── */}
                <div className="card">
                  <h2>Chapter content</h2>

                  <div className="tabs" role="tablist">
                    {tabs.map(([id, label]) => (
                      <button
                        key={id}
                        role="tab"
                        className={`tab ${tab === id ? "active" : ""}`}
                        aria-selected={tab === id}
                        onClick={() => setTab(id)}
                      >
                        {label}
                      </button>
                    ))}
                  </div>

                  <div className="items">
                    {shown.length === 0 && (
                      <div className="small">
                        Nothing extracted for this tab yet.
                      </div>
                    )}

                    {tab === "concepts" &&
                      graph.nodes.map((n) => (
                        <div className="item" key={n.id}>
                          <strong>{n.name}</strong>{" "}
                          <span className="small">
                            page{n.pages.length > 1 ? "s" : ""}{" "}
                            {n.pages.join(", ")}
                          </span>
                          {n.description && (
                            <div className="small">{n.description}</div>
                          )}
                          {needs(n.id).length > 0 && (
                            <div className="small">
                              Builds on: {needs(n.id).join(", ")}
                            </div>
                          )}
                        </div>
                      ))}

                    {tab !== "concepts" &&
                      shown.map((item) => (
                        <div className="item" key={item.id}>
                          <strong>{item.label || item.kind}</strong>{" "}
                          <span className="small">page {item.page_number}</span>
                          {item.text && (
                            <div className="pre small">{item.text}</div>
                          )}
                          {item.solution_text && (
                            <div className="small">
                              <b>Solution:</b> {item.solution_text}
                            </div>
                          )}
                        </div>
                      ))}
                  </div>
                </div>

                {/* ── Doubt box ── */}
                <div className="card">
                  <h2>Stuck on something here?</h2>
                  <DoubtBox chapterId={chapterId} />
                </div>

                {/* ── Raw page text ── */}
                <h2>Pages</h2>
                {pages.map((p) => (
                  <article
                    className="card"
                    key={p.id}
                    id={`page-${p.page_number}`}
                  >
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
