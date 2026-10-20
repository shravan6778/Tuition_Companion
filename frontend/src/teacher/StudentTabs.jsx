import { useState } from "react";
import { addSession, getBriefing, getTrends, listSessions } from "../api/learning";
import { Async, Empty, ErrorNote, Pill, ScoreBar, Sparkline, Tabs, fmtDate, fmtDateTime, signedPct, useLoad, useSubmit } from "../shared/ui";

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

const weekPoints = (weeks) => weeks.map((w) => w.average_score);

function TrendLine({ item, label }) {
  return (
    <div className="row" style={{ alignItems: "center" }}>
      <div style={{ flex: 1, minWidth: 180 }}>
        <strong>{label}</strong>
        <div className="row gap-s" style={{ justifyContent: "flex-start", marginTop: 4 }}>
          <Pill kind={item.trend} />
          {item.delta != null && <span className="small">{signedPct(item.delta)} vs earlier</span>}
        </div>
      </div>
      <div style={{ minWidth: 140, flex: 1 }}>
        <ScoreBar value={item.current_average} label={label} />
        <div className="small">Latest weeks' average</div>
      </div>
      <Sparkline points={weekPoints(item.weeks)} width={120} />
    </div>
  );
}

// ---- Analytics / progress: how scores moved week by week, by subject and chapter ----
export function ProgressTab({ studentId }) {
  const [weeks, setWeeks] = useState(4);
  const state = useLoad(() => getTrends(studentId, weeks), [studentId, weeks]);
  return (
    <div className="stack">
      <div className="row">
        <p className="small mb0">Each dot is one week's average score on checks and tests. The dashed line is the 60% weak line.</p>
        <div>
          <label htmlFor="wk" className="small">Show</label>
          <select id="wk" className="input" style={{ minWidth: 130 }} value={weeks} onChange={(e) => setWeeks(Number(e.target.value))}>
            {[4, 8, 12].map((w) => <option key={w} value={w}>Last {w} weeks</option>)}
          </select>
        </div>
      </div>
      <Async state={state}>
        {(t) => (
          <>
            <div className="tiles mb0">
              <div className="tile weak"><div className="num">{t.weak_count}</div><div className="lbl">⚠ Weak</div></div>
              <div className="tile risk"><div className="num">{t.at_risk_count}</div><div className="lbl">◆ At risk</div></div>
              <div className="tile ok"><div className="num">{t.ok_count}</div><div className="lbl">✓ On track</div></div>
              <div className="tile"><div className="num">{t.improving_count}</div><div className="lbl">↑ Improving</div></div>
              <div className="tile"><div className="num">{t.declining_count}</div><div className="lbl">↓ Declining</div></div>
              <div className="tile"><div className="num">{t.stable_count}</div><div className="lbl">→ Stable</div></div>
            </div>
            {t.subjects.length === 0 ? <div className="card"><Empty>No checks or tests yet, so there is no trend to show.</Empty></div> : t.subjects.map((s) => (
              <div className="card mb0" key={s.subject}>
                <TrendLine item={s} label={s.subject} />
                {s.chapters.length > 0 && (
                  <details className="mt">
                    <summary>{s.chapters.length} chapter{s.chapters.length > 1 ? "s" : ""}</summary>
                    <div className="items mt">
                      {s.chapters.map((c) => <div className="item" key={c.chapter_id}><TrendLine item={c} label={c.chapter_title} /></div>)}
                    </div>
                  </details>
                )}
              </div>
            ))}
          </>
        )}
      </Async>
    </div>
  );
}

// ---- Weak area detection: which ideas are weak or at risk, and why ----
export function WeakAreasTab({ studentId }) {
  const state = useLoad(() => getTrends(studentId, 8), [studentId]);
  const [view, setView] = useState("weak");
  return (
    <Async state={state}>
      {(t) => {
        const flagged = t.concepts.filter((c) => c.status !== "ok");
        const shown = flagged.filter((c) => c.status === view);
        const order = (a, b) => (a.current_score ?? 1) - (b.current_score ?? 1);
        return (
          <div className="stack">
            <Tabs value={view} onChange={setView} tabs={[["weak", `Weak (${t.weak_count})`], ["at_risk", `At risk (${t.at_risk_count})`]]} />
            {flagged.length === 0 && <div className="callout ok">No weak or at-risk ideas right now.</div>}
            {flagged.length > 0 && shown.length === 0 && <div className="card"><Empty>None in this group.</Empty></div>}
            {shown.length > 0 && (
              <div className="card items mb0">
                {[...shown].sort(order).map((c) => (
                  <div className="item" key={c.concept_id}>
                    <div className="row" style={{ alignItems: "flex-start" }}>
                      <div style={{ flex: 1, minWidth: 180 }}>
                        <strong>{c.concept_name}</strong>
                        <div className="small">{[c.subject, c.chapter_title].filter(Boolean).join(" · ")}</div>
                      </div>
                      <div style={{ minWidth: 150, flex: 1 }}>
                        {c.current_score != null ? <ScoreBar value={c.current_score} label={c.concept_name} /> : <span className="small">Flagged, not measured</span>}
                        {c.last_checked && <div className="small">Last tested {fmtDate(c.last_checked)} · {c.event_count} result{c.event_count === 1 ? "" : "s"}</div>}
                      </div>
                      <Pill kind={c.trend} />
                    </div>
                    {c.reason && <p className="small mb0 mt">Why: {c.reason}</p>}
                  </div>
                ))}
              </div>
            )}
            <p className="small mb0">To work on these, set an assignment or generate a test from the other tabs.</p>
          </div>
        );
      }}
    </Async>
  );
}
