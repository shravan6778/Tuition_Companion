import { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function StudentDashboard() {
  const { profile } = useAuth();
  const [rooms, setRooms] = useState(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api("/student/rooms")
      .then(setRooms)
      .catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  async function join(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/student/rooms/join", {
        method: "POST",
        body: { join_code: code },
      });
      setCode("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container stack">
      <Header title="My learning" />

      <form className="card stack" onSubmit={join}>
        <h3>Join a room</h3>
        <label htmlFor="jc">Code from your teacher</label>
        <input
          id="jc"
          className="input"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="ABC123"
          required
        />
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Join
        </button>
      </form>

      <div className="card">
        <h3>My rooms</h3>
        {rooms && rooms.length === 0 && (
          <p className="small">You haven't joined a room yet.</p>
        )}
        {rooms?.map((r) => (
          <p key={r.id}>{r.name}</p>
        ))}
      </div>

      <div className="card">
        <h3>Parent link code</h3>
        <p className="small">
          Give this to your parent so they can follow your progress.
        </p>
        <span className="code">{profile.link_code}</span>
      </div>
    </div>
  );
}
