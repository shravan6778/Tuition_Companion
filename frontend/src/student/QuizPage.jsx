import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMyQuiz, submitQuiz } from "../api/learning";
import Header from "../shared/Header";
import { Async, ErrorNote, Pill, pct, useLoad, useSubmit } from "../shared/ui";
import Results from "./Results";

const KEYS = ["A", "B", "C", "D"];
const TYPE_LABEL = { recall: "Recall", application: "Application", cross_concept: "Connects two ideas" };

// A teacher test or a practice quiz. Multiple choice is graded in code, short answers by the tutor model.
export default function QuizPage() {
  const { quizId } = useParams();
  const state = useLoad(() => getMyQuiz(quizId), [quizId]);
  const [picked, setPicked] = useState({});
  const [typed, setTyped] = useState({});
  const [graded, setGraded] = useState(null);
  const { busy, error, run } = useSubmit();

  const quiz = graded || state.data;
  const ready = quiz?.questions.filter((q) => q.status === "ready") || [];
  const answered = ready.filter((q) => (q.answer_format === "mcq" ? picked[q.id] != null : (typed[q.id] || "").trim())).length;

  const submit = () =>
    run(async () => {
      const answers = ready.map((q) =>
        q.answer_format === "mcq"
          ? { question_id: q.id, chosen_index: picked[q.id] ?? null }
          : { question_id: q.id, answer_text: (typed[q.id] || "").trim() || null });
      setGraded(await submitQuiz(quizId, answers));
    });

  return (
    <>
      <Header title={quiz?.title || "Test"} subtitle={quiz ? (quiz.kind === "practice" ? "Practice test" : "Test from your teacher") : ""} />
      <div className="container">
        <Link to={quiz?.kind === "practice" ? "/student/practice" : "/student"} className="back-link">← Back</Link>
        <Async state={state}>
          {() => {
            const submitted = quiz.status === "submitted";
            return (
              <>
                {submitted && (
                  <div className="card row">
                    <div>
                      <div className="score-big">{pct(quiz.score)}</div>
                      <span className="small">{quiz.questions.filter((q) => q.correct).length} of {quiz.questions.length} questions right</span>
                    </div>
                    <Pill kind="submitted" />
                  </div>
                )}
                {quiz.questions.map((q, n) => (
                  <fieldset key={q.id} className="q" style={{ margin: "0 0 12px" }}>
                    <legend className="small">
                      Question {n + 1} · {TYPE_LABEL[q.question_type] || q.question_type}
                      {q.concept_name ? ` · ${q.concept_name}` : ""}{q.related_concept_name ? ` + ${q.related_concept_name}` : ""}
                    </legend>
                    {q.status !== "ready" ? (
                      <div className="callout warn">{q.message}</div>
                    ) : (
                      <>
                        <p className="q-text">{q.question}</p>
                        {q.answer_format === "mcq" ? (
                          (q.options || []).map((o, i) => {
                            const cls = submitted
                              ? i === q.correct_index ? "right" : i === q.chosen_index ? "wrong" : ""
                              : picked[q.id] === i ? "picked" : "";
                            return (
                              <button key={i} type="button" className={`opt ${cls}`} disabled={submitted}
                                aria-pressed={picked[q.id] === i} onClick={() => setPicked({ ...picked, [q.id]: i })}>
                                <span className="key">{KEYS[i]}</span><span>{o}</span>
                                {submitted && i === q.correct_index && <span> ✓ Correct answer</span>}
                                {submitted && i === q.chosen_index && i !== q.correct_index && <span> ✗ Your answer</span>}
                              </button>
                            );
                          })
                        ) : submitted ? (
                          <div className="stack">
                            <div className="callout"><strong>Your answer:</strong> {q.answer_text || <em>left blank</em>}</div>
                            {q.expected_answer && <div className="callout ok"><strong>Expected:</strong> {q.expected_answer}</div>}
                          </div>
                        ) : (
                          <>
                            <label htmlFor={`a-${q.id}`} className="small">Your answer</label>
                            <textarea id={`a-${q.id}`} className="input" maxLength={2000} value={typed[q.id] || ""}
                              onChange={(e) => setTyped({ ...typed, [q.id]: e.target.value })} />
                          </>
                        )}
                        {submitted && (
                          <div className="stack mt">
                            {q.answer_format !== "mcq" && q.score != null && <div><Pill kind={q.correct ? "ok" : "weak"}>{q.correct ? "Correct" : "Not quite"} · {pct(q.score)}</Pill></div>}
                            {q.feedback && <div className="callout info">{q.feedback}</div>}
                            {q.explanation && <div className="callout info"><strong>Why:</strong> {q.explanation}</div>}
                          </div>
                        )}
                      </>
                    )}
                  </fieldset>
                ))}
                {submitted ? (
                  <Results concepts={quiz.concept_results} atRisk={quiz.at_risk} />
                ) : (
                  <div className="sticky-submit">
                    <ErrorNote error={error} />
                    <div className="row">
                      <span className="small">{answered} of {ready.length} answered. Unanswered questions count as wrong.</span>
                      <button className="btn" disabled={busy || !quiz.can_submit} onClick={submit}>
                        {busy ? "Marking your answers..." : "Submit test"}
                      </button>
                    </div>
                    {!quiz.can_submit && <p className="small">This test can't be submitted yet, some questions are still being written.</p>}
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
