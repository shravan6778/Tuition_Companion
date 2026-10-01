import React, { useState, useEffect } from "react";
import {
  fetchBooks,
  createBook,
  createChapter,
  uploadChapterPages,
} from "../api/content";

export default function TeacherLibrary() {
  const [books, setBooks] = useState([]);
  const [selectedBook, setSelectedBook] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");

  const [newBook, setNewBook] = useState({
    board: "CBSE",
    class_name: "Class 10",
    subject: "Science",
    publisher: "NCERT",
    edition: "2026",
    is_customized: false,
  });

  const [newChapterTitle, setNewChapterTitle] = useState("");

  useEffect(() => {
    loadBooks();
  }, []);

  async function loadBooks() {
    try {
      const data = await fetchBooks();
      setBooks(data);
    } catch (err) {
      console.error(err);
    }
  }

  async function handleCreateBook(e) {
    e.preventDefault();
    try {
      const created = await createBook(newBook);
      setBooks([...books, created]);
      setSelectedBook(created);
      setStatusMessage("Book created successfully.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleCreateChapter(e) {
    e.preventDefault();
    if (!selectedBook || !newChapterTitle.trim()) return;
    try {
      const ch = await createChapter(selectedBook.id, {
        title: newChapterTitle,
        sequence_num: (selectedBook.chapters?.length || 0) + 1,
      });
      const updated = {
        ...selectedBook,
        chapters: [...(selectedBook.chapters || []), ch],
      };
      setSelectedBook(updated);
      setNewChapterTitle("");
      setStatusMessage("Chapter added.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file || !selectedBook || !selectedChapter) return;
    setUploading(true);
    setStatusMessage("Extracting layout & processing pages...");
    try {
      const result = await uploadChapterPages(
        selectedBook.id,
        selectedChapter.id,
        file,
      );
      setStatusMessage(
        `Uploaded and processed ${result.length} verified pages.`,
      );
    } catch (err) {
      setStatusMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Teacher Content Library</h2>
      {statusMessage && <p style={{ color: "blue" }}>{statusMessage}</p>}

      {/* New Book Form */}
      <section
        style={{
          marginBottom: "2rem",
          border: "1px solid #ccc",
          padding: "1rem",
        }}
      >
        <h3>Create New Book</h3>
        <form
          onSubmit={handleCreateBook}
          style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}
        >
          <input
            placeholder="Board (e.g. CBSE)"
            value={newBook.board}
            onChange={(e) => setNewBook({ ...newBook, board: e.target.value })}
            required
          />
          <input
            placeholder="Class (e.g. Class 10)"
            value={newBook.class_name}
            onChange={(e) =>
              setNewBook({ ...newBook, class_name: e.target.value })
            }
            required
          />
          <input
            placeholder="Subject"
            value={newBook.subject}
            onChange={(e) =>
              setNewBook({ ...newBook, subject: e.target.value })
            }
            required
          />
          <input
            placeholder="Publisher (e.g. NCERT)"
            value={newBook.publisher}
            onChange={(e) =>
              setNewBook({ ...newBook, publisher: e.target.value })
            }
            required
          />
          <button type="submit">Add Book</button>
        </form>
      </section>

      {/* Book & Chapter Management */}
      <div style={{ display: "flex", gap: "2rem" }}>
        <div style={{ width: "40%" }}>
          <h3>Textbooks</h3>
          <ul>
            {books.map((b) => (
              <li
                key={b.id}
                onClick={() => {
                  setSelectedBook(b);
                  setSelectedChapter(null);
                }}
                style={{
                  cursor: "pointer",
                  fontWeight: selectedBook?.id === b.id ? "bold" : "normal",
                }}
              >
                {b.board} - {b.class_name} - {b.subject} ({b.publisher})
              </li>
            ))}
          </ul>
        </div>

        {selectedBook && (
          <div style={{ width: "60%" }}>
            <h3>Chapters for {selectedBook.subject}</h3>
            <ul>
              {selectedBook.chapters?.map((ch) => (
                <li
                  key={ch.id}
                  onClick={() => setSelectedChapter(ch)}
                  style={{
                    cursor: "pointer",
                    fontWeight:
                      selectedChapter?.id === ch.id ? "bold" : "normal",
                  }}
                >
                  Ch {ch.sequence_num}: {ch.title}
                </li>
              ))}
            </ul>

            <form onSubmit={handleCreateChapter} style={{ marginTop: "1rem" }}>
              <input
                placeholder="New Chapter Title"
                value={newChapterTitle}
                onChange={(e) => setNewChapterTitle(e.target.value)}
                required
              />
              <button type="submit">Add Chapter</button>
            </form>

            {selectedChapter && (
              <div
                style={{
                  marginTop: "1.5rem",
                  padding: "1rem",
                  backgroundColor: "#f9f9f9",
                }}
              >
                <h4>Upload Document for {selectedChapter.title}</h4>
                <p style={{ fontSize: "0.85rem", color: "#666" }}>
                  Deliberate upload: Ingests pages as verified reference
                  content.
                </p>
                <input
                  type="file"
                  accept="application/pdf,image/*"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
                {uploading && <p>Processing OCR & Concept Graphs...</p>}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
