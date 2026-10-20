import { useState } from "react";
import { createAssignment, exerciseProposal } from "../api/learning";
import { fetchChapterGraph } from "../api/content";
import { ErrorNote, pct, useSubmit } from "../shared/ui";
import BookChapterSelect from "./BookChapterSelect";

const LEVELS = [
  ["chapter", "A chapter", "Every idea in one chapter"],
  ["concept", "Specific ideas", "Pick the ideas yourself"],
  ["exercise", "An exercise", "We suggest the ideas it practises; you confirm"],
  ["subject", "Whole book", "Every ready chapter of the book"],
];

// "12-14, 20" -> [12, 13, 14, 20]
function parsePages(text) {
  const out = new Set();
  for (const part of text.split(",").map((s) => s.trim()).filter(Boolean)) {
    const m = part.match(/^(\d+)\s*-\s*(\d+)$/);
    if (m) for (let n = +m[1]; n <= Math.min(+m[2], +m[1] + 60); n++) out.add(n);
    else if (/^\d+$/.test(part)) out.add(+part);
    else throw new Error(`"${part}" isn't a page number or range`);
  }
  return [...out].sort((a, b) => a - b);
}

// Create an assignment for one room or one student (exactly one of roomId / studentId).
export default function AssignmentForm({ books, roomId, studentId, onCreated }) {
  const [level, setLevel] = useState("chapter");
  const [sel, setSel] = useState({ bookId: "", chapterId: "" });
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");
  const [pagesText, setPagesText] = useState("");
  const [options, setOptions] = useState(null); // [{id, name, note}] the teacher ticks from
  const [chosen, setChosen] = useState(new Set());
  const [info, setInfo] = useState("");
  const { busy, error, setError, run } = useSubmit();

  const needsChapter = level !== "subject";
  const reset = () => { setOptions(null); setChosen(new Set()); setInfo(""); };

  const loadConcepts = () =>
    run(async () => {
      reset();
      if (level === "concept") {
        const g = await fetchChapterGraph(sel.bookId, sel.chapterId);
        setOptions(g.nodes.map((n) => ({ id: n.id, name: n.name, note: `page${n.pages.length > 1 ? "s" : ""} ${n.pages.join(", ")}` })));
      } else {
        const p = await exerciseProposal({ book_id: sel.bookId, chapter_id: sel.chapterId, page_numbers: pagesText.trim() ? parsePages(pagesText) : undefined });
        if (p.status === "no_exercise_pages") setInfo("This chapter has no exercise pages. Pick ideas yourself with \"Specific ideas\" instead.");
        else if (p.status === "no_vectors") setInfo("This chapter isn't indexed yet, so we can't suggest ideas. Try again soon, or use \"Specific ideas\".");
        else setInfo(`Exercise on page${p.exercise_pages.length > 1 ? "s" : ""} ${p.exercise_pages.join(", ")}. Untick anything that doesn't belong.`);
        setOptions(p.proposed.map((c) => ({ id: c.concept_id, name: c.name, note: `${pct(c.similarity)} match` })));
        setChosen(new Set(p.proposed.map((c) => c.concept_id)));
      }
    });

  const submit = (e) => {
    e.preventDefault();
    run(async () => {
      const body = {
        level, book_id: sel.bookId, room_id: roomId || undefined, student_id: studentId || undefined,
        chapter_id: needsChapter ? sel.chapterId : undefined, title: title.trim() || undefined, due_date: due || undefined,
      };
      if (level === "concept" || level === "exercise") {
        if (chosen.size === 0) throw new Error("Tick at least one idea first.");
        body.concept_ids = [...chosen];
      }
      if (level === "exercise" && pagesText.trim()) body.page_numbers = parsePages(pagesText);
      const created = await createAssignment(body);
      reset(); setTitle(""); setDue(""); setPagesText("");
      onCreated?.(created);
    });
  };

  const toggle = (id) => { const n = new Set(chosen); n.has(id) ? n.delete(id) : n.add(id); setChosen(n); };
  const picking = level === "concept" || level === "exercise";

  return (
    <form className="card stack" onSubmit={submit}>
      <h3>Set new work</h3>
      <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
        <legend className="small">What are you assigning?</legend>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 8 }}>
          {LEVELS.map(([id, label, hint]) => (
            <label key={id} className={`opt${level === id ? " picked" : ""}`} style={{ marginBottom: 0, flexDirection: "column", gap: 0 }}>
              <span><input type="radio" name={`lvl-${roomId || studentId}`} checked={level === id} onChange={() => { setLevel(id); reset(); }} /> <strong>{label}</strong></span>
              <span className="small">{hint}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="grid2">
        <BookChapterSelect books={books} bookId={sel.bookId} chapterId={sel.chapterId} chapterRequired={needsChapter}
          idPrefix={`af-${roomId || studentId}`} onChange={(v) => { setSel(v); reset(); }} />
        {level === "exercise" && (
          <div>
            <label htmlFor="af-pages">Exercise pages (optional)</label>
            <input id="af-pages" className="input" value={pagesText} placeholder="e.g. 12-14, 20" onChange={(e) => { setPagesText(e.target.value); reset(); }} />
            <div className="small">Leave empty to use all the chapter's exercise pages.</div>
          </div>
        )}
        <div>
          <label htmlFor="af-title">Title (optional)</label>
          <input id="af-title" className="input" value={title} maxLength={200} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div>
          <label htmlFor="af-due">Due date (optional)</label>
          <input id="af-due" type="date" className="input" value={due} onChange={(e) => setDue(e.target.value)} />
        </div>
      </div>

      {picking && (
        <div className="stack">
          <button type="button" className="btn secondary" disabled={busy || !sel.bookId || !sel.chapterId} onClick={loadConcepts}>
            {level === "concept" ? "Show ideas in this chapter" : "Suggest ideas for this exercise"}
          </button>
          {info && <div className="callout info">{info}</div>}
          {options && options.length > 0 && (
            <div className="items" role="group" aria-label="Ideas to assign">
              {options.map((o) => (
                <div className="item" key={o.id}>
                  <label style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 0, fontWeight: 400 }}>
                    <input type="checkbox" checked={chosen.has(o.id)} onChange={() => toggle(o.id)} style={{ marginTop: 5 }} />
                    <span><strong>{o.name}</strong> <span className="small">{o.note}</span></span>
                  </label>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <ErrorNote error={error} />
      <div className="row">
        <span className="small">Goes to {roomId ? "every student in this room" : "this student only"}.</span>
        <button className="btn" disabled={busy || !sel.bookId || (needsChapter && !sel.chapterId) || (picking && chosen.size === 0)} onClick={() => setError("")}>
          {busy ? "Saving..." : "Assign work"}
        </button>
      </div>
    </form>
  );
}
