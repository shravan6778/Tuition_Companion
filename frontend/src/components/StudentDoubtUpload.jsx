import React, { useState, useEffect } from "react";
import { fetchMyLinkedBooks, uploadStudentDoubtPage } from "../api/content";

export default function StudentDoubtUpload() {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState("");
  const [selectedChapterId, setSelectedChapterId] = useState("");
  const [status, setStatus] = useState("");
  const [processedConcepts, setProcessedConcepts] = useState([]);

  useEffect(() => {
    fetchMyLinkedBooks().then((data) => {
      setBooks(data);
      if (data.length > 0) {
        setSelectedBookId(data[0].id);
        if (data[0].chapters?.length > 0) {
          setSelectedChapterId(data[0].chapters[0].id);
        }
      }
    });
  }, []);

  const activeBook = books.find((b) => b.id === selectedBookId);

  async function handleDoubtPageCapture(e) {
    const file = e.target.files?.[0];
    if (!file || !selectedBookId || !selectedChapterId) return;

    setStatus("Processing single-page doubt pipeline...");
    setProcessedConcepts([]);

    try {
      const pages = await uploadStudentDoubtPage(
        selectedBookId,
        selectedChapterId,
        file,
      );
      setStatus(
        "Page processed and saved as student-contributed (unverified)[cite: 2].",
      );
      const allExtracted = pages.flatMap((p) => p.concepts || []);
      setProcessedConcepts(allExtracted);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  }

  return (
    <div style={{ padding: "1.5rem", maxWidth: "600px", margin: "auto" }}>
      <h3>Ask a Doubt from Textbook</h3>
      <p style={{ fontSize: "0.85rem", color: "#555" }}>
        Take a picture of the page you are stuck on. The page will be ingested
        immediately for your answer[cite: 2].
      </p>

      {/* Select Linked Book */}
      <div style={{ marginBottom: "1rem" }}>
        <label>Your Book: </label>
        <select
          value={selectedBookId}
          onChange={(e) => {
            setSelectedBookId(e.target.value);
            const b = books.find((x) => x.id === e.target.value);
            if (b?.chapters?.length > 0) setSelectedChapterId(b.chapters[0].id);
          }}
        >
          {books.map((b) => (
            <option key={b.id} value={b.id}>
              {b.class_name} {b.subject} ({b.publisher})
            </option>
          ))}
        </select>
      </div>

      {/* Select Chapter */}
      {activeBook && (
        <div style={{ marginBottom: "1rem" }}>
          <label>Chapter: </label>
          <select
            value={selectedChapterId}
            onChange={(e) => setSelectedChapterId(e.target.value)}
          >
            {activeBook.chapters?.map((ch) => (
              <option key={ch.id} value={ch.id}>
                {ch.sequence_num}. {ch.title}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Upload/Camera Input */}
      <div
        style={{
          border: "2px dashed #aaa",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <input
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleDoubtPageCapture}
        />
      </div>

      {status && <p style={{ marginTop: "1rem", color: "blue" }}>{status}</p>}

      {/* Extracted Concepts Output */}
      {processedConcepts.length > 0 && (
        <div style={{ marginTop: "1.5rem" }}>
          <h4>Extracted Page Concepts:</h4>
          <ul>
            {processedConcepts.map((c, i) => (
              <li key={i}>
                <strong>{c.name}</strong>: {c.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
