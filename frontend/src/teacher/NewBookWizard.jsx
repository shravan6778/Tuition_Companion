import React, { useState } from "react";
import { uploadFrontPages, createBook } from "../api/content";

const EMPTY = {
  board: "",
  class_name: "",
  subject: "",
  publisher: "",
  edition: "",
  school: "",
  is_customized: false,
};

const label = (b) =>
  `${b.board} ${b.class_name} ${b.subject} (${b.publisher}${b.edition ? `, ${b.edition}` : ""})`;

// Add a book: front pages first (cover + publisher/edition page) so the system can read the details
// and tell the teacher if an official book already matches. Manual entry stays as a fallback.
export default function NewBookWizard({ onCreated, onUseExisting }) {
  const [form, setForm] = useState(EMPTY);
  const [draft, setDraft] = useState(null); // { draft_id, matches }
  const [manual, setManual] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [warn, setWarn] = useState(false); // the message is a warning (nothing could be read), shown in orange

  const showForm = manual || draft;

  async function handleFront(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setMessage("Reading the front pages...");
    try {
      const d = await uploadFrontPages(file);
      const m = d.metadata;
      setForm({
        board: m.board || "",
        class_name: m.class_name || "",
        subject: m.subject || "",
        publisher: m.publisher || "",
        edition: m.edition || "",
        school: m.school || "",
        is_customized: !!m.is_customized,
      });
      setDraft({ draft_id: d.draft_id, matches: d.matches });
      setWarn(!!d.warning);
      setMessage(
        d.warning
          ? `${d.warning} The form below is empty: fill it in by hand.`
          : d.matches.length
            ? "We found books that already match. Check them before creating a new one."
            : "Check the details below, fix anything that's wrong, then create the book.",
      );
    } catch (err) {
      setWarn(false);
      setMessage(err.message);
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const created = await createBook({
        ...form,
        edition: form.edition.trim() || null,
        school: form.school.trim() || null,
        draft_id: draft?.draft_id || null,
      });
      setForm(EMPTY);
      setDraft(null);
      setManual(false);
      setMessage("");
      await onCreated(created);
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  function cancel() {
    setForm(EMPTY);
    setDraft(null);
    setManual(false);
    setMessage("");
  }

  const field = (key, placeholder, required = false) => (
    <input
      placeholder={placeholder}
      value={form[key]}
      onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      required={required}
    />
  );

  return (
    <section style={{ marginBottom: "2rem", border: "1px solid #ccc", padding: "1rem" }}>
      <h3>Add a book</h3>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Official NCERT books are already in the library below; you can link them to your
        students without uploading anything. Add a book here only if it isn't listed (private
        publisher or school edition). It will be visible only to students in your rooms.
      </p>

      {!showForm && (
        <>
          <label>
            <b>1. Upload the cover and publisher/edition pages</b> (PDF or photo, a few pages)
            <br />
            <input type="file" accept="application/pdf,image/*" onChange={handleFront} disabled={busy} />
          </label>
          <p>
            <button type="button" onClick={() => setManual(true)}>
              I don't have these pages - enter the details by hand
            </button>
          </p>
        </>
      )}

      {message && <p style={{ color: warn ? "#b45f06" : "blue" }}>{message}</p>}

      {draft?.matches?.length > 0 && (
        <div style={{ background: "#eef6ff", padding: "0.5rem", marginBottom: "0.75rem" }}>
          <b>Already in the library:</b>
          <ul>
            {draft.matches.map((b) => (
              <li key={b.id}>
                {label(b)}
                {b.is_reference ? " - official" : " - yours"}{" "}
                <button type="button" onClick={() => { cancel(); onUseExisting(b); }}>
                  Use this one
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {field("board", "Board (e.g. ICSE)", true)}
          {field("class_name", "Class (e.g. Class 9)", true)}
          {field("subject", "Subject", true)}
          {field("publisher", "Publisher", true)}
          {field("edition", "Edition (optional)")}
          {field("school", "School (optional)")}
          <label>
            <input
              type="checkbox"
              checked={form.is_customized}
              onChange={(e) => setForm({ ...form, is_customized: e.target.checked })}
            />{" "}
            School-customized edition
          </label>
          <button type="submit" disabled={busy}>
            {draft ? "Looks right - create book" : "Create book"}
          </button>
          <button type="button" onClick={cancel}>
            Cancel
          </button>
        </form>
      )}
    </section>
  );
}
