import { useState } from "react";
import { assignmentDoubts, deleteAssignment, listAssignments } from "../api/learning";
import { Async, Empty, ErrorNote, Pill, fmtDate, fmtDateTime, isOverdue, useLoad, useSubmit } from "../shared/ui";

const LEVEL = { subject: "Whole book", chapter: "Chapter", concept: "Ideas", exercise: "Exercise" };

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
                    {a.chapter_title && <span className="chip">{a.chapter_title}</span>}
                    <span className="chip">{a.concept_count} {a.concept_count === 1 ? "idea" : "ideas"}</span>
                    {studentId && <span className="chip">{a.student_id ? "Just this student" : "Whole room"}</span>}
                  </div>
                </div>
                <div className="small">
                  {a.due_date ? (isOverdue(a.due_date) ? <Pill kind="weak">Was due {fmtDate(a.due_date)}</Pill> : `Due ${fmtDate(a.due_date)}`) : `Set ${fmtDate(a.created_at)}`}
                </div>
              </div>
              <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
                <button className="btn secondary small-btn" aria-expanded={open === a.id} onClick={() => setOpen(open === a.id ? null : a.id)}>
                  Doubt
                </button>
                <button className="btn danger small-btn"
                  onClick={() => window.confirm("Delete this assignment? Students keep their own doubt and check history.") && run(async () => { await deleteAssignment(a.id); state.reload(); })}>
                  Delete
                </button>
              </div>
              {open === a.id && <Doubts assignmentId={a.id} studentId={studentId} />}
            </div>
          ))}
        </div>
      )}
    </Async>
  );
}
