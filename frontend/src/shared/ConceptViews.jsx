import { Pill, ScoreBar, fmtDate } from "./ui";
import { byPage, groupConcepts } from "./conceptGroups";

const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;

function PageTag({ page }) {
  return page != null ? <span className="small nowrap"> · p. {page}</span> : null;
}

// One concept in the Weak Areas list: name + page, score, when it was tested, and why it is flagged.
function WeakRow({ c }) {
  const tested = c.event_count > 0;
  return (
    <div className="item">
      <div className="row" style={{ alignItems: "flex-start" }}>
        <div style={{ flex: 1, minWidth: 180 }}>
          <strong>{c.concept_name}</strong>
          <PageTag page={c.page_number} />
        </div>
        <div style={{ minWidth: 150, flex: 1 }}>
          {c.current_score != null ? <ScoreBar value={c.current_score} label={c.concept_name} /> : <span className="small">Flagged, not measured</span>}
          {tested && (
            <div className="small">
              Last tested {fmtDate(c.last_checked)} · {c.event_count === 1 ? "tested once" : `tested ${c.event_count} times`}
            </div>
          )}
        </div>
        {/* "Not enough data" only means there is no earlier score to compare with, so it is shown for a real trend only. */}
        {c.trend && c.trend !== "insufficient_data" && <Pill kind={c.trend} />}
      </div>
      {c.reason && <p className="small mb0 mt">Why: {c.reason}</p>}
    </div>
  );
}

// Weak / at-risk concepts grouped as subject -> chapter (book order) -> page order.
export function WeakConceptGroups({ concepts }) {
  return (
    <div className="stack">
      {groupConcepts(concepts).map((s) => (
        <div className="card mb0" key={s.subject}>
          <div className="row">
            <strong>{s.subject}</strong>
            <span className="small">{plural(s.count, "concept")}</span>
          </div>
          {s.chapters.map((ch) => (
            <details className="mt" key={ch.id} open>
              <summary>{ch.title} <span className="small">({plural(ch.concepts.length, "concept")})</span></summary>
              <div className="items mt">
                {ch.concepts.map((c) => <WeakRow key={c.concept_id} c={c} />)}
              </div>
            </details>
          ))}
        </div>
      ))}
    </div>
  );
}

// Every concept of one chapter with its page, status and latest score (used under a chapter in Analytics).
export function ChapterConcepts({ concepts }) {
  if (!concepts || concepts.length === 0) return null;
  return (
    <details className="mt">
      <summary>{plural(concepts.length, "concept")}</summary>
      <div className="items mt">
        {[...concepts].sort(byPage).map((c) => (
          <div className="item" key={c.concept_id}>
            <div className="row" style={{ alignItems: "center" }}>
              <div style={{ flex: 1, minWidth: 180 }}>
                <strong>{c.concept_name}</strong>
                <PageTag page={c.page_number} />
              </div>
              <div style={{ minWidth: 140, flex: 1 }}>
                {c.current_score != null ? <ScoreBar value={c.current_score} label={c.concept_name} /> : <span className="small">not measured</span>}
              </div>
              <Pill kind={c.status} />
            </div>
          </div>
        ))}
      </div>
    </details>
  );
}
