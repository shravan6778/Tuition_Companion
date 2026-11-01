import { useEffect, useRef, useState } from "react";
import { chapterOutline } from "../api/learning";
import { bookLabel } from "../shared/ui";
import { countsLine, EMPTY_SELECTION, GROUPS, itemKey } from "./assignmentSelection";

// Book > Chapter > Concepts / Examples / Exercises (one box per question) / Figures / Activities.
// Ticking a book or a chapter assigns all of it; ticking anything inside a chapter assigns just those parts.
// An assignment covers ONE chapter, so ticking in another chapter starts the selection over there.
// `value` is { bookId, chapterId, whole, concepts, items } (see assignmentSelection.js).
export default function AssignmentTree({ books, value, onChange, idPrefix = "tree" }) {
  const [openBooks, setOpenBooks] = useState(() => new Set());
  const [openChapters, setOpenChapters] = useState(() => new Set());
  const [outlines, setOutlines] = useState({}); // chapterId -> { status: "loading" | "ready" | "error", data, error }

  const loadOutline = async (bookId, chapterId) => {
    if (outlines[chapterId]?.status === "ready" || outlines[chapterId]?.status === "loading") return;
    setOutlines((o) => ({ ...o, [chapterId]: { status: "loading" } }));
    try {
      const data = await chapterOutline({ book_id: bookId, chapter_id: chapterId });
      setOutlines((o) => ({ ...o, [chapterId]: { status: "ready", data } }));
    } catch (e) {
      setOutlines((o) => ({ ...o, [chapterId]: { status: "error", error: e.message } }));
    }
  };

  const toggleSet = (setter, id) => setter((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const toggleBook = (b) => toggleSet(setOpenBooks, b.id);
  const toggleChapter = (b, c) => {
    toggleSet(setOpenChapters, c.id);
    if (!openChapters.has(c.id)) loadOutline(b.id, c.id);
  };

  // A selection inside chapter c of book b, keeping the current picks only if they are already in that chapter.
  const partial = (b, c) => (value.chapterId === c.id && !value.whole ? value : { ...EMPTY_SELECTION, bookId: b.id, chapterId: c.id });
  const pickWhole = (b, c) => {
    if (c ? value.whole === "chapter" && value.chapterId === c.id : value.whole === "book" && value.bookId === b.id) return onChange(EMPTY_SELECTION);
    onChange(c ? { ...EMPTY_SELECTION, bookId: b.id, chapterId: c.id, whole: "chapter" } : { ...EMPTY_SELECTION, bookId: b.id, whole: "book" });
  };
  const toggleConcepts = (b, c, names, on) => {
    const cur = partial(b, c);
    const rest = cur.concepts.filter((n) => !names.includes(n));
    onChange({ ...cur, concepts: on ? [...rest, ...names] : rest });
  };
  const toggleItems = (b, c, items, on) => {
    const cur = partial(b, c);
    const drop = new Set(items.map(itemKey));
    const rest = cur.items.filter((i) => !drop.has(itemKey(i)));
    onChange({ ...cur, items: on ? [...rest, ...items] : rest });
  };

  const chosenChapter = books.flatMap((b) => b.chapters || []).find((c) => c.id === value.chapterId);
  const summary = countsLine(value, chosenChapter ? `Ch ${chosenChapter.sequence_num}: ${chosenChapter.title}` : "");

  return (
    <div className="stack">
      <div role="tree" aria-label="Pick what to assign" style={{ border: "1px solid var(--border)", borderRadius: 8, padding: 8, maxHeight: 420, overflowY: "auto" }}>
        {books.length === 0 && <div className="small">No books to pick from yet.</div>}
        {books.map((b) => {
          const ready = (b.chapters || []).filter((c) => c.status === "ready");
          const open = openBooks.has(b.id);
          return (
            <div key={b.id} role="treeitem" aria-expanded={open} aria-selected={value.whole === "book" && value.bookId === b.id}>
              <Row id={`${idPrefix}-b-${b.id}`} open={open} onToggle={() => toggleBook(b)}
                checked={value.whole === "book" && value.bookId === b.id} onCheck={() => pickWhole(b, null)}
                label={<strong>{bookLabel(b)}{b.is_reference ? " · official" : ""}</strong>} />
              {open && (
                <div role="group" style={{ marginLeft: 22 }}>
                  {ready.length === 0 && <div className="small" style={{ padding: "4px 0" }}>No chapters are ready in this book yet.</div>}
                  {ready.map((c) => {
                    const copen = openChapters.has(c.id);
                    const inThis = value.chapterId === c.id;
                    const picked = inThis && !value.whole ? value.concepts.length + value.items.length : 0;
                    return (
                      <div key={c.id} role="treeitem" aria-expanded={copen} aria-selected={inThis}>
                        <Row id={`${idPrefix}-c-${c.id}`} open={copen} onToggle={() => toggleChapter(b, c)}
                          checked={inThis && value.whole === "chapter"} indeterminate={picked > 0} onCheck={() => pickWhole(b, c)}
                          label={<span>Ch {c.sequence_num}: {c.title}{picked > 0 && <span className="pill info" style={{ marginLeft: 8 }}>{picked} picked</span>}</span>} />
                        {copen && <ChapterBody outline={outlines[c.id]} sel={inThis && !value.whole ? value : EMPTY_SELECTION}
                          idPrefix={`${idPrefix}-${c.id}`} onConcepts={(n, on) => toggleConcepts(b, c, n, on)} onItems={(i, on) => toggleItems(b, c, i, on)}
                          onRetry={() => { setOutlines((o) => ({ ...o, [c.id]: undefined })); loadOutline(b.id, c.id); }} />}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="row">
        <span className="small" aria-live="polite">{summary ? `Selected: ${summary}` : "Tick a whole book or chapter, or open a chapter and pick concepts, examples, questions or figures."}</span>
        {summary && <button type="button" className="btn link" onClick={() => onChange(EMPTY_SELECTION)}>Clear</button>}
      </div>
    </div>
  );
}

function Row({ id, open, onToggle, checked, indeterminate, onCheck, label }) {
  const box = useRef(null);
  useEffect(() => { if (box.current) box.current.indeterminate = !!indeterminate && !checked; }, [indeterminate, checked]);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 6, minHeight: 40 }}>
      <button type="button" className="btn link" aria-label={open ? "Collapse" : "Expand"} aria-expanded={open} onClick={onToggle}
        style={{ textDecoration: "none", width: 28, padding: 0 }}>{open ? "▾" : "▸"}</button>
      <label htmlFor={id} style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 0, fontWeight: 400, cursor: "pointer" }}>
        <input ref={box} id={id} type="checkbox" checked={checked} onChange={onCheck} />
        {label}
      </label>
    </div>
  );
}

function ChapterBody({ outline, sel, idPrefix, onConcepts, onItems, onRetry }) {
  if (!outline || outline.status === "loading") return <div className="small" style={{ marginLeft: 22 }} role="status">Loading this chapter...</div>;
  if (outline.status === "error") {
    return <div className="callout warn" style={{ marginLeft: 22 }} role="alert">{outline.error} <button type="button" className="btn link" onClick={onRetry}>Try again</button></div>;
  }
  const { data } = outline;
  const have = (id) => (id === "concepts" ? data.concepts : data[id] || []);
  return (
    <div style={{ marginLeft: 22 }}>
      {GROUPS.map((g) => {
        const rows = have(g.id);
        if (rows.length === 0 && !g.empty) return null;
        const isConcept = g.id === "concepts";
        const ticked = (r) => (isConcept ? sel.concepts.includes(r) : sel.items.some((i) => itemKey(i) === itemKey(r)));
        const allOn = rows.length > 0 && rows.every(ticked);
        const setAll = (on) => (isConcept ? onConcepts(rows, on) : onItems(rows, on));
        return (
          <div key={g.id} role="group" aria-label={g.title} style={{ margin: "6px 0 10px" }}>
            <div style={{ display: "flex", gap: 8, alignItems: "center", minHeight: 32 }}>
              <strong className="small" style={{ color: "inherit" }}>{g.title} ({rows.length})</strong>
              {rows.length > 1 && <button type="button" className="btn link" onClick={() => setAll(!allOn)}>{allOn ? "Clear all" : "Select all"}</button>}
            </div>
            {rows.length === 0 && <div className="small">{g.empty}</div>}
            {rows.map((r, n) => {
              const text = isConcept ? r : r.label;
              const id = `${idPrefix}-${g.id}-${n}`;
              return (
                <label key={id} htmlFor={id} style={{ display: "flex", gap: 10, alignItems: "flex-start", fontWeight: 400, margin: "2px 0 2px 8px" }}>
                  <input id={id} type="checkbox" checked={ticked(r)} style={{ marginTop: 5 }}
                    onChange={(e) => (isConcept ? onConcepts([r], e.target.checked) : onItems([r], e.target.checked))} />
                  <span>{text}{!isConcept && r.page_number != null && <span className="small"> · p. {r.page_number}</span>}</span>
                </label>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}
