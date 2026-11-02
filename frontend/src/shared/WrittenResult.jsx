import { Pill, pct } from "./ui";

const LANG = { "en-IN": "English", "hi-IN": "Hindi", "te-IN": "Telugu" };

// What a marked written / spoken answer shows: the text, how it was given, the key points hit and missed, and who gave the score.
export default function WrittenResult({ q, teacher = false }) {
  const aiNote = q.score_source === "ai" || q.needs_confirm;
  return (
    <div className="stack">
      <div className="callout">
        <strong>{teacher ? "Answer" : "Your answer"}</strong>
        {" "}<span className="chip">{q.input_method === "voice" ? `Spoken · ${LANG[q.transcript_language] || q.transcript_language}` : "Typed"}</span>
        <p className="pre mb0 mt">{q.answer_text || <em>left blank</em>}</p>
      </div>
      {q.rubric?.length > 0 && (
        <ul className="mb0" aria-label="Key points">
          {q.rubric.map((p, i) => (
            <li key={i}>{p.hit == null ? "• " : p.hit ? "✓ " : "✗ "}{p.point} <span className="small">({p.marks} {p.marks === 1 ? "mark" : "marks"}{p.hit == null ? "" : p.hit ? ", got it" : ", missed"})</span></li>
          ))}
        </ul>
      )}
      <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
        {q.score != null && <Pill kind={q.score >= 0.8 ? "ok" : "weak"}>{q.marks_available ? `${q.marks_awarded} of ${q.marks_available} marks · ` : ""}{pct(q.score)}</Pill>}
        {q.score_label && <span className={`chip${aiNote ? "" : " ok"}`}>{q.score_label}</span>}
      </div>
      {q.feedback && <div className="callout info">{q.feedback}</div>}
      {q.teacher_feedback && <div className="callout ok"><strong>Your teacher:</strong> {q.teacher_feedback}</div>}
      {q.expected_answer && <div className="callout ok"><strong>A good answer:</strong> {q.expected_answer}</div>}
    </div>
  );
}
