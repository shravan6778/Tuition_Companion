// What the teacher has ticked in the assignment tree, and how it becomes a POST /teacher/assignments body.
// Kept apart from the component so the rules are plain functions (and the component file only exports a component).

export const EMPTY_SELECTION = { bookId: "", chapterId: "", whole: null, concepts: [], items: [] };

export const itemKey = (i) => `${i.kind}|${i.label}|${i.page_number ?? ""}`;

// Groups under a chapter, in the order the teacher sees them. `kind` is the page-item kind the API stores.
export const GROUPS = [
  { id: "concepts", title: "Concepts", empty: "No concepts were found in this chapter." },
  { id: "examples", title: "Examples", empty: "No worked examples were found in this chapter." },
  { id: "exercises", title: "Exercises", empty: "No exercise questions were found in this chapter." },
  { id: "figures", title: "Figures", empty: "No figures were found in this chapter." },
  { id: "activities", title: "Activities", empty: "" },
];

export function countsLine(sel, chapterTitle) {
  if (sel.whole === "book") return "The whole book";
  if (sel.whole === "chapter") return `The whole chapter${chapterTitle ? `: ${chapterTitle}` : ""}`;
  const parts = [];
  if (sel.concepts.length) parts.push(`${sel.concepts.length} concept${sel.concepts.length > 1 ? "s" : ""}`);
  if (sel.items.length) parts.push(`${sel.items.length} item${sel.items.length > 1 ? "s" : ""}`);
  return parts.length ? `${parts.join(" and ")}${chapterTitle ? ` from ${chapterTitle}` : ""}` : "";
}

export const isEmptySelection = (sel) => !sel.bookId || (!sel.whole && sel.concepts.length === 0 && sel.items.length === 0);

// Whole book -> subject. Whole chapter -> chapter. Any example / question / figure -> items (the ticked concepts ride
// along). Only concepts -> concept. Returns null while nothing usable is ticked.
export function selectionToAssignment(sel) {
  if (isEmptySelection(sel)) return null;
  if (sel.whole === "book") return { level: "subject", book_id: sel.bookId };
  if (!sel.chapterId) return null;
  const base = { book_id: sel.bookId, chapter_id: sel.chapterId };
  if (sel.whole === "chapter") return { level: "chapter", ...base };
  if (sel.items.length > 0) {
    return {
      level: "items", ...base,
      items: sel.items.map(({ kind, label, page_number }) => ({ kind, label, page_number })),
      concept_names: sel.concepts.length ? sel.concepts : undefined,
    };
  }
  return { level: "concept", ...base, concept_names: sel.concepts };
}
