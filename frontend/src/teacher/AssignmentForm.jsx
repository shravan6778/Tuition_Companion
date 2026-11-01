import { useState } from "react";
import { createAssignment } from "../api/learning";
import { ErrorNote, Tabs, useSubmit } from "../shared/ui";
import AssignmentTree from "./AssignmentTree";
import { EMPTY_SELECTION, selectionToAssignment } from "./assignmentSelection";

// Create an assignment for one room or one student (exactly one of roomId / studentId).
// Two kinds: work from a book (below), or school homework ("manual": a subject, a title and what to do, no book at all).
// The teacher picks from a tree (book > chapter > concepts, examples, exercise questions, figures); what was ticked decides the
// level: whole book -> subject, whole chapter -> chapter, any example / question / figure -> items, only concepts -> concept.
export default function AssignmentForm({ books, roomId, studentId, onCreated }) {
  const [mode, setMode] = useState("book");
  const [sel, setSel] = useState(EMPTY_SELECTION);
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const { busy, error, setError, run } = useSubmit();

  const target = mode === "manual"
    ? (subject.trim() ? { level: "manual", subject: subject.trim(), description: description.trim() || undefined } : null)
    : selectionToAssignment(sel);

  const submit = (e) => {
    e.preventDefault();
    if (!target) return;
    run(async () => {
      const created = await createAssignment({
        ...target, room_id: roomId || undefined, student_id: studentId || undefined,
        title: title.trim() || undefined, due_date: due || undefined,
      });
      setSel(EMPTY_SELECTION); setSubject(""); setDescription(""); setTitle(""); setDue("");
      onCreated?.(created);
    });
  };

  return (
    <form className="card stack" onSubmit={submit}>
      <h3>Set new work</h3>
      <Tabs tabs={[["book", "From a book"], ["manual", "School homework"]]} value={mode} onChange={setMode} />
      {mode === "manual" ? (
        <div className="stack">
          <p className="small mb0">Homework that isn't in an uploaded book. Students send a photo or say their answer, and you mark it good, needs work or redo.</p>
          <div>
            <label htmlFor={`af-subject-${roomId || studentId}`}>Subject</label>
            <input id={`af-subject-${roomId || studentId}`} className="input" value={subject} maxLength={120} required
              placeholder="e.g. Hindi" onChange={(e) => setSubject(e.target.value)} />
          </div>
          <div>
            <label htmlFor={`af-desc-${roomId || studentId}`}>What should they do? (optional)</label>
            <textarea id={`af-desc-${roomId || studentId}`} className="input" value={description} maxLength={4000}
              placeholder="e.g. Answer questions 1 to 5 from the school worksheet" onChange={(e) => setDescription(e.target.value)} />
          </div>
        </div>
      ) : (
        <div>
          <div className="small" id={`af-tree-label-${roomId || studentId}`}>What are you assigning?</div>
          <AssignmentTree books={books} value={sel} onChange={setSel} idPrefix={`af-${roomId || studentId}`} />
        </div>
      )}

      <div className="grid2">
        <div>
          <label htmlFor="af-title">Title (optional)</label>
          <input id="af-title" className="input" value={title} maxLength={200} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div>
          <label htmlFor="af-due">Due date (optional)</label>
          <input id="af-due" type="date" className="input" value={due} onChange={(e) => setDue(e.target.value)} />
        </div>
      </div>

      <ErrorNote error={error} />
      <div className="row">
        <span className="small">Goes to {roomId ? "every student in this room" : "this student only"}.</span>
        <button className="btn" disabled={busy || !target} onClick={() => setError("")}>
          {busy ? "Saving..." : "Assign work"}
        </button>
      </div>
    </form>
  );
}
