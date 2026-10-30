import { useState } from "react";
import {
  uploadStudentFrontPages, createStudentBook, planStudentWholeBook,
  confirmStudentWholeBook, uploadStudentChapterPages, removeStudentBook,
  createStudentChapter,
} from "../api/content";
import { ErrorNote, useSubmit } from "../shared/ui";

export default function StudentBookUpload({ books, reload }) {
  const [frontFile, setFrontFile] = useState(null);
  const [draft, setDraft] = useState(null);
  const [form, setForm] = useState({ board: "", class_name: "", subject: "", publisher: "", edition: "", school: "", is_customized: false });
  const [wholeBookId, setWholeBookId] = useState("");
  const [wholeFile, setWholeFile] = useState(null);
  const [plan, setPlan] = useState(null);
  const [chapterFiles, setChapterFiles] = useState({});
  // Chapter-wise upload: create a new chapter then upload its PDF
  const [newChBookId, setNewChBookId] = useState("");
  const [newChTitle, setNewChTitle] = useState("");
  const [newChSeq, setNewChSeq] = useState(1);
  const [newChFile, setNewChFile] = useState(null);
  const { busy, error, setError, run } = useSubmit();

  const uploadFront = () => run(async () => {
    if (!frontFile) throw new Error("Choose the cover/publisher pages first.");
    const d = await uploadStudentFrontPages(frontFile);
    setDraft(d);
    setForm((f) => ({ ...f, ...Object.fromEntries(Object.entries(d.metadata || {}).map(([k, v]) => [k, v ?? ""])) }));
  });

  const create = () => run(async () => {
    const book = await createStudentBook({ ...form, draft_id: draft?.draft_id });
    setDraft(null); setFrontFile(null); setForm({ board: "", class_name: "", subject: "", publisher: "", edition: "", school: "", is_customized: false });
    reload?.();
    return book;
  });

  const planWhole = () => run(async () => {
    if (!wholeBookId || !wholeFile) throw new Error("Choose a private book and textbook PDF.");
    const p = await planStudentWholeBook(wholeBookId, wholeFile);
    setPlan(p);
  });

  const confirmWhole = () => run(async () => {
    if (!plan) return;
    await confirmStudentWholeBook(wholeBookId, plan.draft_id, plan.proposed_chapters);
    setPlan(null); setWholeFile(null); reload?.();
  });

  const addChapterAndUpload = () => run(async () => {
    if (!newChBookId) throw new Error("Choose a private book first.");
    if (!newChTitle.trim()) throw new Error("Enter a chapter title.");
    if (!newChFile) throw new Error("Choose a PDF or image file for this chapter.");
    const chapter = await createStudentChapter(newChBookId, { title: newChTitle.trim(), sequence_num: newChSeq });
    await uploadStudentChapterPages(newChBookId, chapter.id, newChFile);
    setNewChTitle(""); setNewChSeq((s) => s + 1); setNewChFile(null);
    reload?.();
  });

  const privateBooks = books.filter((b) => !b.is_reference);

  return (
    <div className="card stack">
      <h2>Upload your textbook</h2>
      <p className="small mb0">Your uploaded book belongs only to you. Your teacher can see chapter, concept and exercise labels, but not page text or images.</p>
      <div className="stack">
        <h3 className="mb0">1. Cover + publisher pages</h3>
        <input type="file" accept="application/pdf,image/*" onChange={(e) => setFrontFile(e.target.files?.[0] || null)} />
        <button className="btn" disabled={busy || !frontFile} onClick={uploadFront}>Read book details</button>
        {draft && <div className="callout info">Details were read. Check them below, then create your private book.</div>}
        {(draft || form.board) && (
          <div className="grid2">
            {[["board","Board"],["class_name","Class"],["subject","Subject"],["publisher","Publisher"],["edition","Edition"],["school","School"]].map(([k,label]) => (
              <label key={k}>{label}<input className="input" value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} /></label>
            ))}
            <label><input type="checkbox" checked={form.is_customized} onChange={(e) => setForm({ ...form, is_customized: e.target.checked })} /> School-customized edition</label>
            <button className="btn" disabled={busy || !form.board || !form.class_name || !form.subject || !form.publisher} onClick={create}>Create private book</button>
          </div>
        )}
      </div>
      <div className="stack">
        <h3 className="mb0">2a. Whole textbook PDF</h3>
        <p className="small mb0">Upload the full textbook and split it into chapters automatically.</p>
        <select className="input" value={wholeBookId} onChange={(e) => setWholeBookId(e.target.value)}>
          <option value="">Choose your private book...</option>
          {privateBooks.map((b) => <option key={b.id} value={b.id}>{b.subject} · {b.publisher}</option>)}
        </select>
        <input type="file" accept="application/pdf" onChange={(e) => setWholeFile(e.target.files?.[0] || null)} />
        <button className="btn secondary" disabled={busy || !wholeBookId || !wholeFile} onClick={planWhole}>Read chapter bookmarks</button>
        {plan && <div className="stack"><div className="small">Review the detected chapter split before processing.</div>{plan.proposed_chapters.map((c, i) => <div className="row" key={i}><span>{c.title} · pages {c.start_page}-{c.end_page}</span></div>)}<button className="btn" disabled={busy} onClick={confirmWhole}>Process these chapters</button></div>}
      </div>
      <div className="stack">
        <h3 className="mb0">2b. Upload chapter by chapter</h3>
        <p className="small mb0">Add one chapter at a time — useful when you only have part of the textbook, or scanned individual chapters.</p>
        <select className="input" value={newChBookId} onChange={(e) => { setNewChBookId(e.target.value); setNewChSeq(
          (privateBooks.find((b) => b.id === e.target.value)?.chapters?.length || 0) + 1
        ); }}>
          <option value="">Choose your private book...</option>
          {privateBooks.map((b) => <option key={b.id} value={b.id}>{b.subject} · {b.publisher}</option>)}
        </select>
        {newChBookId && (
          <div className="grid2">
            <label>Chapter title<input className="input" value={newChTitle} onChange={(e) => setNewChTitle(e.target.value)} placeholder="e.g. Motion in a Straight Line" /></label>
            <label>Sequence #<input className="input" type="number" min={1} value={newChSeq} onChange={(e) => setNewChSeq(Number(e.target.value) || 1)} /></label>
            <label>Chapter PDF or scan<input type="file" accept="application/pdf,image/*" onChange={(e) => setNewChFile(e.target.files?.[0] || null)} /></label>
            <button className="btn" disabled={busy || !newChTitle.trim() || !newChFile} onClick={addChapterAndUpload}>Create chapter &amp; upload</button>
          </div>
        )}
        {privateBooks.length === 0 && <p className="small mb0">Create a private book first (step 1).</p>}
      </div>
      <div className="stack">
        <h3 className="mb0">3. Replace an existing chapter</h3>
        {privateBooks.flatMap((b) => (b.chapters || []).map((c) => ({ b, c }))).map(({ b, c }) => (
          <div className="row" key={`${b.id}-${c.id}`}>
            <span style={{ flex: 1 }}>{b.subject} · Ch {c.sequence_num}: {c.title}</span>
            <input type="file" accept="application/pdf,image/*" onChange={(e) => setChapterFiles({ ...chapterFiles, [c.id]: e.target.files?.[0] || null })} />
            <button className="btn ghost small-btn" disabled={busy || !chapterFiles[c.id]} onClick={() => run(async () => { await uploadStudentChapterPages(b.id, c.id, chapterFiles[c.id]); reload?.(); })}>Upload</button>
          </div>
        ))}
        {privateBooks.flatMap((b) => b.chapters || []).length === 0 && <p className="small mb0">No chapters yet. Upload a whole book (2a) or add chapters one at a time (2b).</p>}
      </div>
      <ErrorNote error={error} />
      {privateBooks.length > 0 && <div className="stack"><h3 className="mb0">Remove a private book</h3>{privateBooks.map((b) => <div className="row" key={b.id}><span>{b.subject} · {b.publisher}</span><button className="btn ghost small-btn" disabled={busy} onClick={() => window.confirm("Delete this book, its pages, embeddings, graph data and stored PDFs?") && run(async () => { await removeStudentBook(b.id); reload?.(); })}>Remove</button></div>)}</div>}
    </div>
  );
}
