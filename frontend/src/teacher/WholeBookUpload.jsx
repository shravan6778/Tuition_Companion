import React, { useState } from "react";
import { planWholeBook, confirmWholeBook } from "../api/content";

// Upload the whole textbook as one PDF, review the chapter split, then confirm. Nothing is
// processed until the teacher confirms.
export default function WholeBookUpload({ book, onDone }) {
  const [plan, setPlan] = useState(null); // { draft_id, page_count }
  const [rows, setRows] = useState([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMessage("Reading the PDF...");
    try {
      const p = await planWholeBook(book.id, file);
      setPlan(p);
      setRows(p.proposed_chapters);
      setMessage(
        p.proposed_chapters.length
          ? `The PDF has ${p.page_count} pages. We split it using its bookmarks - check the page ranges.`
          : `The PDF has ${p.page_count} pages and no bookmarks. Add each chapter with its page range.`,
      );
    } catch (err) {
      setMessage(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  const update = (i, key, value) =>
    setRows(rows.map((r, j) => (j === i ? { ...r, [key]: value } : r)));

  async function handleConfirm() {
    setBusy(true);
    try {
      const chapters = rows.map((r) => ({
        title: r.title,
        start_page: Number(r.start_page),
        end_page: Number(r.end_page),
      }));
      const created = await confirmWholeBook(book.id, plan.draft_id, chapters);
      setPlan(null);
      setRows([]);
      setMessage(`Started processing ${created.length} chapter(s). Their status updates below.`);
      await onDone();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ marginTop: "1.5rem", padding: "1rem", backgroundColor: "#f4f9f4" }}>
      <h4>Upload the whole textbook</h4>
      {!plan && (
        <input type="file" accept="application/pdf" onChange={handleFile} disabled={busy} />
      )}
      {message && <p style={{ color: "blue" }}>{message}</p>}
      {plan && (
        <>
          <table>
            <thead>
              <tr><th>Chapter title</th><th>From page</th><th>To page</th><th /></tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  <td><input value={r.title} onChange={(e) => update(i, "title", e.target.value)} /></td>
                  <td><input type="number" min="1" max={plan.page_count} value={r.start_page}
                    onChange={(e) => update(i, "start_page", e.target.value)} style={{ width: "5rem" }} /></td>
                  <td><input type="number" min="1" max={plan.page_count} value={r.end_page}
                    onChange={(e) => update(i, "end_page", e.target.value)} style={{ width: "5rem" }} /></td>
                  <td><button type="button" onClick={() => setRows(rows.filter((_, j) => j !== i))}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            <button type="button" onClick={() => setRows([...rows, { title: "", start_page: 1, end_page: 1 }])}>
              Add chapter
            </button>{" "}
            <button type="button" onClick={handleConfirm} disabled={busy || rows.length === 0}>
              Confirm and process {rows.length} chapter(s)
            </button>{" "}
            <button type="button" onClick={() => { setPlan(null); setMessage(""); }}>Cancel</button>
          </p>
        </>
      )}
    </div>
  );
}
