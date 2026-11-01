import { useState } from "react";
import { assignmentSubmissions, reviewSubmission } from "../api/learning";
import HomeworkPhoto from "../shared/HomeworkPhoto";
import { Async, ErrorNote, Pill, fmtDateTime, useLoad, useSubmit } from "../shared/ui";

const VERDICTS = [["good", "Good"], ["needs_work", "Needs work"], ["redo", "Redo"]];

function Judge({ submission, onDone }) {
  const [feedback, setFeedback] = useState(submission.feedback || "");
  const { busy, error, run } = useSubmit();
  const give = (verdict) => run(async () => { await reviewSubmission(submission.id, verdict, feedback.trim()); onDone(); });
  return (
    <div className="stack mt">
      <div>
        <label htmlFor={`fb-${submission.id}`}>Note for the student (optional)</label>
        <input id={`fb-${submission.id}`} className="input" value={feedback} maxLength={1000} onChange={(e) => setFeedback(e.target.value)} />
      </div>
      <ErrorNote error={error} />
      <div className="row gap-s" style={{ justifyContent: "flex-start" }} role="group" aria-label="Your verdict">
        {VERDICTS.map(([id, label]) => (
          <button key={id} type="button" className={`btn small-btn${submission.verdict === id ? "" : " secondary"}`} aria-pressed={submission.verdict === id}
            disabled={busy} onClick={() => give(id)}>{label}</button>
        ))}
      </div>
    </div>
  );
}

// Everything students handed in for one homework task, newest first, with the verdict buttons on each student's newest attempt.
export default function SubmissionReview({ assignmentId, studentId, onChanged }) {
  const state = useLoad(() => assignmentSubmissions(assignmentId, studentId), [assignmentId, studentId]);
  const changed = () => { state.reload(); onChanged?.(); };
  return (
    <div className="mt">
      <Async state={state}>
        {(list) => {
          if (list.length === 0) return <p className="small mb0">Nothing handed in yet.</p>;
          // the list is newest first, so the first row seen for a student is the attempt that counts
          const newestOf = [];
          const seen = new Set();
          for (const s of list) {
            if (!seen.has(s.student_id)) { seen.add(s.student_id); newestOf.push(s.id); }
          }
          return (
            <div className="items">
              {list.map((s) => (
                <div className="item" key={s.id}>
                  <div className="row"><strong>{s.student_name}</strong><span className="small">{fmtDateTime(s.created_at)}</span></div>
                  <div className="row gap-s mt" style={{ justifyContent: "flex-start" }}>
                    <span className="chip">{s.source === "photo" ? "Photo" : "Spoken answer"}</span>
                    {s.verdict ? <Pill kind={s.verdict} /> : <Pill kind="sent">Waiting for you</Pill>}
                    {!newestOf.includes(s.id) && <span className="small">Earlier attempt</span>}
                  </div>
                  {s.has_photo && <div className="mt"><HomeworkPhoto path={`/teacher/submissions/${s.id}/photo`} alt={`${s.student_name}'s homework`} /></div>}
                  {s.text && <p className="pre mt mb0">{s.text}</p>}
                  {s.feedback && !newestOf.includes(s.id) && <p className="small mb0 mt">You said: {s.feedback}</p>}
                  {newestOf.includes(s.id) && <Judge submission={s} onDone={changed} />}
                </div>
              ))}
            </div>
          );
        }}
      </Async>
    </div>
  );
}
