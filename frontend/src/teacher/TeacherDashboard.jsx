import { useEffect, useState } from "react";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function TeacherDashboard() {
  const [rooms, setRooms] = useState(null);
  const [name, setName] = useState("");
  const [roomType, setRoomType] = useState("single_class");
  const [error, setError] = useState("");

  const load = () =>
    api("/teacher/rooms")
      .then(setRooms)
      .catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  async function create(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/teacher/rooms", {
        method: "POST",
        body: { name, room_type: roomType },
      });
      setName("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container">
      <Header title="Your rooms" />

      <form className="card stack" onSubmit={create}>
        <h3>Create a room</h3>
        <div>
          <label htmlFor="rname">Room name</label>
          <input
            id="rname"
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Class 10 Maths"
            required
            minLength={2}
          />
        </div>
        <div>
          <label htmlFor="rtype">Room type</label>
          <select
            id="rtype"
            className="input"
            value={roomType}
            onChange={(e) => setRoomType(e.target.value)}
          >
            <option value="single_class">Single class</option>
            <option value="mixed_class">Mixed class</option>
          </select>
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Create room
        </button>
      </form>

      {rooms && rooms.length === 0 && (
        <div className="card">
          <h3>Create your first room</h3>
          <p className="small">
            Share the join code with your students once it's created.
          </p>
        </div>
      )}

      {rooms && rooms.length > 0 && (
        <div className="card" style={{ overflowX: "auto" }}>
          <table className="table">
            <thead>
              <tr>
                <th>Room</th>
                <th>Type</th>
                <th>Join code</th>
                <th>Students</th>
              </tr>
            </thead>
            <tbody>
              {rooms.map((r) => (
                <tr key={r.id}>
                  <td>{r.name}</td>
                  <td>
                    {r.room_type === "single_class"
                      ? "Single class"
                      : "Mixed class"}
                  </td>
                  <td>
                    <span className="code" style={{ fontSize: 16 }}>
                      {r.join_code}
                    </span>
                  </td>
                  <td>{r.member_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
