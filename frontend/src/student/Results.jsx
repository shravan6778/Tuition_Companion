import { Link } from "react-router-dom";
import { Pill, ScoreBar } from "../shared/ui";

// What a finished check or quiz says: per-concept result, and which dependent concepts it put at risk (with the reason).
export default function Results({ concepts, atRisk }) {
  if (!concepts?.length && !atRisk?.length) return null;
  return (
    <div className="stack">
      {concepts?.length > 0 && (
        <div className="card mb0">
          <h3>How each idea went</h3>
          <div className="items">
            {concepts.map((c, i) => (
              <div className="item" key={`${c.concept_id}-${i}`}>
                <div className="row">
                  <strong>{c.concept_name}</strong>
                  <span className="row gap-s">
                    <span className="small">{c.correct} of {c.asked} right</span>
                    <Pill kind={c.weak ? "weak" : "ok"} />
                  </span>
                </div>
                <ScoreBar value={c.score} label={c.concept_name} />
              </div>
            ))}
          </div>
        </div>
      )}
      {atRisk?.length > 0 && (
        <div className="callout risk">
          <strong>These may need a look too</strong>
          <ul>
            {atRisk.map((a, i) => <li key={`${a.concept_id}-${i}`}><strong>{a.concept_name}</strong>: {a.reason}</li>)}
          </ul>
        </div>
      )}
      <p className="small mb0">See all of this over time in <Link to="/student/progress">My Progress</Link>.</p>
    </div>
  );
}
