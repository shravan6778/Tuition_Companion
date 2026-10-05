import React, { useEffect, useState } from "react";
import { requestChapter, fetchMyRequests, cancelRequest } from "../api/content";

const STATUS_TEXT = {
  open: "waiting for your teacher",
  fulfilled: "added - check your textbook",
  dismissed: "your teacher can't add this one",
  cancelled: "cancelled",
};

// "A chapter I need isn't in my teacher's book": ask the teacher to add it. Official books have no teacher
// to ask, so they're not offered here.
export default function ChapterRequestPanel({ linkedBooks }) {
  const privateBooks = linkedBooks.filter((b) => !b.is_reference);
  const [requests, setRequests] = useState([]);
  const [bookId, setBookId] = useState("");
  const [hint, setHint] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    try {
      setRequests(await fetchMyRequests());
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    load();
  }, [linkedBooks.length]);

  useEffect(() => {
    if (!bookId && privateBooks.length > 0) setBookId(privateBooks[0].id);
  }, [privateBooks.length]);

  if (privateBooks.length === 0 && requests.length === 0) return null;

  async function submit(e) {
    e.preventDefault();
    try {
      await requestChapter(bookId, hint);
      setHint("");
      setMessage("Sent to your teacher.");
      await load();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function cancel(id) {
    await cancelRequest(id);
    await load();
  }

  return (
    <div style={{ marginTop: "1.5rem" }}>
      {privateBooks.length > 0 && (
        <>
          <h3>Missing a chapter?</h3>
          <form onSubmit={submit} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <select value={bookId} onChange={(e) => setBookId(e.target.value)}>
              {privateBooks.map((b) => (
                <option key={b.id} value={b.id}>{b.class_name} {b.subject}</option>
              ))}
            </select>
            <input
              placeholder="Which chapter? (e.g. Chapter 5 - Force)"
              value={hint}
              onChange={(e) => setHint(e.target.value)}
              required
              minLength={3}
              maxLength={200}
              style={{ flex: 1, minWidth: "12rem" }}
            />
            <button type="submit">Ask my teacher</button>
          </form>
          {message && <p style={{ color: "blue" }}>{message}</p>}
        </>
      )}
      {requests.length > 0 && (
        <>
          <h4>My requests</h4>
          <ul>
            {requests.map((r) => (
              <li key={r.id}>
                {r.chapter_hint} ({r.book.class_name} {r.book.subject}) - {STATUS_TEXT[r.status]}{" "}
                {r.status === "open" && <button onClick={() => cancel(r.id)}>Cancel</button>}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
