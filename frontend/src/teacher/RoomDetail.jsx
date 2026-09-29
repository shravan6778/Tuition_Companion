import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function RoomDetail() {
  const { roomId } = useParams();
  const [room, setRoom] = useState(null);
  const [attached, setAttached] = useState(null);
  const [library, setLibrary] = useState([]);
  const [pick, setPick] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(
    () =>
      Promise.all([
        api("/teacher/rooms"),
        api(`/teacher/rooms/${roomId}/subjects`),
        api("/teacher/subjects"),
      ])
        .then(([rooms, inRoom, all]) => {
          setRoom(rooms.find((r) => r.id === roomId) ?? null);
          setAttached(inRoom);
          setLibrary(all);
        })
        .catch((e) => setError(e.message)),
    [roomId],
  );
  useEffect(() => {
    load();
  }, [load]);

  const available = library.filter(
    (s) => !attached?.some((a) => a.id === s.id),
  );

  async function attach(e) {
    e.preventDefault();
    if (!pick) return;
    setError("");
    try {
      await api(`/teacher/rooms/${roomId}/subjects`, {
        method: "POST",
        body: { subject_id: pick },
      });
      setPick("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function detach(subject) {
    if (
      !window.confirm(
        `Remove "${subject.name}" from this room? It stays in your library.`,
      )
    )
      return;
    setError("");
    try {
      await api(`/teacher/rooms/${roomId}/subjects/${subject.id}`, {
        method: "DELETE",
      });
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <Link className="back-link" to="/teacher">
        ← Back to rooms
      </Link>
      <Header title={room ? room.name : "Room"} />

      <form className="card stack" onSubmit={attach}>
        <h3>Add a subject from your library</h3>
        {available.length === 0 ? (
          <p className="small">
            {library.length === 0 ? (
              <>
                Your library is empty.{" "}
                <Link to="/teacher/library">Add a subject</Link> first.
              </>
            ) : (
              "Every subject in your library is already in this room."
            )}
          </p>
        ) : (
          <>
            <label htmlFor="subj">Subject</label>
            <select
              id="subj"
              className="input"
              value={pick}
              onChange={(e) => setPick(e.target.value)}
              required
            >
              <option value="">Choose a subject…</option>
              {available.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                  {s.grade ? ` (Grade ${s.grade})` : ""}
                </option>
              ))}
            </select>
            <button className="btn" type="submit" disabled={!pick}>
              Add to room
            </button>
          </>
        )}
        {error && <div className="error">{error}</div>}
      </form>

      {attached && attached.length === 0 && (
        <div className="card">
          <h3>No subjects in this room yet</h3>
          <p className="small">
            Students only see subjects you add here, and only chapters that are
            ready.
          </p>
        </div>
      )}

      {attached && attached.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Chapters</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {attached.map((s) => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>{s.chapter_count}</td>
                  <td>
                    <button
                      className="btn danger small-btn"
                      onClick={() => detach(s)}
                    >
                      Remove from room
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
