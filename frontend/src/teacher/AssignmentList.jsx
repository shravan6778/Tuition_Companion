import { useState } from "react";
import { assignmentChecks, assignmentDoubts, deleteAssignment, listAssignments } from "../api/learning";
import { Async, Empty, ErrorNote, Pill, fmtDate, fmtDateTime, isOverdue, useLoad, useSubmit } from "../shared/ui";
import AnswerReview from "./AnswerReview";
import SubmissionReview from "./SubmissionReview";

const LEVEL = { subject: "Whole book", chapter: "Chapter", concept: "Ideas", exercise: "Exercise", items: "Picked items", manual: "Homework" };

// The per-task Doubt button: every doubt students raised on this one assignment.
function Doubts({ assignmentId, studentId }) {
  const state = useLoad(() => assignmentDoubts(assignmentId, studentId), [assignmentId, studentId]);
  return (
    <div className="mt">
      <Async state={state}>
        {(list) => list.length === 0 ? <p className="small mb0">No doubts raised on this task yet.</p> : (
          <div className="items">
            {list.map((d) => (
              <div className="item" key={d.id}>
                <div className="row"><strong>{d.student_name}</strong><span className="small">{fmtDateTime(d.created_at)}</span></div>
                <p className="mb0">{d.text}</p>
                <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
                  <Pill kind={d.status === "grounded" ? "ready" : d.status === "not_in_book" ? "failed" : "processing"}>
                    {d.status === "grounded" ? "Found in book" : d.status === "not_in_book" ? "Not in book" : d.status === "outside_assignment" ? "Outside the task" : "Couldn't look up"}
                  </Pill>
                  {d.needs_review && <Pill kind="at_risk">Low confidence</Pill>}
                </div>
                {d.answer && <details className="mt"><summary>Explanation the student saw</summary><p className="pre small">{d.answer}</p></details>}
              </div>
            ))}
          </div>
        )}
      </Async>
    </div>
  );
}

// Assignments for one room, or one student (their own plus their rooms').
export default function AssignmentList({ roomId, studentId, refreshKey = 0 }) {
  const state = useLoad(() => listAssignments(roomId ? { room_id: roomId } : { student_id: studentId }), [roomId, studentId, refreshKey]);
  const [open, setOpen] = useState(null);
  const [checksOpen, setChecksOpen] = useState(null);
  const { error, run } = useSubmit();

  return (
    <Async state={state}>
      {(list) => list.length === 0 ? (
        <div className="card"><Empty>No work set yet. Use the form above to assign the first piece.</Empty></div>
      ) : (
        <div className="stack">
          <ErrorNote error={error} />
          {list.map((a) => (
            <div className="card mb0" key={a.id}>
              <div className="row" style={{ alignItems: "flex-start" }}>
                <div>
                  <h3 className="mb0">{a.title}</h3>
                  <div className="chips mt">
                    <span className="chip">{LEVEL[a.level] || a.level}</span>
                    {a.level === "manual" && <span className="chip">{a.subject}</span>}
                    {a.chapter_title && <span className="chip">{a.chapter_title}</span>}
                    {a.level !== "manual" && <span className="chip">{a.concept_count} {a.concept_count === 1 ? "idea" : "ideas"}</span>}
                    {a.level === "manual" && a.pending_review > 0 && <Pill kind="sent">{a.pending_review} to review</Pill>}
                    {studentId && <span className="chip">{a.student_id ? "Just this student" : "Whole room"}</span>}
                  </div>
                </div>
                <div className="small">
                  {a.due_date ? (isOverdue(a.due_date) ? <Pill kind="weak">Was due {fmtDate(a.due_date)}</Pill> : `Due ${fmtDate(a.due_date)}`) : `Set ${fmtDate(a.created_at)}`}
                </div>
              </div>
              {a.description && <p className="pre small mt mb0">{a.description}</p>}
              <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
                {/* a homework task has no book behind it, so it has no Doubt button: its work is reviewed instead */}
                <button className="btn secondary small-btn" aria-expanded={open === a.id} onClick={() => setOpen(open === a.id ? null : a.id)}>
                  {a.level === "manual" ? "Review work" : "Doubt"}
                </button>
                {a.level !== "manual" && (
                  <button className="btn secondary small-btn" aria-expanded={checksOpen === a.id} onClick={() => setChecksOpen(checksOpen === a.id ? null : a.id)}>Check answers</button>
                )}
                <button className="btn danger small-btn"
                  onClick={() => window.confirm("Delete this assignment? Students keep their own doubt and check history.") && run(async () => { await deleteAssignment(a.id); state.reload(); })}>
                  Delete
                </button>
              </div>
              {checksOpen === a.id && <AnswerReview kind="check" load={() => assignmentChecks(a.id, studentId)} deps={[a.id, studentId]} />}
              {open === a.id && (a.level === "manual"
                ? <SubmissionReview assignmentId={a.id} studentId={studentId} onChanged={state.reload} />
                : <Doubts assignmentId={a.id} studentId={studentId} />)}
            </div>
          ))}
        </div>
      )}
    </Async>
  );
}
