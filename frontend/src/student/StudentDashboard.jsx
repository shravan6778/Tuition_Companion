import React, { useState, useEffect } from "react";
import { useAuth } from "../auth/AuthContext";
import api from "../shared/api";
import Header from "../shared/Header";
import ChapterRequestPanel from "./ChapterRequestPanel.jsx";
import {
  fetchMyLinkedBooks,
  fetchStudentLibrary,
  linkBook,
} from "../api/content";

export default function StudentDashboard() {
  const { user } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [joinCode, setJoinCode] = useState("");
  const [linkedBooks, setLinkedBooks] = useState([]);
  const [availableBooks, setAvailableBooks] = useState([]);

  useEffect(() => {
    loadRooms();
    loadBooks();
  }, []);

  async function loadRooms() {
    try {
      const res = await api.get("/student/rooms");
      setRooms(res.data || []);
    } catch (err) {
      console.error("Failed to load rooms:", err);
    }
  }

  async function loadBooks() {
    try {
      const myBooks = await fetchMyLinkedBooks();
      setLinkedBooks(myBooks || []);
      setAvailableBooks((await fetchStudentLibrary()) || []);
    } catch (err) {
      console.error("Failed to load books:", err);
    }
  }

  async function joinRoom(e) {
    e.preventDefault();
    try {
      await api.post("/student/rooms/join", { join_code: joinCode });
      setJoinCode("");
      loadRooms();
    } catch (err) {
      alert("Failed to join room. Please verify the code.");
    }
  }

  async function handleLinkBook(e) {
    if (!e.target.value) return;
    try {
      await linkBook(e.target.value);
      await loadBooks();
    } catch (err) {
      alert("Failed to link book.");
    }
  }

  return (
    <div>
      <Header role="Student" />
      <div
        className="container"
        style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}
      >
        {/* Books & Doubts Section */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>My textbooks</h2>
          {linkedBooks.length === 0 ? (
            <p>
              You haven't linked any textbooks yet. Select a textbook below to
              get started.
            </p>
          ) : (
            <ul>
              {linkedBooks.map((b) => (
                <li key={b.id} style={{ margin: "0.5rem 0" }}>
                  <strong>
                    {b.class_name} {b.subject}
                  </strong>{" "}
                  ({b.publisher})
                </li>
              ))}
            </ul>
          )}

          <div style={{ marginTop: "1rem" }}>
            <select
              onChange={handleLinkBook}
              value=""
              style={{ padding: "0.5rem" }}
            >
              <option value="" disabled>
                Link a textbook...
              </option>
              {availableBooks.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.board} - {b.class_name} {b.subject} ({b.publisher})
                  {b.is_reference ? " - official" : ""}
                </option>
              ))}
            </select>
          </div>

          <ChapterRequestPanel linkedBooks={linkedBooks} />
        </div>

        {/* Room Section */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "2rem",
          }}
        >
          <h2>Join a room</h2>
          <form
            onSubmit={joinRoom}
            style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}
          >
            <input
              placeholder="Code from teacher"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              required
              style={{ padding: "0.5rem", flex: 1 }}
            />
            <button type="submit" style={{ padding: "0.5rem 1rem" }}>
              Join
            </button>
          </form>
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
          <h2>My rooms</h2>
          {rooms.length === 0 ? (
            <p>No rooms joined yet.</p>
          ) : (
            <ul>
              {rooms.map((r) => (
                <li key={r.id} style={{ margin: "0.5rem 0" }}>
                  <strong>{r.name}</strong> ({r.room_type})
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Parent Link Code */}
        <div
          className="card"
          style={{
            padding: "1.5rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
          }}
        >
          <h2>Parent link code</h2>
          <p style={{ color: "#666", fontSize: "0.9rem" }}>
            Give this code to your parent so they can follow your progress:
          </p>
          <div
            style={{
              fontSize: "1.5rem",
              letterSpacing: "3px",
              fontWeight: "bold",
              padding: "0.8rem 1.5rem",
              background: "#e0f2f1",
              display: "inline-block",
              borderRadius: "4px",
              marginTop: "0.5rem",
            }}
          >
            {user?.link_code || "N/A"}
          </div>
        </div>
      </div>
    </div>
  );
}
