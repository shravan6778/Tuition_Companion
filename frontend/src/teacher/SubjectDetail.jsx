import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api";
import Header from "../shared/Header";
import StatusBadge from "./StatusBadge";

const MAX_MB = 20; // keep in sync with MAX_UPLOAD_MB on the backend

export default function SubjectDetail() {
  const { subjectId } = useParams();
  const [subject, setSubject] = useState(null);
  const [chapters, setChapters] = useState(null);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fileInput = useRef(null);

  const load = useCallback(
    () =>
      Promise.all([
        api("/teacher/subjects"),
        api(`/teacher/subjects/${subjectId}/chapters`),
      ])
        .then(([subjects, list]) => {
          setSubject(subjects.find((s) => s.id === subjectId) ?? null);
          setChapters(list);
        })
        .catch((e) => setError(e.message)),
    [subjectId],
  );
  useEffect(() => {
    load();
  }, [load]);

  function pickFile(e) {
    const f = e.target.files[0] ?? null;
    setError("");
    if (f && f.size > MAX_MB * 1024 * 1024) {
      setError(`That file is larger than ${MAX_MB} MB.`);
      e.target.value = "";
      setFile(null);
      return;
    }
    setFile(f);
  }

  async function upload(e) {
    e.preventDefault();
    if (!file) return;
    setError("");
    setBusy(true);
    try {
      const form = new FormData();
      form.append("title", title);
      form.append("file", file);
      await api(`/teacher/subjects/${subjectId}/chapters`, {
        method: "POST",
        body: form,
      });
      setTitle("");
      setFile(null);
      if (fileInput.current) fileInput.current.value = "";
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(chapter) {
    if (!window.confirm(`Delete "${chapter.title}"?`)) return;
    setError("");
    try {
      await api(`/teacher/subjects/${subjectId}/chapters/${chapter.id}`, {
        method: "DELETE",
      });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <Link className="back-link" to="/teacher/library">
        ← Back to library
      </Link>
      <Header title={subject ? subject.name : "Chapters"} />

      <form className="card stack" onSubmit={upload}>
        <h3>Upload a chapter</h3>
        <div>
          <label htmlFor="ctitle">Chapter title</label>
          <input
            id="ctitle"
            className="input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Chapter 1: Real Numbers"
            required
            minLength={2}
            maxLength={200}
          />
        </div>
        <div>
          <label htmlFor="cfile">PDF, PNG or JPG (up to {MAX_MB} MB)</label>
          <input
            id="cfile"
            ref={fileInput}
            className="input"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
            onChange={pickFile}
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit" disabled={busy || !file}>
          {busy ? "Uploading…" : "Upload chapter"}
        </button>
      </form>

      {chapters && chapters.length === 0 && (
        <div className="card">
          <h3>No chapters yet</h3>
          <p className="small">Upload the first chapter above.</p>
        </div>
      )}

      {chapters && chapters.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <div className="row" style={{ marginBottom: 8 }}>
            <h3>Chapters</h3>
            <button className="btn secondary small-btn" onClick={load}>
              Refresh status
            </button>
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {chapters.map((c) => (
                <tr key={c.id}>
                  <td>{c.position}</td>
                  <td>{c.title}</td>
                  <td>
                    <StatusBadge status={c.status} />
                    {c.error_message && (
                      <div className="small">{c.error_message}</div>
                    )}
                  </td>
                  <td>
                    <button
                      className="btn danger small-btn"
                      onClick={() => remove(c)}
                      disabled={c.status === "processing"}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
