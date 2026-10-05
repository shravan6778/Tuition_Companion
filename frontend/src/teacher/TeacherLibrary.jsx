import React, { useState, useEffect } from "react";
import api from "../shared/api";
import NewBookWizard from "./NewBookWizard.jsx";
import WholeBookUpload from "./WholeBookUpload.jsx";
import ChapterRequests from "./ChapterRequests.jsx";
import {
  fetchBooks,
  bulkLinkBook,
  createChapter,
  uploadChapterPages,
  retryChapter,
  fetchChapterGraph,
  fetchVariantSuggestions,
  confirmVariant,
  clearVariant,
} from "../api/content";

// Convenience: link this book to every student in one of the teacher's single-class rooms.
function LinkToRoom({ book }) {
  const [rooms, setRooms] = useState([]);
  const [roomId, setRoomId] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    api
      .get("/teacher/rooms")
      .then((res) => setRooms((res.data || []).filter((r) => r.room_type === "single_class")))
      .catch(() => {});
  }, []);

  useEffect(() => setNote(""), [book.id]);

  if (rooms.length === 0) return null;

  async function link() {
    try {
      const r = await bulkLinkBook(roomId, book.id);
      setNote(
        `Linked for ${r.linked} student(s)` +
          (r.already_linked ? `, ${r.already_linked} already had it` : "") +
          `. Students who join later link it themselves.`,
      );
    } catch (err) {
      setNote(err.message);
    }
  }

  return (
    <p>
      <select value={roomId} onChange={(e) => setRoomId(e.target.value)}>
        <option value="">Link this book to all students in...</option>
        {rooms.map((r) => (
          <option key={r.id} value={r.id}>{r.name} ({r.member_count} students)</option>
        ))}
      </select>{" "}
      <button type="button" disabled={!roomId} onClick={link}>Link</button>{" "}
      <span style={{ color: "#444" }}>{note}</span>
    </p>
  );
}

function VariantBanner({ book, books, suggestions, onConfirm, onClear, onDismiss }) {
  const base = book.variant_of_id && books.find((b) => b.id === book.variant_of_id);
  const label = (b) => `${b.board} ${b.class_name} ${b.subject} (${b.publisher}${b.edition ? `, ${b.edition}` : ""})`;
  if (base) {
    return (
      <p style={{ background: "#eef6ff", padding: "0.5rem" }}>
        Marked as a customized version of <b>{label(base)}</b>.{" "}
        <button onClick={onClear}>Remove</button>
      </p>
    );
  }
  const s = suggestions[0];
  if (!s) return null;
  const percent = Math.round(s.coverage * 100);
  return (
    <div style={{ background: "#fff8e6", padding: "0.5rem", marginBottom: "1rem" }}>
      {s.kind === "same" ? (
        <p>
          {percent}% of your pages are nearly identical to <b>{label(s.book)}</b>
          {s.book.is_reference ? " (official)" : ""}. Students can link that book
          directly; you may not need your own copy.
        </p>
      ) : (
        <p>
          {percent}% of your pages match <b>{label(s.book)}</b>
          {s.book.is_reference ? " (official)" : ""}, with edits. Is this a
          customized version of it?
        </p>
      )}
      <button onClick={() => onConfirm(s.book.id)}>Yes, it's a variant of it</button>{" "}
      <button onClick={() => onDismiss(s.book.id)}>Not now</button>
    </div>
  );
}

function ConceptMap({ graph }) {
  const nameById = Object.fromEntries(graph.nodes.map((n) => [n.id, n.name]));
  const report = graph.report || {};
  const dropped = report.dropped_cycle_edges?.length || 0;
  const unresolved = report.unresolved_prerequisites?.length || 0;
  return (
    <div style={{ marginTop: "1rem" }}>
      <h4>Concept map ({graph.nodes.length} concepts)</h4>
      {graph.nodes.length === 0 ? (
        <p style={{ color: "#666" }}>No concepts were found in this chapter.</p>
      ) : (
        <ul>
          {graph.nodes.map((n) => {
            const needs = graph.edges
              .filter((e) => e.concept_id === n.id)
              .map((e) => nameById[e.prerequisite_id]);
            return (
              <li key={n.id}>
                {n.name}{" "}
                <small style={{ color: "#666" }}>(p. {n.pages.join(", ")})</small>
                {needs.length > 0 && (
                  <div style={{ fontSize: "0.85rem", color: "#444" }}>
                    needs: {needs.join(", ")}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
      {(dropped > 0 || unresolved > 0) && (
        <p style={{ fontSize: "0.85rem", color: "#a60" }}>
          {dropped > 0 && `${dropped} link(s) were skipped because they formed a loop. `}
          {unresolved > 0 &&
            `${unresolved} prerequisite(s) mentioned in the text don't match any concept in this chapter.`}
        </p>
      )}
    </div>
  );
}

export default function TeacherLibrary() {
  const [books, setBooks] = useState([]);
  const [selectedBookId, setSelectedBookId] = useState(null);
  const [selectedChapterId, setSelectedChapterId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [search, setSearch] = useState("");
  const [newChapterTitle, setNewChapterTitle] = useState("");
  const [graph, setGraph] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [dismissed, setDismissed] = useState([]); // base book ids hidden for this session

  const selectedBook = books.find((b) => b.id === selectedBookId) || null;
  const selectedChapter =
    selectedBook?.chapters?.find((c) => c.id === selectedChapterId) || null;
  const anyProcessing = !!selectedBook?.chapters?.some(
    (c) => c.status === "processing",
  );
  const referenceBooks = books.filter((b) => b.is_reference);
  const myBooks = books.filter((b) => !b.is_reference);

  useEffect(() => {
    const timer = setTimeout(loadBooks, search ? 250 : 0);
    return () => clearTimeout(timer);
  }, [search]);

  // Variant suggestions for the selected book (own books only), refreshed as chapters finish.
  const readyChapters = selectedBook?.chapters?.filter((c) => c.status === "ready").length || 0;
  useEffect(() => {
    setSuggestions([]);
    if (!selectedBook || selectedBook.is_reference || readyChapters === 0) return undefined;
    let cancelled = false;
    fetchVariantSuggestions(selectedBook.id)
      .then((list) => !cancelled && setSuggestions(list.filter((s) => !dismissed.includes(s.book.id))))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [selectedBook?.id, selectedBook?.variant_of_id, readyChapters, dismissed]);

  async function handleConfirmVariant(baseId) {
    try {
      await confirmVariant(selectedBook.id, baseId);
      await loadBooks();
      setStatusMessage("Saved. This book is now marked as a variant.");
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  async function handleClearVariant() {
    try {
      await clearVariant(selectedBook.id);
      await loadBooks();
    } catch (err) {
      setStatusMessage(`Error: ${err.message}`);
    }
  }

  // Load the concept map whenever a finished chapter is selected.
  useEffect(() => {
    setGraph(null);
    if (!selectedBook || !selectedChapter || selectedChapter.status !== "ready") {
      return undefined;
    }
    let cancelled = false;
    fetchChapterGraph(selectedBook.id, selectedChapter.id)
      .then((g) => !cancelled && setGraph(g))
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [selectedBook?.id, selectedChapter?.id, selectedChapter?.status]);

  // While a chapter is processing in the background, refresh every few seconds.
  useEffect(() => {
    if (!anyProcessing) return undefined;
    const timer = setInterval(loadBooks, 3000);
    return () => clearInterval(timer);
  }, [anyProcessing]);

  async function loadBooks() {
    try {
      setBooks(await fetchBooks(search.trim() ? { q: search.trim() } : {}));
    } catch (err) {
      setStatusMessage(`Couldn't load books: ${err.message}`);
    }
  }

  function selectBook(book) {
    setSelectedBookId(book.id);
    setSelectedChapterId(null);
  }

  async function handleBookCreated(created) {
    setSearch("");
    setBooks(await fetchBooks());
    setSelectedBookId(created.id);
    setSelectedChapterId(null);
    setStatusMessage("Book created. Upload the whole textbook, or add chapters one by one.");
  }

  function handleUseExisting(book) {
    setSearch("");
    setSelectedBookId(book.id);
    setSelectedChapterId(null);
    setStatusMessage("This book is already in the library. Link it to your students below - no upload needed.");
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

      <ChapterRequests refreshKey={books.length} />

      <NewBookWizard onCreated={handleBookCreated} onUseExisting={handleUseExisting} />

      <input
        placeholder="Search the library (e.g. 'class 9 science ncert')"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ width: "100%", maxWidth: "28rem", marginBottom: "1rem" }}
      />

      <div style={{ display: "flex", gap: "2rem" }}>
        <div style={{ width: "40%" }}>
          <h3>Official (reference) books</h3>
          {referenceBooks.length === 0 ? (
            <p style={{ color: "#666" }}>{search ? "No official books match." : "None loaded yet."}</p>
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
            {!selectedBook.is_reference && (
              <VariantBanner
                book={selectedBook}
                books={books}
                suggestions={suggestions}
                onConfirm={handleConfirmVariant}
                onClear={handleClearVariant}
                onDismiss={(id) => setDismissed((d) => [...d, id])}
              />
            )}
            <LinkToRoom book={selectedBook} />
            <ul>
              {selectedBook.chapters?.map((ch) => (
                <li
                  key={ch.id}
                  onClick={() => setSelectedChapterId(ch.id)}
                  style={{
                    cursor: selectedBook.is_reference ? "default" : "pointer",
                    fontWeight: selectedChapter?.id === ch.id ? "bold" : "normal",
                  }}
                >
                  Ch {ch.sequence_num}: {ch.title}
                  <span style={{ color: ch.status === "failed" ? "crimson" : "#666" }}>
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

            {graph && <ConceptMap graph={graph} />}

            {!selectedBook.is_reference && (
              <>
                <WholeBookUpload book={selectedBook} onDone={loadBooks} />
                <p style={{ marginTop: "1rem" }}>Or add a chapter at a time:</p>
                <form onSubmit={handleCreateChapter} style={{ marginTop: "1rem" }}>
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
                      disabled={uploading || selectedChapter.status === "processing"}
                    />
                    {selectedChapter.status === "processing" && (
                      <p>Processing OCR & concepts... this page refreshes by itself.</p>
                    )}
                    {selectedChapter.status === "ready" && (
                      <p style={{ color: "#666" }}>
                        Uploading a different file replaces this chapter's pages.
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
