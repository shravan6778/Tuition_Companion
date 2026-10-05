import React, { useEffect, useState } from "react";
import { fetchTeacherRequests, dismissRequest, fulfillRequest } from "../api/content";

// Inbox of chapters students asked for. Requests also close themselves when a matching chapter finishes processing.
export default function ChapterRequests({ refreshKey }) {
  const [requests, setRequests] = useState([]);

  async function load() {
    try {
      setRequests(await fetchTeacherRequests("open"));
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    load();
  }, [refreshKey]);

  if (requests.length === 0) return null;

  async function act(fn, id) {
    try {
      await fn(id);
    } finally {
      await load();
    }
  }

  return (
    <section style={{ marginBottom: "2rem", border: "1px solid #e0b000", padding: "1rem", background: "#fffbea" }}>
      <h3>Chapter requests ({requests.length})</h3>
      <ul>
        {requests.map((r) => (
          <li key={r.id} style={{ margin: "0.4rem 0" }}>
            <b>{r.student_name}</b> asked for <i>{r.chapter_hint}</i> in {r.book.class_name} {r.book.subject}{" "}
            <button onClick={() => act(fulfillRequest, r.id)}>Mark done</button>{" "}
            <button onClick={() => act(dismissRequest, r.id)}>Dismiss</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
