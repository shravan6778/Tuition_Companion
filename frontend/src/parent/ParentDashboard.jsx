import { useState } from "react";
import { getChildProgress, linkChild, listChildren } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, Pill, fmtDateTime, pct, useLoad, useSubmit } from "../shared/ui";

const KIND = { check: "Micro-check", quiz: "Test", propagated: "Flagged" };

function Progress({ child }) {
  const [days, setDays] = useState(7);
  const state = useLoad(() => getChildProgress(child.id, days), [child.id, days]);
  return (
    <div className="stack">
      <div className="row">
        <span className="small">{child.rooms.length ? `In ${child.rooms.map((r) => r.name).join(", ")}` : "Not in any room yet"}</span>
        <div>
          <label htmlFor={`d-${child.id}`} className="small">Digest for</label>
          <select id={`d-${child.id}`} className="input" style={{ minWidth: 140 }} value={days} onChange={(e) => setDays(Number(e.target.value))}>
            {[7, 14, 30].map((d) => <option key={d} value={d}>Last {d} days</option>)}
          </select>
        </div>
      </div>
      <Async state={state}>
        {(p) => (
          <>
            <div className="tiles mb0">
              <div className="tile"><div className="num">{p.digest.concepts_covered}</div><div className="lbl">Ideas practised</div></div>
              <div className="tile"><div className="num">{p.digest.checks_taken}</div><div className="lbl">Micro-checks</div></div>
              <div className="tile"><div className="num">{p.digest.quizzes_taken}</div><div className="lbl">Tests</div></div>
              <div className="tile ok"><div className="num">{pct(p.digest.pass_rate)}</div><div className="lbl">Pass rate</div></div>
            </div>
            {p.digest.pass_rate == null && <p className="small mb0">No checks or tests in this period yet.</p>}

            {p.digest.flagged_this_week.length > 0 && (
              <div className="callout risk">
                <strong>Flagged in this period</strong>
                <div className="chips mt">{p.digest.flagged_this_week.map((n) => <span className="chip" key={n}>{n}</span>)}</div>
              </div>
            )}

            <div className="card mb0">
              <h3>Areas to support ({p.weak + p.at_risk})</h3>
              {p.weak_areas.length === 0 ? <div className="callout ok">No weak or at-risk ideas right now.</div> : (
                <div className="items">
                  {p.weak_areas.map((c) => (
                    <div className="item" key={c.concept_name}>
                      <div className="row"><strong>{c.concept_name}</strong><span className="row gap-s">{c.score != null && <span className="small">{pct(c.score)}</span>}<Pill kind={c.status} /></span></div>
                      {c.reason && <div className="small">{c.reason}</div>}
                    </div>
                  ))}
                </div>
              )}
              <p className="small mb0 mt">{p.ok} idea{p.ok === 1 ? "" : "s"} on track.</p>
            </div>

            {p.recent.length > 0 && (
              <details>
                <summary>Recent results</summary>
                <div className="items mt">
                  {p.recent.map((e, i) => (
                    <div className="item row" key={i}>
                      <div><strong>{e.concept_name}</strong><div className="small">{KIND[e.kind] || e.kind} · {fmtDateTime(e.created_at)}</div></div>
                      {e.score != null && <Pill kind={e.score < 0.6 ? "weak" : "ok"}>{pct(e.score)}</Pill>}
                    </div>
                  ))}
                </div>
              </details>
            )}
          </>
        )}
      </Async>
    </div>
  );
}

export default function ParentDashboard() {
  const state = useLoad(listChildren);
  const [code, setCode] = useState("");
  const { busy, error, run } = useSubmit();

  const link = (e) => {
    e.preventDefault();
    run(async () => { await linkChild(code.trim()); setCode(""); state.reload(); });
  };

  return (
    <>
      <Header title="My children" subtitle="A read-only view of how they're getting on. You can't change anything here." />
      <div className="container">
        <Async state={state}>
          {(children) => (
            <>
              {children.length === 0 && <div className="card"><Empty><p><strong>No children linked yet.</strong></p><p className="mb0">Ask your child for the link code on their My Books page and enter it below.</p></Empty></div>}
              {children.map((c) => (
                <section className="card" key={c.id} aria-label={c.name}>
                  <h2>{c.name}</h2>
                  <Progress child={c} />
                </section>
              ))}
              <form className="card stack" onSubmit={link}>
                <h3>Link a student</h3>
                <label htmlFor="lc">Link code (from your child's My Books page)</label>
                <input id="lc" className="input" value={code} onChange={(e) => setCode(e.target.value)} required minLength={4} maxLength={12} />
                <ErrorNote error={error} />
                <div><button className="btn" disabled={busy}>{busy ? "Linking..." : "Link student"}</button></div>
              </form>
            </>
          )}
        </Async>
      </div>
    </>
  );
}
