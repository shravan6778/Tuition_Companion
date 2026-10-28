import { useState } from "react";
import { browseForDoubts, myDoubts } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, Pill, fmtDateTime, useLoad } from "../shared/ui";
import DoubtBox from "./DoubtBox";
import { Link } from "react-router-dom";

const STATUS = {
  grounded: "ready",
  outside_assignment: "processing",
  not_in_book: "failed",
  unavailable: "failed",
};
const STATUS_TEXT = {
  grounded: "Found in book",
  outside_assignment: "Outside the task",
  not_in_book: "Not in book yet",
  unavailable: "Couldn't look up",
};

function History({ refreshKey }) {
  const state = useLoad(() => myDoubts(), [refreshKey]);
  return (
    <Async state={state}>
      {(list) =>
        list.length === 0 ? null : (
          <>
            <h2 className="mt">Your recent doubts</h2>
            <div className="card items">
              {list.slice(0, 15).map((d) => (
                <div className="item" key={d.id}>
                  <div className="row">
                    <div>
                      <strong>{d.text}</strong>
                      <div className="small">
                        {fmtDateTime(d.created_at)}
                        {d.assignment_id ? " · on a task" : ""}
                      </div>
                    </div>
                    <Pill kind={STATUS[d.status]}>
                      {STATUS_TEXT[d.status] || d.status}
                    </Pill>
                  </div>
                  {d.answer && (
                    <div className="callout info mt">
                      <strong>Saved answer</strong>
                      <p className="pre mb0">{d.answer}</p>
                      {d.refresher && (
                        <p className="small pre mb0 mt">
                          Quick refresher: {d.refresher}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )
      }
    </Async>
  );
}

// Doubts beyond today's tasks: pick a subject, book and chapter to narrow the search, or search all linked books.
export default function AskDoubt() {
  const state = useLoad(browseForDoubts);
  const [subject, setSubject] = useState("");
  const [bookId, setBookId] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [asked, setAsked] = useState(0);

  return (
    <>
      <Header
        title="Ask a Doubt"
        subtitle="Anything from your linked books, not only today's work."
      />
      <div className="container">
        <Async state={state}>
          {(subjects) => {
            if (subjects.length === 0) {
              return (
                <div className="card">
                  <Empty>
                    <p>
                      <strong>No chapters to search yet.</strong>
                    </p>
                    <p className="mb0">
                      Link a textbook in{" "}
                      <Link to="/student/books">My Books</Link>. Only chapters
                      your teacher has finished adding show up here.
                    </p>
                  </Empty>
                </div>
              );
            }
            const subj = subjects.find((s) => s.subject === subject);
            const book = subj?.books.find((b) => b.id === bookId);
            return (
              <>
                <div className="card stack">
                  <h3>Where should we look?</h3>
                  <div className="grid2">
                    <div>
                      <label htmlFor="d-subj">Subject</label>
                      <select
                        id="d-subj"
                        className="input"
                        value={subject}
                        onChange={(e) => {
                          setSubject(e.target.value);
                          setBookId("");
                          setChapterId("");
                        }}
                      >
                        <option value="">All my subjects</option>
                        {subjects.map((s) => (
                          <option key={s.subject} value={s.subject}>
                            {s.subject}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="d-book">Book</label>
                      <select
                        id="d-book"
                        className="input"
                        value={bookId}
                        disabled={!subj}
                        onChange={(e) => {
                          setBookId(e.target.value);
                          setChapterId("");
                        }}
                      >
                        <option value="">All books</option>
                        {subj?.books.map((b) => (
                          <option key={b.id} value={b.id}>
                            {b.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="d-ch">Chapter</label>
                      <select
                        id="d-ch"
                        className="input"
                        value={chapterId}
                        disabled={!book}
                        onChange={(e) => setChapterId(e.target.value)}
                      >
                        <option value="">Whole book</option>
                        {book?.chapters.map((c) => (
                          <option key={c.id} value={c.id}>
                            Ch {c.number}: {c.title}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <p className="small mb0">
                    {chapterId
                      ? "Searching this chapter only."
                      : bookId
                        ? "Searching this whole book."
                        : subject
                          ? `Searching all your ${subject} books.`
                          : "Searching all your linked books."}
                  </p>
                </div>
                <div className="card">
                  <DoubtBox
                    key={chapterId}
                    chapterId={chapterId || undefined}
                    onAsked={() => setAsked((n) => n + 1)}
                  />
                </div>
                <History refreshKey={asked} />
              </>
            );
          }}
        </Async>
      </div>
    </>
  );
}
