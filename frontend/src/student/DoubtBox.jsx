import { useState } from "react";
import { Link } from "react-router-dom";
import { askDoubt, askDoubtPhoto, postPath } from "../api/learning";
import { ErrorNote, useSubmit } from "../shared/ui";

const NOTE_BY_STATUS = {
  grounded: "ok",
  outside_assignment: "risk",
  not_in_book: "warn",
  unavailable: "warn",
};

// Ask the teacher to add a chapter that the book is missing (only offered when a doubt wasn't found in the book).
function RequestChapter({ request }) {
  const [hint, setHint] = useState("");
  const [sent, setSent] = useState(false);
  const { busy, error, run } = useSubmit();
  if (sent) return <p className="small mb0">Sent. Your teacher will see this request.</p>;
  return (
    <form
      className="stack"
      onSubmit={(e) => {
        e.preventDefault();
        run(async () => {
          await postPath(request.path, { chapter_hint: hint });
          setSent(true);
        });
      }}
    >
      <label htmlFor="req-hint">Which chapter should your teacher add?</label>
      <div className="row gap-s" style={{ flexWrap: "nowrap" }}>
        <input id="req-hint" className="input" value={hint} minLength={3} maxLength={200} required
          placeholder="e.g. Chapter 5 - Force and Laws of Motion" onChange={(e) => setHint(e.target.value)} />
        <button className="btn" disabled={busy}>Ask teacher</button>
      </div>
      <ErrorNote error={error} />
    </form>
  );
}

// One answered doubt: the explanation first, then where it comes from and what to revise.
export function DoubtResult({ doubt }) {
  const tone = NOTE_BY_STATUS[doubt.status] || "info";
  return (
    <div className="stack">
      <div className={`callout ${tone}`}>
        <strong>{doubt.message}</strong>
        {doubt.note && <div className="small">Auto-generated, please verify with your book or teacher.</div>}
      </div>

      {doubt.answer && (
        <div className="card mb0">
          <h3>Explanation</h3>
          <p className="pre">{doubt.answer}</p>
          {doubt.refresher && (
            <div className="callout info">
              <strong>Quick refresher</strong>
              <p className="pre mb0">{doubt.refresher}</p>
            </div>
          )}
          {doubt.sources.length > 0 && (
            <p className="small mb0 mt">
              From {doubt.sources.map((s) => `page ${s.page_number} (${s.chapter_title})`).join(", ")}
            </p>
          )}
        </div>
      )}

      {doubt.prerequisites.length > 0 && (
        <div>
          <h3>Revise these first</h3>
          <div className="chips">
            {doubt.prerequisites.map((p) => <span className="chip" key={p.concept_id}>{p.name}</span>)}
          </div>
        </div>
      )}

      {doubt.pages.length > 0 && (
        <details>
          <summary>Pages in your book that match ({doubt.pages.length})</summary>
          <div className="items mt">
            {doubt.pages.map((p) => (
              <div className="item" key={p.page_id}>
                <strong>Page {p.page_number}</strong> <span className="small">{p.chapter_title}</span>
                <p className="small pre mb0">{p.excerpt}</p>
              </div>
            ))}
          </div>
        </details>
      )}

      {doubt.elsewhere.length > 0 && (
        <p className="small">Also covered elsewhere in your books: {doubt.elsewhere.map((e) => e.name).join(", ")}.</p>
      )}

      {doubt.request_chapter && <RequestChapter request={doubt.request_chapter} />}
    </div>
  );
}

// The doubt form. Pass assignmentId (a doubt on one task) or chapterId (a doubt inside one chapter), never both.
export default function DoubtBox({ assignmentId, chapterId, onAsked }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null); // { doubt } | { page, message } | { message }
  const { busy, error, run } = useSubmit();
  const scope = { assignment_id: assignmentId || undefined, chapter_id: chapterId || undefined };

  const ask = (e) => {
    e.preventDefault();
    run(async () => {
      const doubt = await askDoubt({ text, ...scope });
      setResult({ doubt });
      setText("");
      onAsked?.();
    });
  };

  const photo = (file) => {
    if (!file) return;
    run(async () => {
      const res = await askDoubtPhoto(file, { assignmentId, chapterId });
      if (res.kind === "doubt" && res.doubt) {
        setResult({ doubt: res.doubt });
        onAsked?.();
      } else {
        setResult({ photo: res });
      }
    });
  };

  const pickConcept = (conceptId) =>
    run(async () => {
      setResult({ doubt: await askDoubt({ concept_id: conceptId, ...scope }) });
      onAsked?.();
    });

  const p = result?.photo;
  return (
    <div className="stack">
      <form className="stack" onSubmit={ask}>
        <label htmlFor={`doubt-${assignmentId || chapterId || "any"}`}>What is confusing you?</label>
        <textarea id={`doubt-${assignmentId || chapterId || "any"}`} className="input" value={text} maxLength={1000}
          placeholder="Write it the way you would say it to your teacher" onChange={(e) => setText(e.target.value)} />
        <div className="row gap-s">
          <button className="btn" disabled={busy || !text.trim()}>{busy ? "Looking in your book..." : "Ask doubt"}</button>
          <label className="btn secondary" style={{ marginBottom: 0 }}>
            Photograph it
            <input type="file" accept="image/*" capture="environment" hidden disabled={busy}
              onChange={(e) => { photo(e.target.files?.[0]); e.target.value = ""; }} />
          </label>
        </div>
      </form>
      <ErrorNote error={error} />

      {result?.doubt && <DoubtResult doubt={result.doubt} />}

      {p && (
        <div className="stack">
          <div className={`callout ${p.kind === "page" && p.page ? "info" : "warn"}`}>
            {p.message}
            {p.text_read && <div className="small">We read: "{p.text_read}"</div>}
          </div>
          {p.page && (
            <div>
              <h3>Which idea on page {p.page.page_number} confused you?</h3>
              <div className="stack">
                {p.page.concepts.map((c) => (
                  <button key={c.concept_id} type="button" className="opt" disabled={busy} onClick={() => pickConcept(c.concept_id)}>
                    <span><strong>{c.name}</strong>{c.description && <span className="small"> {c.description}</span>}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          {p.request_chapter && <RequestChapter request={p.request_chapter} />}
          {p.kind === "unavailable" && <p className="small">Type your doubt instead, or <Link to="/student/books">check your books</Link>.</p>}
        </div>
      )}
    </div>
  );
}
