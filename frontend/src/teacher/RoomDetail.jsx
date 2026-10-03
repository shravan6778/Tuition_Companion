import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../shared/api";
import Header from "../shared/Header";

export default function RoomDetail() {
  const { roomId } = useParams();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/teacher/rooms/${roomId}/members`)
      .then((res) => {
        setMembers(res.data || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [roomId]);

  return (
    <div>
      <Header role="Teacher" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}
      >
        <Link to="/teacher">← Back to rooms</Link>
        <h2 style={{ marginTop: "1rem" }}>Room Members</h2>
        <p style={{ color: "#666", marginBottom: "1.5rem" }}>
          Rooms only group students. Content is managed independently through
          the Content Library.
        </p>

        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          {loading ? (
            <p>Loading members...</p>
          ) : members.length === 0 ? (
            <p>No students have joined this room yet.</p>
          ) : (
            <table
              style={{
                width: "100%",
                textAlign: "left",
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "2px solid #ddd" }}>
                  <th style={{ padding: "0.5rem" }}>Student Name</th>
                  <th style={{ padding: "0.5rem" }}>Joined At</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id} style={{ borderBottom: "1px solid #eee" }}>
                    <td style={{ padding: "0.5rem" }}>{m.name}</td>
                    <td style={{ padding: "0.5rem" }}>
                      {new Date(m.joined_at).toLocaleDateString()}
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
