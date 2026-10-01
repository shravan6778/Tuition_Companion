import React, { useState, useEffect } from "react";
import { fetchUnverifiedPages, verifyPage } from "../api/content";

export default function TeacherVerificationQueue() {
  const [unverifiedPages, setUnverifiedPages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadUnverified();
  }, []);

  async function loadUnverified() {
    setLoading(true);
    try {
      const data = await fetchUnverifiedPages();
      setUnverifiedPages(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify(pageId) {
    try {
      await verifyPage(pageId);
      setUnverifiedPages(unverifiedPages.filter((p) => p.id !== pageId));
    } catch (err) {
      alert(`Verification failed: ${err.message}`);
    }
  }

  return (
    <div style={{ padding: "1.5rem" }}>
      <h3>Student Upload Verification Queue</h3>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Review doubt pages uploaded by students and mark them verified to add
        them permanently to the official reference corpus[cite: 2].
      </p>

      {loading && <p>Loading queue...</p>}
      {!loading && unverifiedPages.length === 0 && (
        <p>No unverified pages pending review.</p>
      )}

      {unverifiedPages.map((page) => (
        <div
          key={page.id}
          style={{
            border: "1px solid #ddd",
            margin: "1rem 0",
            padding: "1rem",
          }}
        >
          <p>
            <strong>Page #{page.page_number}</strong>
          </p>
          <p
            style={{
              maxHeight: "100px",
              overflowY: "auto",
              background: "#f1f1f1",
              padding: "0.5rem",
            }}
          >
            {page.content_text}
          </p>
          <button onClick={() => handleVerify(page.id)}>
            Confirm & Verify Page
          </button>
        </div>
      ))}
    </div>
  );
}
