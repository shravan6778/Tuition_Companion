import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../shared/api";
import Header from "../shared/Header";

export default function TeacherDashboard() {
  const [rooms, setRooms] = useState([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("single_class");

  useEffect(() => {
    loadRooms();
  }, []);

  async function loadRooms() {
    try {
      const res = await api.get("/teacher/rooms");
      setRooms(res.data || []);
    } catch (err) {
      console.error("Failed to load rooms:", err);
    }
  }

  async function createRoom(e) {
    e.preventDefault();
    try {
      await api.post("/teacher/rooms", { name, room_type: type });
      setName("");
      loadRooms();
    } catch (err) {
      alert("Failed to create room.");
    }
  }

  return (
    <div>
      <Header role="Teacher" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "900px", margin: "0 auto" }}
      >
        <div style={{ display: "flex", gap: "1rem", marginBottom: "2rem" }}>
          <Link
            to="/teacher/library"
            style={{
              padding: "0.6rem 1.2rem",
              background: "#0070f3",
              color: "#fff",
              textDecoration: "none",
              borderRadius: "5px",
            }}
          >
            Content Library
          </Link>
        </div>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>Create a room</h2>
          <form
            onSubmit={createRoom}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
              marginTop: "1rem",
            }}
          >
            <div>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Room name
              </label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={{ padding: "0.5rem", width: "100%" }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Room type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value)}
                style={{ padding: "0.5rem", width: "100%" }}
              >
                <option value="single_class">Single class</option>
                <option value="mixed_class">Mixed class</option>
              </select>
            </div>
            <button
              type="submit"
              style={{ padding: "0.6rem 1.2rem", alignSelf: "flex-start" }}
            >
              Create room
            </button>
          </form>
        </div>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <h2>Your rooms</h2>
          {rooms.length === 0 ? (
            <p>No rooms created yet.</p>
          ) : (
            <table
              style={{
                width: "100%",
                textAlign: "left",
                borderCollapse: "collapse",
                marginTop: "1rem",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  <th style={{ padding: "0.5rem" }}>Room</th>
                  <th style={{ padding: "0.5rem" }}>Type</th>
                  <th style={{ padding: "0.5rem" }}>Join code</th>
                  <th style={{ padding: "0.5rem" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {rooms.map((r) => (
                  <tr key={r.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.5rem" }}>{r.name}</td>
                    <td style={{ padding: "0.5rem" }}>{r.room_type}</td>
                    <td style={{ padding: "0.5rem" }}>
                      <strong>{r.join_code}</strong>
                    </td>
                    <td style={{ padding: "0.5rem" }}>
                      <Link
                        to={`/teacher/rooms/${r.id}`}
                        style={{ color: "#0070f3" }}
                      >
                        View members
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
