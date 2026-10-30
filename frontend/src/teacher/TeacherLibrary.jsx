import { useState } from "react";
import { fetchBooks, fetchStudentBookOutlines } from "../api/content";
import { listRooms, listMembers } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, bookLabel, useLoad, useSubmit } from "../shared/ui";

export default function TeacherLibrary() {
  const refs = useLoad(fetchBooks);
  const rooms = useLoad(listRooms);
  const [studentId, setStudentId] = useState("");
  const [outlines, setOutlines] = useState(null);
  const [error, setError] = useState("");
  const { busy, run } = useSubmit();

  const loadStudent = () => run(async () => {
    if (!studentId) return;
    setError("");
    try { setOutlines(await fetchStudentBookOutlines(studentId)); }
    catch (e) { setError(e.message); }
  });

  return <>
    <Header title="Content Library" subtitle="Reference books plus privacy-safe views of students' own textbooks." />
    <div className="container stack">
      <div className="card stack">
        <h2>Reference library</h2>
        <Async state={refs}>{(books) => books.length ? <div className="items">{books.map((b) => <div className="item" key={b.id}><strong>{bookLabel(b)}</strong><div className="small">{b.board} · {b.publisher}{b.edition ? ` · ${b.edition}` : ""}</div></div>)}</div> : <Empty>No reference books found.</Empty>}</Async>
      </div>
      <div className="card stack">
        <h2>Student textbook outline</h2>
        <p className="small mb0">You can see chapter titles, concept names and exercise/item labels only. Page text, images and PDFs are never shown here.</p>
        <Async state={rooms}>{(rs) => <div className="stack">{rs.length === 0 ? <Empty>No rooms yet.</Empty> : rs.map((r) => <StudentPicker key={r.id} room={r} studentId={studentId} setStudentId={setStudentId} />)}<button className="btn" disabled={busy || !studentId} onClick={loadStudent}>Load selected student's outline</button></div>}</Async>
        <ErrorNote error={error} />
        {outlines && (outlines.length ? outlines.map((b) => <div className="card" key={b.id}><h3>{b.subject} · {b.publisher}</h3>{b.chapters.map((c) => <div className="item" key={c.id}><strong>{c.title}</strong><div className="small">Concepts: {c.concept_names.join(", ") || "none"}</div><div className="small">Items: {c.item_labels.join(", ") || "none"}</div></div>)}</div>) : <Empty>No private books uploaded by this student yet.</Empty>)}
      </div>
    </div>
  </>;
}

function StudentPicker({ room, studentId, setStudentId }) {
  const members = useLoad(() => listMembers(room.id), [room.id]);
  return <Async state={members}>{(ms) => <label>{room.name}<select className="input" value={studentId} onChange={(e) => setStudentId(e.target.value)}><option value="">Choose a student...</option>{ms.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}</select></label>}</Async>;
}
