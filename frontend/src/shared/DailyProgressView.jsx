import { useState } from "react";
import { Async, Empty, Pill, pct, useLoad } from "./ui";

// Day-by-day progress. `fetcher(from, to)` resolves to the daily-progress payload, so the same view
// serves any reader (the teacher now; a parent later) without knowing which route feeds it.

const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const daysAgo = (n) => { const d = new Date(); d.setDate(d.getDate() - n); return iso(d); };
const longDay = (s) => new Date(`${s}T00:00:00`).toLocaleDateString(undefined, { weekday: "short", day: "numeric", month: "short", year: "numeric" });
const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
const time = (t) => new Date(t).toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });

function Section({ title, children }) {
  return (
    <div className="mt">
      <div className="small"><strong>{title}</strong></div>
      <div className="items mt">{children}</div>
    </div>
  );
}

function DayCard({ d }) {
  const checks = d.worked.filter((w) => w.kind === "check");
  const homework = d.worked.filter((w) => w.kind === "homework");
  const parts = [
    d.subjects_worked.length ? plural(d.subjects_worked.length, "subject") : null,
    checks.length ? plural(checks.length, "check") : null,
    homework.length ? plural(homework.length, "homework hand-in") : null,
    d.tests.length ? `${plural(d.tests.length, "test")}${d.average_test_score != null ? ` (${pct(d.average_test_score)})` : ""}` : null,
  ].filter(Boolean);

  return (
    <div className="card mb0">
      <strong>{longDay(d.day)}</strong>
      <div className="small">{parts.length ? parts.join(" · ") : "Nothing done by the student this day"}</div>
      {d.subjects_worked.length > 0 && <div className="small mt">Subjects worked on: {d.subjects_worked.join(", ")}</div>}

      {d.worked.length > 0 && (
        <Section title="Done by the student">
          {d.worked.map((w, i) => (
            <div className="item" key={`${w.kind}-${i}`}>
              <div className="row" style={{ alignItems: "center" }}>
                <div style={{ flex: 1, minWidth: 180 }}>
                  <strong>{w.title}</strong>
                  <div className="small">{[w.subject, w.kind === "check" ? "Check" : "Homework", time(w.at)].filter(Boolean).join(" · ")}</div>
                </div>
                {w.kind === "check" && <span className="small nowrap">Score {pct(w.score)}</span>}
                {w.kind === "homework" && <Pill kind={w.verdict || "sent"} />}
              </div>
            </div>
          ))}
        </Section>
      )}

      {d.tests.length > 0 && (
        <Section title="Tests">
          {d.tests.map((t) => (
            <div className="item" key={t.quiz_id}>
              <div className="row" style={{ alignItems: "center" }}>
                <div style={{ flex: 1, minWidth: 180 }}>
                  <strong>{t.title}</strong>
                  <div className="small">{[t.subject, t.kind === "practice" ? "Practice" : "Teacher test", time(t.at)].filter(Boolean).join(" · ")}</div>
                </div>
                <span className="small nowrap">Result {pct(t.score)}</span>
              </div>
            </div>
          ))}
        </Section>
      )}

      {d.assigned.length > 0 && (
        <Section title="Assigned this day">
          {d.assigned.map((a) => (
            <div className="item" key={a.assignment_id}>
              <strong>{a.title}</strong>
              <div className="small">{[a.subject, a.chapter_title, a.due_date ? `due ${longDay(a.due_date)}` : null].filter(Boolean).join(" · ")}</div>
            </div>
          ))}
        </Section>
      )}

      {d.doubts.length > 0 && (
        <Section title={`Doubts asked (${d.doubts.length})`}>
          {d.doubts.map((x, i) => (
            <div className="item" key={i}>
              <div>{x.text}</div>
              {x.subject && <div className="small">{x.subject}</div>}
            </div>
          ))}
        </Section>
      )}

      {d.sessions.length > 0 && (
        <Section title="Session notes">
          {d.sessions.map((s, i) => (
            <div className="item" key={i}>
              <div>{s.notes}</div>
              {s.tags.length > 0 && <div className="small">{s.tags.join(", ")}</div>}
            </div>
          ))}
        </Section>
      )}
    </div>
  );
}

export default function DailyProgressView({ fetcher }) {
  const [from, setFrom] = useState(() => daysAgo(13));
  const [to, setTo] = useState(() => daysAgo(0));
  const state = useLoad(() => fetcher(from, to), [from, to]);
  return (
    <div className="stack">
      <div className="row">
        <p className="small mb0">What the student did each day. "Assigned" is what the teacher set; "Done by the student" is what was actually handed in.</p>
        <div className="row gap-s">
          <div>
            <label htmlFor="dp-from" className="small">From</label>
            <input id="dp-from" type="date" className="input" value={from} max={to} onChange={(e) => e.target.value && setFrom(e.target.value)} />
          </div>
          <div>
            <label htmlFor="dp-to" className="small">To</label>
            <input id="dp-to" type="date" className="input" value={to} min={from} onChange={(e) => e.target.value && setTo(e.target.value)} />
          </div>
        </div>
      </div>
      <Async state={state}>
        {(p) => (
          <>
            <div className="tiles mb0">
              <div className="tile"><div className="num">{p.days_active}</div><div className="lbl">Active days</div></div>
              <div className="tile"><div className="num">{p.checks_done}</div><div className="lbl">Checks done</div></div>
              <div className="tile"><div className="num">{p.tests_taken}</div><div className="lbl">Tests taken</div></div>
              <div className="tile"><div className="num">{pct(p.average_test_score)}</div><div className="lbl">Average test result</div></div>
            </div>
            {p.days.length === 0
              ? <div className="card"><Empty>Nothing happened between {longDay(p.date_from)} and {longDay(p.date_to)}.</Empty></div>
              : p.days.map((d) => <DayCard key={d.day} d={d} />)}
          </>
        )}
      </Async>
    </div>
  );
}
