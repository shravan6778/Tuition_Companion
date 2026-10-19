import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { generatePractice, listMyQuizzes } from "../api/learning";
import { fetchMyLinkedBooks } from "../api/content";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, Pill, bookLabel, fmtDate, pct, useLoad, useSubmit } from "../shared/ui";

function PastQuizzes({ list }) {
  const mine = list.filter((q) => q.kind === "practice");
  if (mine.length === 0) return null;
  return (
    <>
      <h2 className="mt">Your practice tests</h2>
      <div className="card items">
        {mine.map((q) => (
          <div className="item row" key={q.id}>
            <div><strong>{q.title}</strong><div className="small">{fmtDate(q.created_at)} · {q.question_count} questions</div></div>
            <div className="row gap-s">
              {q.status === "submitted" ? <Pill kind="submitted">Done · {pct(q.score)}</Pill> : <Pill kind="open" />}
              <Link className="btn secondary small-btn" to={`/student/quizzes/${q.id}`}>{q.status === "submitted" ? "Review" : "Continue"}</Link>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

// Self-triggered practice. The server aims most questions at the concepts this student is weakest on.
export default function Practice() {
  const nav = useNavigate();
  const state = useLoad(async () => {
    const [books, quizzes] = await Promise.all([fetchMyLinkedBooks(), listMyQuizzes()]);
    return { books: books || [], quizzes };
  });
  const [bookId, setBookId] = useState("");
  const [chapterId, setChapterId] = useState("");
  const [count, setCount] = useState(10);
  const { busy, error, run } = useSubmit();

  const start = (e) => {
    e.preventDefault();
    run(async () => {
      const quiz = await generatePractice({ book_id: bookId || undefined, chapter_id: chapterId || undefined, question_count: Number(count) });
      nav(`/student/quizzes/${quiz.id}`);
    });
  };

  return (
    <>
      <Header title="Practice Test" subtitle="A quiz built around the ideas you find hardest." />
      <div className="container">
        <Async state={state}>
          {({ books, quizzes }) => {
            const book = books.find((b) => b.id === bookId);
            if (books.length === 0) {
              return <div className="card"><Empty><p><strong>Link a textbook first.</strong></p><p className="mb0">Practice tests are made from your books. Add one in <Link to="/student/books">My Books</Link>.</p></Empty></div>;
            }
            return (
              <>
                <form className="card stack" onSubmit={start}>
                  <div className="callout info">
                    About 60% of the questions target ideas you've scored below 60% on, 20% target ideas flagged as at risk, and the rest revise other topics. Short answers are marked by the tutor, so allow a few seconds.
                  </div>
                  <div className="grid2">
                    <div>
                      <label htmlFor="p-book">Book</label>
                      <select id="p-book" className="input" value={bookId} onChange={(e) => { setBookId(e.target.value); setChapterId(""); }}>
                        <option value="">All my linked books</option>
                        {books.map((b) => <option key={b.id} value={b.id}>{bookLabel(b)}</option>)}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="p-ch">Chapter</label>
                      <select id="p-ch" className="input" value={chapterId} disabled={!book} onChange={(e) => setChapterId(e.target.value)}>
                        <option value="">Whole book</option>
                        {book?.chapters.map((c) => <option key={c.id} value={c.id}>Ch {c.sequence_num}: {c.title}</option>)}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="p-n">Questions</label>
                      <select id="p-n" className="input" value={count} onChange={(e) => setCount(e.target.value)}>
                        {[5, 10, 15, 20].map((n) => <option key={n} value={n}>{n}</option>)}
                      </select>
                    </div>
                  </div>
                  <ErrorNote error={error} />
                  <div><button className="btn" disabled={busy}>{busy ? "Writing your questions..." : "Start practice test"}</button></div>
                </form>
                <PastQuizzes list={quizzes} />
              </>
            );
          }}
        </Async>
      </div>
    </>
  );
}
