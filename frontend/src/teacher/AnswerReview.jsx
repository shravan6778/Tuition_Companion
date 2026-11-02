import { useState } from "react";
import { confirmAnswer, overrideAnswer } from "../api/learning";
import WrittenResult from "../shared/WrittenResult";
import { Async, ErrorNote, Pill, fmtDateTime, pct, useLoad, useSubmit } from "../shared/ui";

// One written or spoken answer with the teacher's controls: confirm a held transcript, or override the AI's suggestion.
function AnswerRow({ kind, a, onChanged }) {
  const [hit, setHit] = useState(() => new Set((a.rubric || []).flatMap((p, i) => (p.hit ? [i] : []))));
  const [score, setScore] = useState(a.score != null ? String(Math.round(a.score * 100)) : "");
  const [note, setNote] = useState(a.teacher_feedback || "");
  const [text, setText] = useState(a.answer_text || "");
  const { busy, error, run } = useSubmit();
  const hasRubric = a.rubric?.length > 0;
  const toggle = (i) => setHit((h) => { const n = new Set(h); n.has(i) ? n.delete(i) : n.add(i); return n; });
  const save = () => run(async () => {
    await overrideAnswer(kind, a.id, hasRubric ? { points_hit: [...hit].sort(), feedback: note } : { score: Number(score) / 100, feedback: note });
    onChanged();
  });
  const confirm = () => run(async () => { await confirmAnswer(kind, a.id, text !== a.answer_text ? text : undefined); onChanged(); });

  return (
    <div className="item">
      <div className="row"><strong>Q{a.position + 1}{a.concept_name ? ` · ${a.concept_name}` : ""}</strong>
        <span className="chip">{a.answer_format === "long_answer" ? "Long answer" : "Short answer"}</span></div>
      <p className="q-text">{a.question}</p>
      {a.needs_confirm ? (
        <div className="stack">
          <div className="callout warn"><strong>Spoken answer waiting for you.</strong> Check the transcript against what the student meant, fix it if needed, then confirm. It is not marked or counted until you do.</div>
          <label htmlFor={`tx-${a.id}`} className="small">Transcript ({a.transcript_language})</label>
          <textarea id={`tx-${a.id}`} className="input" rows={4} value={text} onChange={(e) => setText(e.target.value)} />
          <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
            <button className="btn small-btn" disabled={busy || !text.trim()} onClick={confirm}>Confirm transcript and mark</button>
          </div>
        </div>
      ) : (
        <>
          <WrittenResult q={a} teacher />
          <details className="mt" open={a.score_source === "ai"}>
            <summary>{a.score_source === "teacher" ? "Change your mark" : "Override the AI suggestion"}</summary>
            <div className="stack mt">
              {hasRubric ? (
                <fieldset className="q"><legend className="small">Key points this answer hit</legend>
                  {a.rubric.map((p, i) => (
                    <label key={i} style={{ display: "block" }}><input type="checkbox" checked={hit.has(i)} onChange={() => toggle(i)} /> {p.point} <span className="small">({p.marks})</span></label>
                  ))}
                </fieldset>
              ) : (
                <div><label htmlFor={`sc-${a.id}`} className="small">Score (0 to 100)</label>
                  <input id={`sc-${a.id}`} className="input" type="number" min="0" max="100" value={score} onChange={(e) => setScore(e.target.value)} /></div>
              )}
              <div><label htmlFor={`nt-${a.id}`} className="small">Note for the student (optional)</label>
                <input id={`nt-${a.id}`} className="input" maxLength={1000} value={note} onChange={(e) => setNote(e.target.value)} /></div>
              <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
                <button className="btn small-btn" disabled={busy || (!hasRubric && score === "")} onClick={save}>Save my marks</button>
                {a.ai_score != null && a.score_source === "teacher" && <span className="small">The AI had suggested {pct(a.ai_score)}.</span>}
              </div>
            </div>
          </details>
        </>
      )}
      <ErrorNote error={error} />
    </div>
  );
}

// `load` returns [{ student_name, submitted_at, score, waiting_for_you, answers }]; `kind` is "quiz" (test) or "check" (assignment check).
export default function AnswerReview({ kind, load, deps = [] }) {
  const state = useLoad(load, deps);
  return (
    <div className="mt">
      <Async state={state}>
        {(list) => list.length === 0 ? <p className="small mb0">Nothing handed in yet.</p> : (
          <div className="items">
            {list.map((w, n) => {
              const written = w.answers.filter((a) => a.answer_format !== "mcq");
              return (
                <div className="card mb0" key={`${w.student_id}-${w.check_id || n}`}>
                  <div className="row"><strong>{w.student_name}</strong><span className="small">{fmtDateTime(w.submitted_at)}</span></div>
                  <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
                    {w.score != null && <Pill kind={w.score >= 0.6 ? "ok" : "weak"}>{pct(w.score)}</Pill>}
                    {w.waiting_for_you > 0 && <Pill kind="sent">{w.waiting_for_you} to confirm</Pill>}
                    <span className="small">{written.length} written or spoken · {w.answers.length - written.length} multiple choice</span>
                  </div>
                  <div className="items mt">
                    {written.length === 0 && <p className="small mb0">No written answers in this one.</p>}
                    {written.map((a) => <AnswerRow key={`${a.id}-${a.score}-${a.score_source}-${a.needs_confirm}`} kind={kind} a={a} onChanged={state.reload} />)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Async>
    </div>
  );
}
