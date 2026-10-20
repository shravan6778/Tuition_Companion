import { useState } from "react";
import { assignTeacherQuiz, deleteTeacherQuiz, generateTeacherQuiz, getTeacherQuiz, listRooms, listTeacherBooks, listTeacherQuizzes } from "../api/learning";
import { Async, Empty, ErrorNote, Pill, fmtDate, useLoad, useSubmit } from "../shared/ui";
import BookChapterSelect from "./BookChapterSelect";

const KEYS = ["A", "B", "C", "D"];
const TYPE = { recall: "Recall", application: "Application", cross_concept: "Connects two ideas" };
const LENGTHS = [["short", "Short · 10 questions"], ["medium", "Medium · 20 questions"], ["long", "Long · 30 questions"]];

// A generated test as the teacher sees it, answer key included.
function QuizViewer({ quizId }) {
  const state = useLoad(() => getTeacherQuiz(quizId), [quizId]);
  return (
    <Async state={state}>
      {(quiz) => (
        <div className="stack mt">
          {quiz.questions.map((q, n) => (
            <div className="q mb0" key={q.id}>
              <div className="q-head">
                <strong>Q{n + 1}</strong>
                <span className="chip">{TYPE[q.question_type] || q.question_type}</span>
                <span className="small">{q.concept_name}{q.related_concept_name ? ` + ${q.related_concept_name}` : ""}</span>
                <span className="small">{q.answer_format === "mcq" ? "Multiple choice" : "Short answer"}</span>
              </div>
              {q.status !== "ready" ? <div className="callout warn">{q.message}</div> : (
                <>
                  <p className="q-text">{q.question}</p>
                  {q.options?.map((o, i) => (
                    <div key={i} className={`opt ${i === q.correct_index ? "right" : ""}`} style={{ cursor: "default" }}>
                      <span className="key">{KEYS[i]}</span><span>{o}{i === q.correct_index ? "  ✓ correct" : ""}</span>
                    </div>
                  ))}
                  {q.expected_answer && <div className="callout ok"><strong>Expected answer:</strong> {q.expected_answer}</div>}
                  {q.explanation && <p className="small mb0 mt">{q.explanation}</p>}
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </Async>
  );
}

function AssignControls({ quiz, rooms, onDone }) {
  const [roomId, setRoomId] = useState("");
  const [due, setDue] = useState("");
  const { busy, error, run } = useSubmit();
  return (
    <form className="row gap-s mt" style={{ justifyContent: "flex-start", alignItems: "flex-end" }}
      onSubmit={(e) => { e.preventDefault(); run(async () => { await assignTeacherQuiz(quiz.id, { room_id: roomId, due_date: due || undefined }); onDone(); }); }}>
      <div>
        <label htmlFor={`as-${quiz.id}`}>Give to a room</label>
        <select id={`as-${quiz.id}`} className="input" value={roomId} required onChange={(e) => setRoomId(e.target.value)}>
          <option value="">Choose a room...</option>
          {rooms.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
        </select>
      </div>
      <div><label htmlFor={`due-${quiz.id}`}>Due (optional)</label><input id={`due-${quiz.id}`} type="date" className="input" value={due} onChange={(e) => setDue(e.target.value)} /></div>
      <button className="btn" disabled={busy}>Assign</button>
      <div style={{ flexBasis: "100%" }}><ErrorNote error={error} /></div>
    </form>
  );
}

// Generate tests, review them with their answer keys, and hand them to a room.
// `target` = { room_id } or { student_id } to give a new test straight to them; empty to generate for later.
export default function QuizPanel({ target = {} }) {
  const data = useLoad(async () => {
    const [books, rooms] = await Promise.all([listTeacherBooks(), listRooms()]);
    return { books, rooms };
  });
  const list = useLoad(() => listTeacherQuizzes());
  const [sel, setSel] = useState({ bookId: "", chapterId: "" });
  const [length, setLength] = useState("short");
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [viewing, setViewing] = useState(null);
  const [assigning, setAssigning] = useState(null);
  const [made, setMade] = useState("");
  const { busy, error, run } = useSubmit();
  const hasTarget = !!(target.room_id || target.student_id);

  const generate = (e) => {
    e.preventDefault();
    setMade("");
    run(async () => {
      const q = await generateTeacherQuiz({
        book_id: sel.bookId, chapter_id: sel.chapterId, length, title: title.trim() || undefined,
        ...(hasTarget ? { ...target, due_date: due || undefined } : {}),
      });
      setMade(hasTarget ? `Created "${q.title}" and gave it to ${target.room_id ? "the room" : "this student"}.` : `Created "${q.title}". Review it below, then give it to a room.`);
      setTitle("");
      setViewing(q.id);
      list.reload();
    });
  };

  return (
    <div className="stack">
      <Async state={data}>
        {({ books, rooms }) => (
          <>
            <form className="card stack mb0" onSubmit={generate}>
              <h3>Generate a test</h3>
              <p className="small mb0">Mixes recall, application and cross-idea questions from the chapter, with page references. Writing takes a little while.</p>
              <div className="grid2">
                <BookChapterSelect books={books} bookId={sel.bookId} chapterId={sel.chapterId} onChange={setSel} idPrefix={`qg-${target.room_id || target.student_id || "all"}`} />
                <div>
                  <label htmlFor="qg-len">Length</label>
                  <select id="qg-len" className="input" value={length} onChange={(e) => setLength(e.target.value)}>
                    {LENGTHS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                  </select>
                </div>
                <div><label htmlFor="qg-title">Title (optional)</label><input id="qg-title" className="input" value={title} maxLength={200} onChange={(e) => setTitle(e.target.value)} /></div>
                {hasTarget && <div><label htmlFor="qg-due">Due (optional)</label><input id="qg-due" type="date" className="input" value={due} onChange={(e) => setDue(e.target.value)} /></div>}
              </div>
              <ErrorNote error={error} />
              {made && <div className="callout ok" role="status">{made}</div>}
              <div className="row">
                <span className="small">{hasTarget ? `Goes to ${target.room_id ? "every student in this room" : "this student"} as soon as it's ready.` : "Not visible to students until you give it to a room."}</span>
                <button className="btn" disabled={busy || !sel.chapterId}>{busy ? "Writing questions..." : "Generate test"}</button>
              </div>
            </form>

            <h3 className="mt">Your tests</h3>
            <Async state={list}>
              {(quizzes) => quizzes.length === 0 ? <div className="card"><Empty>No tests yet.</Empty></div> : (
                <div className="stack">
                  {quizzes.map((q) => (
                    <div className="card mb0" key={q.id}>
                      <div className="row">
                        <div><strong>{q.title}</strong><div className="small">{q.question_count} questions · {fmtDate(q.created_at)}</div></div>
                        <div className="row gap-s">
                          {q.assignment_id ? <Pill kind="ready">Given out</Pill> : <Pill kind="insufficient_data">Not given out</Pill>}
                          <button className="btn secondary small-btn" aria-expanded={viewing === q.id} onClick={() => setViewing(viewing === q.id ? null : q.id)}>{viewing === q.id ? "Hide" : "View with answers"}</button>
                          {!q.assignment_id && <button className="btn small-btn" onClick={() => setAssigning(assigning === q.id ? null : q.id)}>Give to a room</button>}
                          <button className="btn danger small-btn" onClick={() => window.confirm("Delete this test?") && run(async () => { await deleteTeacherQuiz(q.id); list.reload(); })}>Delete</button>
                        </div>
                      </div>
                      {assigning === q.id && <AssignControls quiz={q} rooms={rooms} onDone={() => { setAssigning(null); list.reload(); }} />}
                      {viewing === q.id && <QuizViewer quizId={q.id} />}
                    </div>
                  ))}
                </div>
              )}
            </Async>
          </>
        )}
      </Async>
    </div>
  );
}
