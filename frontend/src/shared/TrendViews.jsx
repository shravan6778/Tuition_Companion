import { useState } from "react";
import { getTrends } from "../api/learning";
import { Async, Empty, Pill, ScoreBar, Sparkline, Tabs, signedPct, useLoad } from "./ui";
import { ChapterConcepts, WeakConceptGroups } from "./ConceptViews";

// Analytics (week-by-week scores by subject and chapter, with the concepts and their pages) and Weak Areas.
// Read-only views of one student's trends: the teacher's student page and the parent dashboard both use them.

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
// `fetchTrends(weeks)` lets another reader (a parent) feed the same view from its own route; the teacher's default is used otherwise.
export function ProgressTab({ studentId, fetchTrends }) {
  const [weeks, setWeeks] = useState(4);
  const state = useLoad(() => (fetchTrends ? fetchTrends(weeks) : getTrends(studentId, weeks)), [studentId, weeks]);
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
                      {s.chapters.map((c) => (
                        <div className="item" key={c.chapter_id}>
                          <TrendLine item={c} label={c.chapter_title} />
                          <ChapterConcepts concepts={t.concepts.filter((x) => x.chapter_id === c.chapter_id)} />
                        </div>
                      ))}
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
// `readOnly` is for a parent: no pointers to the teacher's assign / test tools.
export function WeakAreasTab({ studentId, fetchTrends, readOnly = false }) {
  const state = useLoad(() => (fetchTrends ? fetchTrends(8) : getTrends(studentId, 8)), [studentId]);
  const [view, setView] = useState("weak");
  return (
    <Async state={state}>
      {(t) => {
        const flagged = t.concepts.filter((c) => c.status !== "ok");
        const shown = flagged.filter((c) => c.status === view);
        return (
          <div className="stack">
            <Tabs value={view} onChange={setView} tabs={[["weak", `Weak (${t.weak_count})`], ["at_risk", `At risk (${t.at_risk_count})`]]} />
            {flagged.length === 0 && <div className="callout ok">No weak or at-risk ideas right now.</div>}
            {flagged.length > 0 && shown.length === 0 && <div className="card"><Empty>None in this group.</Empty></div>}
            {shown.length > 0 && <WeakConceptGroups concepts={shown} />}
            <p className="small mb0">
              {readOnly
                ? "Your child's teacher can set work on these ideas."
                : "To work on these, set an assignment or generate a test from the other tabs."}
            </p>
          </div>
        );
      }}
    </Async>
  );
}
