import { useState } from "react";
import { addSession, getBriefing, listSessions } from "../api/learning";
import { Async, Empty, ErrorNote, fmtDate, fmtDateTime, useLoad, useSubmit } from "../shared/ui";

// Analytics and Weak Areas live in shared/ so the parent dashboard can show the same views.
export { ProgressTab, WeakAreasTab } from "../shared/TrendViews";

// ---- Briefing: a short pre-session summary written from the student's history and the teacher's notes ----
export function BriefingTab({ studentId }) {
  const state = useLoad(() => getBriefing(studentId), [studentId]);
  const { busy, error, run } = useSubmit();
  const [fresh, setFresh] = useState(null);
  const b = fresh || state.data;
  return (
    <Async state={state}>
      {() => (
        <div className="stack">
          <div className="tiles mb0">
            <div className="tile weak"><div className="num">{b.weak_count}</div><div className="lbl">⚠ Weak</div></div>
            <div className="tile risk"><div className="num">{b.at_risk_count}</div><div className="lbl">◆ At risk</div></div>
            <div className="tile ok"><div className="num">{b.improving_count}</div><div className="lbl">↑ Improving</div></div>
            <div className="tile"><div className="num">{b.declining_count}</div><div className="lbl">↓ Declining</div></div>
          </div>
          <div className="card mb0"><h3>Last covered</h3><p className="pre mb0">{b.last_covered}</p></div>
          <div className="card mb0"><h3>Weak areas</h3><p className="pre mb0">{b.weak_areas}</p></div>
          <div className="card mb0">
            <h3>Suggested focus for the next session</h3>
            <p className="pre">{b.suggested_focus}</p>
            {b.focus_concepts.length > 0 && <div className="chips">{b.focus_concepts.map((c) => <span className="chip" key={c}>{c}</span>)}</div>}
          </div>
          {b.model === "fake" && <div className="callout warn">This briefing came from the placeholder test model, not a real one. Set LLM_PROVIDER in the backend settings.</div>}
          <ErrorNote error={error} />
          <div className="row">
            <span className="small">Based on {b.recent_session_count} recent session note{b.recent_session_count === 1 ? "" : "s"} · {b.cached ? "saved" : "new"} briefing from {fmtDateTime(b.generated_at)}</span>
            <button className="btn secondary small-btn" disabled={busy} onClick={() => run(async () => setFresh(await getBriefing(studentId, true)))}>
              {busy ? "Writing..." : "Write a fresh briefing"}
            </button>
          </div>
        </div>
      )}
    </Async>
  );
}

// ---- Session log: what was covered, so the next briefing can use it ----
export function SessionLogTab({ studentId }) {
  const state = useLoad(() => listSessions(studentId), [studentId]);
  const [notes, setNotes] = useState("");
  const [tags, setTags] = useState("");
  const [date, setDate] = useState("");
  const { busy, error, run } = useSubmit();
  const save = (e) => {
    e.preventDefault();
    run(async () => {
      await addSession(studentId, {
        notes: notes.trim(), session_date: date || undefined,
        tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      });
      setNotes(""); setTags(""); setDate("");
      state.reload();
    });
  };
  return (
    <div className="stack">
      <form className="card stack mb0" onSubmit={save}>
        <h3>Log a session</h3>
        <div>
          <label htmlFor="sl-notes">What did you cover? How did it go?</label>
          <textarea id="sl-notes" className="input" required maxLength={4000} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>
        <div className="grid2">
          <div><label htmlFor="sl-tags">Tags (comma separated)</label><input id="sl-tags" className="input" value={tags} placeholder="fractions, revision" onChange={(e) => setTags(e.target.value)} /></div>
          <div><label htmlFor="sl-date">Date (defaults to today)</label><input id="sl-date" type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} /></div>
        </div>
        <ErrorNote error={error} />
        <div><button className="btn" disabled={busy || !notes.trim()}>{busy ? "Saving..." : "Save session"}</button></div>
      </form>
      <Async state={state}>
        {(list) => list.length === 0 ? <div className="card"><Empty>No sessions logged yet.</Empty></div> : (
          <div className="card items mb0">
            {list.map((s) => (
              <div className="item" key={s.id}>
                <strong>{fmtDate(s.session_date)}</strong>
                <p className="pre mb0">{s.notes}</p>
                {s.tags.length > 0 && <div className="chips mt">{s.tags.map((t) => <span className="chip" key={t}>{t}</span>)}</div>}
              </div>
            ))}
          </div>
        )}
      </Async>
    </div>
  );
}
