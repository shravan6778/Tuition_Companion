import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { askDoubt, getMastery, getMasteryEvents } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, Pill, ScoreBar, Sparkline, Tabs, fmtDate, fmtDateTime, pct, useLoad, useSubmit } from "../shared/ui";
import { DoubtResult } from "./DoubtBox";

const KIND = { check: "Micro-check", quiz: "Test", doubt: "Doubt asked", propagated: "Flagged" };

// Measured scores per concept, oldest first, from the append-only history. This is what makes it a trend, not a snapshot.
function scoreHistory(events) {
  const byConcept = new Map();
  for (const e of [...events].reverse()) {
    if (e.score == null || !e.concept_id) continue;
    if (!byConcept.has(e.concept_id)) byConcept.set(e.concept_id, []);
    byConcept.get(e.concept_id).push(e.score);
  }
  return byConcept;
}

function direction(h) {
  if (!h || h.length < 2) return null;
  const d = h[h.length - 1] - h[0];
  return d >= 0.1 ? "improving" : d <= -0.1 ? "declining" : "stable";
}

function ConceptRow({ c, history }) {
  const [doubt, setDoubt] = useState(null);
  const { busy, error, run } = useSubmit();
  const dir = direction(history);
  return (
    <div className="item">
      <div className="row" style={{ alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 200 }}>
          <strong>{c.concept_name}</strong>
          <div className="row gap-s" style={{ justifyContent: "flex-start", marginTop: 4 }}>
            <Pill kind={c.status} />
            {dir && <Pill kind={dir} />}
          </div>
        </div>
        <div style={{ minWidth: 150, flex: 1 }}>
          <ScoreBar value={c.score} label={c.concept_name} />
          {c.asked != null && <div className="small">{c.correct} of {c.asked} right last time{c.last_checked ? ` · ${fmtDate(c.last_checked)}` : ""}</div>}
        </div>
        <div><Sparkline points={history || []} width={110} /></div>
      </div>
      {c.reason && <p className="small mt mb0">Why: {c.reason}</p>}
      {c.status !== "ok" && (
        <div className="mt">
          <button className="btn secondary small-btn" disabled={busy} onClick={() => run(async () => setDoubt(await askDoubt({ concept_id: c.concept_id })))}>
            {busy ? "Looking..." : "Explain this to me"}
          </button>
        </div>
      )}
      <ErrorNote error={error} />
      {doubt && <div className="mt"><DoubtResult doubt={doubt} /></div>}
    </div>
  );
}

export default function Progress() {
  const state = useLoad(async () => {
    const [mastery, events] = await Promise.all([getMastery(), getMasteryEvents()]);
    return { mastery, events };
  });
  const [tab, setTab] = useState("weak");
  const history = useMemo(() => (state.data ? scoreHistory(state.data.events) : new Map()), [state.data]);

  return (
    <>
      <Header title="My Progress" subtitle="Every check and test you've done, and how each idea is trending." />
      <div className="container">
        <Async state={state}>
          {({ mastery, events }) => {
            if (mastery.concepts.length === 0 && events.length === 0) {
              return (
                <div className="card"><Empty>
                  <p><strong>Nothing to show yet.</strong></p>
                  <p className="mb0">Finish a check in <Link to="/student">Today's Work</Link> or take a <Link to="/student/practice">practice test</Link>, and your progress will appear here.</p>
                </Empty></div>
              );
            }
            const shown = mastery.concepts.filter((c) => (tab === "weak" ? c.status === "weak" : tab === "at_risk" ? c.status === "at_risk" : tab === "ok" ? c.status === "ok" : true));
            return (
              <>
                <div className="tiles">
                  <div className="tile weak"><div className="num">{mastery.weak}</div><div className="lbl">⚠ Weak ideas</div></div>
                  <div className="tile risk"><div className="num">{mastery.at_risk}</div><div className="lbl">◆ At risk</div></div>
                  <div className="tile ok"><div className="num">{mastery.ok}</div><div className="lbl">✓ On track</div></div>
                </div>

                {(mastery.weak > 0 || mastery.at_risk > 0) && (
                  <div className="callout risk mb0" style={{ marginBottom: 16 }}>
                    Ready to work on them? <Link to="/student/practice">Start a practice test</Link>, which leans toward your weak ideas.
                  </div>
                )}

                <Tabs value={tab} onChange={setTab} tabs={[
                  ["weak", `Weak areas (${mastery.weak})`], ["at_risk", `At risk (${mastery.at_risk})`], ["ok", `On track (${mastery.ok})`], ["all", "All"],
                ]} />
                <div className="card items">
                  {shown.length === 0 ? <Empty>Nothing in this group.</Empty> : shown.map((c) => <ConceptRow key={c.concept_id} c={c} history={history.get(c.concept_id)} />)}
                </div>

                <h2 className="mt">History</h2>
                <div className="card items">
                  {events.length === 0 ? <Empty>No events yet.</Empty> : events.slice(0, 40).map((e) => (
                    <div className="item row" key={e.id}>
                      <div><strong>{e.concept_name}</strong><div className="small">{KIND[e.kind] || e.kind} · {fmtDateTime(e.created_at)}{e.reason ? ` · ${e.reason}` : ""}</div></div>
                      {e.score != null && <Pill kind={e.score < 0.6 ? "weak" : "ok"}>{pct(e.score)} ({e.correct}/{e.asked})</Pill>}
                    </div>
                  ))}
                </div>
              </>
            );
          }}
        </Async>
      </div>
    </>
  );
}
