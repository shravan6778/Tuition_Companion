import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  getTodaysWork,
  listChecks,
  listMyQuizzes,
  myDoubts,
  startCheck,
} from "../api/learning";
import Header from "../shared/Header";
import {
  Async,
  Empty,
  ErrorNote,
  Pill,
  fmtDate,
  isOverdue,
  pct,
  useLoad,
  useSubmit,
} from "../shared/ui";
import DoubtBox from "./DoubtBox";

const LEVEL = {
  subject: "Whole subject",
  chapter: "Chapter",
  concept: "Concepts",
  exercise: "Exercise",
};

function DoubtHistory({ assignmentId, refreshKey }) {
  const state = useLoad(
    () => myDoubts(assignmentId),
    [assignmentId, refreshKey],
  );
  if (!state.data?.length) return null;
  return (
    <div>
      <h3>Doubts you asked on this</h3>
      <div className="items">
        {state.data.map((d) => (
          <div className="item" key={d.id}>
            <strong>{d.text}</strong>
            {d.answer && (
              <div className="callout info mt">
                <strong>Saved answer</strong>
                <p className="pre mb0">{d.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function AssignmentCard({ a, checks, onChanged }) {
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const [asked, setAsked] = useState(0);
  const { busy, error, run } = useSubmit();
  const mine = checks.filter((c) => c.assignment_id === a.id);
  const openCheck = mine.find((c) => c.status === "open");
  const lastDone = mine.find((c) => c.status === "submitted");

  const begin = () =>
    run(async () => {
      const check = await startCheck(a.id);
      onChanged();
      nav(`/student/checks/${check.id}`);
    });

  return (
    <div className="card">
      <div className="row" style={{ alignItems: "flex-start" }}>
        <div>
          <h3 className="mb0">{a.title}</h3>
          <div className="chips mt">
            <span className="chip">{LEVEL[a.level] || a.level}</span>
            {a.chapter_title && <span className="chip">{a.chapter_title}</span>}
            <span className="chip">
              {a.concept_count} {a.concept_count === 1 ? "idea" : "ideas"}
            </span>
          </div>
        </div>
        <div className="row gap-s">
          {a.due_date &&
            (isOverdue(a.due_date) && !lastDone ? (
              <Pill kind="weak">Was due {fmtDate(a.due_date)}</Pill>
            ) : (
              <span className="small">Due {fmtDate(a.due_date)}</span>
            ))}
          {lastDone && (
            <Pill kind="submitted">Checked · {pct(lastDone.score)}</Pill>
          )}
        </div>
      </div>

      <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
        {openCheck ? (
          <Link className="btn" to={`/student/checks/${openCheck.id}`}>
            Continue check
          </Link>
        ) : (
          <button className="btn" onClick={begin} disabled={busy}>
            {busy
              ? "Preparing your check..."
              : lastDone
                ? "Take another check"
                : "Mark complete"}
          </button>
        )}
        {lastDone && (
          <Link className="btn secondary" to={`/student/checks/${lastDone.id}`}>
            See result
          </Link>
        )}
        <button
          className="btn ghost"
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          {open ? "Hide doubt box" : "Doubt"}
        </button>
      </div>
      <ErrorNote error={error} />
      {!openCheck && !lastDone && (
        <p className="small mb0 mt">
          Marking this complete gives you a short check on the ideas in it.
        </p>
      )}

      {open && (
        <div className="stack mt">
          <DoubtBox
            assignmentId={a.id}
            onAsked={() => setAsked((n) => n + 1)}
          />
          <DoubtHistory assignmentId={a.id} refreshKey={asked} />
        </div>
      )}
    </div>
  );
}

export default function TodayWork() {
  const state = useLoad(async () => {
    const [work, checks, quizzes] = await Promise.all([
      getTodaysWork(),
      listChecks(),
      listMyQuizzes(),
    ]);
    return { work, checks, tests: quizzes.filter((q) => q.kind === "teacher") };
  });

  return (
    <>
      <Header
        title="Today's Work"
        subtitle="What your teacher has set, soonest due first."
      />
      <div className="container">
        <Async state={state}>
          {({ work, checks, tests }) => (
            <>
              {work.length === 0 ? (
                <div className="card">
                  <Empty>
                    <p>
                      <strong>Nothing assigned yet.</strong>
                    </p>
                    <p className="mb0">
                      Link your textbooks and join your teacher's room in{" "}
                      <Link to="/student/books">My Books</Link>, or try a{" "}
                      <Link to="/student/practice">practice test</Link>.
                    </p>
                  </Empty>
                </div>
              ) : (
                work.map((a) => (
                  <AssignmentCard
                    key={a.id}
                    a={a}
                    checks={checks}
                    onChanged={state.reload}
                  />
                ))
              )}

              {tests.length > 0 && (
                <>
                  <h2 className="mt">Tests from your teacher</h2>
                  <div className="card items">
                    {tests.map((t) => (
                      <div className="item row" key={t.id}>
                        <div>
                          <strong>{t.title}</strong>
                          <div className="small">
                            {t.question_count} questions
                          </div>
                        </div>
                        <div className="row gap-s">
                          {t.status === "submitted" ? (
                            <Pill kind="submitted">Done · {pct(t.score)}</Pill>
                          ) : (
                            <Pill kind="open" />
                          )}
                          <Link
                            className={`btn small-btn${t.status === "submitted" ? " secondary" : ""}`}
                            to={`/student/quizzes/${t.id}`}
                          >
                            {t.status === "submitted" ? "Review" : "Start test"}
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </Async>
      </div>
    </>
  );
}
