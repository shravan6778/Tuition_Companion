import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function Library() {
  const [subjects, setSubjects] = useState(null);
  const [name, setName] = useState("");
  const [grade, setGrade] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(
    () =>
      api("/teacher/subjects")
        .then(setSubjects)
        .catch((e) => setError(e.message)),
    [],
  );
  useEffect(() => {
    load();
  }, [load]);

  async function create(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/teacher/subjects", {
        method: "POST",
        body: { name, grade: grade || null },
      });
      setName("");
      setGrade("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <Link className="back-link" to="/teacher">
        ← Back to rooms
      </Link>
      <Header title="Content library" />

      <form className="card stack" onSubmit={create}>
        <h3>Add a subject</h3>
        <div>
          <label htmlFor="sname">Subject name</label>
          <input
            id="sname"
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Maths"
            required
            minLength={2}
            maxLength={100}
          />
        </div>
        <div>
          <label htmlFor="sgrade">Grade (optional)</label>
          <input
            id="sgrade"
            className="input"
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
            placeholder="e.g. 10"
            maxLength={20}
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Add subject
        </button>
      </form>

      {subjects && subjects.length === 0 && (
        <div className="card">
          <h3>Your library is empty</h3>
          <p className="small">
            Add a subject, then upload its chapters. Subjects can be reused in
            any room.
          </p>
        </div>
      )}

      {subjects && subjects.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Grade</th>
                <th>Chapters</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {subjects.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.grade ?? "—"}</td>
                  <td>{s.chapter_count}</td>
                  <td>
                    <Link
                      className="btn secondary small-btn"
                      to={`/teacher/library/${s.id}`}
                    >
                      Manage chapters
                    </Link>
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
