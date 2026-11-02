import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getCheck, submitCheck } from "../api/learning";
import Header from "../shared/Header";
import { Async, ErrorNote, Pill, pct, useLoad, useSubmit } from "../shared/ui";
import Results from "./Results";
import AnswerBox from "./AnswerBox";
import { answerPayload, answerReady, emptyAnswer } from "./answerState";
import WrittenResult from "../shared/WrittenResult";

const KEYS = ["A", "B", "C", "D"];

// The micro-check after "Mark complete": mostly multiple choice (graded in code) plus some written or spoken answers (marked against key points,
// as a suggestion a teacher can change). Keys and key points are revealed only after submitting.
export default function CheckPage() {
  const { checkId } = useParams();
  const state = useLoad(() => getCheck(checkId), [checkId]);
  const [picked, setPicked] = useState({});
  const { busy, error, run } = useSubmit();
  const [done, setDone] = useState(null);

  const check = done || state.data;
  const readyQs = check?.questions.filter((q) => q.status === "ready") || [];
  const [typed, setTyped] = useState({});
  const isWritten = (q) => q.answer_format && q.answer_format !== "mcq";
  const answered = readyQs.filter((q) => (isWritten(q) ? answerReady(typed[q.id]) : picked[q.id] != null)).length;
  const unconfirmed = readyQs.some((q) => isWritten(q) && typed[q.id]?.method === "voice" && typed[q.id].text.trim() && !typed[q.id].confirmed);

  const submit = () =>
    run(async () => {
      const answers = readyQs.map((q) => (isWritten(q) ? answerPayload(q.id, typed[q.id]) : { question_id: q.id, chosen_index: picked[q.id] ?? null }));
      setDone(await submitCheck(checkId, answers));
    });

  return (
    <>
      <Header title="Check your understanding" subtitle={check?.assignment_title} />
      <div className="container">
        <Link to="/student" className="back-link">← Back to Today's Work</Link>
        <Async state={state}>
          {() => {
            const submitted = check.status === "submitted";
            return (
              <>
                {submitted && (
                  <div className="card row">
                    <div>
                      <div className="score-big">{pct(check.score)}</div>
                      <span className="small">{check.questions.filter((q) => q.correct).length} of {check.questions.length} right{check.questions.some((q) => q.needs_confirm) ? " so far (a spoken answer is waiting for your teacher)" : ""}</span>
                    </div>
                    <Pill kind="submitted" />
                  </div>
                )}
                {check.questions.map((q, n) => (
                  <fieldset key={q.id} className="q" style={{ margin: "0 0 12px" }}>
                    <legend className="small">Question {n + 1}{q.concept_name ? ` · ${q.concept_name}` : ""}</legend>
                    {q.status !== "ready" ? (
                      <div className="callout warn">{q.message}</div>
                    ) : (
                      <>
                        <p className="q-text">{q.question}</p>
                        {isWritten(q) ? (
                          submitted ? <WrittenResult q={q} /> : (
                            <AnswerBox id={q.id} long={q.answer_format === "long_answer"} voiceAllowed={q.voice_allowed} value={typed[q.id] || emptyAnswer}
                              onChange={(v) => setTyped({ ...typed, [q.id]: v })} />
                          )
                        ) : q.options.map((o, i) => {
                          const cls = submitted
                            ? i === q.correct_index ? "right" : i === q.chosen_index ? "wrong" : ""
                            : picked[q.id] === i ? "picked" : "";
                          return (
                            <button key={i} type="button" className={`opt ${cls}`} disabled={submitted}
                              aria-pressed={picked[q.id] === i} onClick={() => setPicked({ ...picked, [q.id]: i })}>
                              <span className="key">{KEYS[i]}</span><span>{o}</span>
                              {submitted && i === q.correct_index && <span className="right-mark"> ✓ Correct answer</span>}
                              {submitted && i === q.chosen_index && i !== q.correct_index && <span> ✗ Your answer</span>}
                            </button>
                          );
                        })}
                        {submitted && !isWritten(q) && q.explanation && <div className="callout info"><strong>Why:</strong> {q.explanation}</div>}
                      </>
                    )}
                  </fieldset>
                ))}
                {submitted ? (
                  <Results concepts={check.concept_results} atRisk={check.at_risk} />
                ) : (
                  <div className="sticky-submit">
                    <ErrorNote error={error} />
                    <div className="row">
                      <span className="small">{answered} of {readyQs.length} answered. Unanswered questions count as wrong.</span>
                      <button className="btn" disabled={busy || !check.can_submit || unconfirmed} onClick={submit}>
                        {busy ? "Marking..." : "Submit answers"}
                      </button>
                    </div>
                    {unconfirmed && <p className="small">Tick "I read this and it says what I meant" on your spoken answers first.</p>}
                    {!check.can_submit && <p className="small">Some questions are still being written. Reload in a moment.</p>}
                  </div>
                )}
              </>
            );
          }}
        </Async>
      </div>
    </>
  );
}
