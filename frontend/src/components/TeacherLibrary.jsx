import React, { useState, useEffect } from "react";
import {
  fetchBooks,
  createBook,
  createChapter,
  uploadChapterPages,
  retryChapter,
} from "../api/content";

const EMPTY_BOOK = {
  board: "",
  class_name: "",
  subject: "",
  publisher: "",
  edition: "",
  school: "",
  is_customized: false,
};

export default function TeacherLibrary() {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(null);
  const [selectedChapterId, setSelectedChapterId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [newBook, setNewBook] = useState(EMPTY_BOOK);
  const [newChapterTitle, setNewChapterTitle] = useState("");

  const selectedBook = books.find((b) => b.id === selectedBookId) || null;
  const selectedChapter =
    selectedBook?.chapters?.find((c) => c.id === selectedChapterId) || null;
  const anyProcessing = !!selectedBook?.chapters?.some(
    (c) => c.status === "processing",
  );
  const referenceBooks = books.filter((b) => b.is_reference);
  const myBooks = books.filter((b) => !b.is_reference);

  useEffect(() => {
    loadBooks();
  }, []);

  // While a chapter is processing in the background, refresh every few seconds.
  useEffect(() => {
    if (!anyProcessing) return undefined;
    const timer = setInterval(loadBooks, 3000);
    return () => clearInterval(timer);
  }, [anyProcessing]);

  async function loadBooks() {
    try {
      setBooks(await fetchBooks());
    } catch (err) {
      setStatusMessage(`Couldn't load books: ${err.message}`);
    }
  }

  function selectBook(book) {
    setSelectedBookId(book.id);
    setSelectedChapterId(null);
  }

  async function handleCreateBook(e) {
    e.preventDefault();
    try {
      const body = {
        ...newBook,
        edition: newBook.edition.trim() || null,
        school: newBook.school.trim() || null,
      };
      const created = await createBook(body);
      await loadBooks();
      setSelectedBookId(created.id);
      setSelectedChapterId(null);
      setNewBook(EMPTY_BOOK);
      setStatusMessage("Book created. Add a chapter, then upload its pages.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleCreateChapter(e) {
    e.preventDefault();
    if (!selectedBook || !newChapterTitle.trim()) return;
    try {
      await createChapter(selectedBook.id, {
        title: newChapterTitle.trim(),
        sequence_num: (selectedBook.chapters?.length || 0) + 1,
      });
      await loadBooks(); // refetch so the chapter list stays correct when switching books
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
    setStatusMessage("Uploading...");
    try {
      const chapter = await uploadChapterPages(
        selectedBook.id,
        selectedChapter.id,
        file,
      );
      setStatusMessage(
        chapter.status === "ready"
          ? "This is the same file as before, so nothing needed to be redone."
          : "Upload received. Processing in the background - you can keep working.",
      );
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleRetry(chapter) {
    try {
      await retryChapter(selectedBook.id, chapter.id);
      setStatusMessage("Retrying...");
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Retry failed: ${err.message}`);
    }
  }

  const statusLabel = (ch) => {
    if (ch.status === "processing") return " - processing...";
    if (ch.status === "ready") return " - ready";
    if (ch.status === "failed") return " - failed";
    return " - no file yet";
  };

  const field = (key, placeholder, required = false) => (
    <input
      placeholder={placeholder}
      value={newBook[key]}
      onChange={(e) => setNewBook({ ...newBook, [key]: e.target.value })}
      required={required}
    />
  );

  const bookItem = (b) => (
    <li
      key={b.id}
      onClick={() => selectBook(b)}
      style={{
        cursor: "pointer",
        fontWeight: selectedBookId === b.id ? "bold" : "normal",
      }}
    >
      {b.board} - {b.class_name} - {b.subject} ({b.publisher}
      {b.edition ? `, ${b.edition}` : ""})
    </li>
  );

  return (
    <div style={{ padding: "1.5rem" }}>
      <h2>Content Library</h2>
      {statusMessage && <p style={{ color: "blue" }}>{statusMessage}</p>}

      <section
        style={{
          marginBottom: "2rem",
          border: "1px solid #ccc",
          padding: "1rem",
        }}
      >
        <h3>Add your own book</h3>
        <p style={{ fontSize: "0.85rem", color: "#666" }}>
          Official NCERT books are already in the library below. Add a book here
          only if it isn't listed (private publisher or school edition). It will
          be visible only to students in your rooms.
        </p>
        <form
          onSubmit={handleCreateBook}
          style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}
        >
          {field("board", "Board (e.g. ICSE)", true)}
          {field("class_name", "Class (e.g. Class 9)", true)}
          {field("subject", "Subject", true)}
          {field("publisher", "Publisher", true)}
          {field("edition", "Edition (optional)")}
          {field("school", "School (optional)")}
          <label>
            <input
              type="checkbox"
              checked={newBook.is_customized}
              onChange={(e) =>
                setNewBook({ ...newBook, is_customized: e.target.checked })
              }
            />{" "}
            School-customized edition
          </label>
          <button type="submit">Add Book</button>
        </form>
      </section>

      <div style={{ display: "flex", gap: "2rem" }}>
        <div style={{ width: "40%" }}>
          <h3>Official (reference) books</h3>
          {referenceBooks.length === 0 ? (
            <p style={{ color: "#666" }}>None loaded yet.</p>
          ) : (
            <ul>{referenceBooks.map(bookItem)}</ul>
          )}
          <h3>My books</h3>
          {myBooks.length === 0 ? (
            <p style={{ color: "#666" }}>You haven't added any books.</p>
          ) : (
            <ul>{myBooks.map(bookItem)}</ul>
          )}
        </div>

        {selectedBook && (
          <div style={{ width: "60%" }}>
            <h3>
              Chapters for {selectedBook.subject}
              {selectedBook.is_reference ? " (official, read-only)" : ""}
            </h3>
            <ul>
              {selectedBook.chapters?.map((ch) => (
                <li
                  key={ch.id}
                  onClick={() => setSelectedChapterId(ch.id)}
                  style={{
                    cursor: selectedBook.is_reference ? "default" : "pointer",
                    fontWeight:
                      selectedChapter?.id === ch.id ? "bold" : "normal",
                  }}
                >
                  Ch {ch.sequence_num}: {ch.title}
                  <span
                    style={{
                      color: ch.status === "failed" ? "crimson" : "#666",
                    }}
                  >
                    {statusLabel(ch)}
                  </span>
                  {ch.status === "failed" && (
                    <>
                      <div style={{ color: "crimson", fontSize: "0.85rem" }}>
                        {ch.error_message}
                      </div>
                      {!selectedBook.is_reference && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRetry(ch);
                          }}
                        >
                          Retry
                        </button>
                      )}
                    </>
                  )}
                </li>
              ))}
            </ul>

            {!selectedBook.is_reference && (
              <>
                <form
                  onSubmit={handleCreateChapter}
                  style={{ marginTop: "1rem" }}
                >
                  <input
                    placeholder="New chapter title"
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
                    <h4>Upload pages for {selectedChapter.title}</h4>
                    <input
                      type="file"
                      accept="application/pdf,image/*"
                      onChange={handleFileUpload}
                      disabled={
                        uploading || selectedChapter.status === "processing"
                      }
                    />
                    {selectedChapter.status === "processing" && (
                      <p>
                        Processing OCR & concepts... this page refreshes by
                        itself.
                      </p>
                    )}
                    {selectedChapter.status === "ready" && (
                      <p style={{ color: "#666" }}>
                        Uploading a different file replaces this chapter's
                        pages.
                      </p>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
