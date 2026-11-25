// Pure helpers for showing a student's concepts organised by subject -> chapter -> page.
// Used by the teacher's Weak Areas and Analytics tabs (and reusable by any read-only view of the same data).

export const byPage = (a, b) =>
  (a.page_number ?? Infinity) - (b.page_number ?? Infinity) || a.concept_name.localeCompare(b.concept_name);

const byChapter = (a, b) =>
  (a.sequence ?? Infinity) - (b.sequence ?? Infinity) || a.title.localeCompare(b.title);

// concepts: ConceptTrendItem[] -> [{ subject, count, chapters: [{ id, title, sequence, concepts }] }]
// Subjects are alphabetical, chapters follow book order, concepts follow page order.
export function groupConcepts(concepts) {
  const subjects = new Map();
  for (const c of concepts) {
    const subject = c.subject || "General";
    if (!subjects.has(subject)) subjects.set(subject, new Map());
    const chapters = subjects.get(subject);
    const key = c.chapter_id || "none";
    if (!chapters.has(key)) chapters.set(key, { id: key, title: c.chapter_title || "Other", sequence: c.chapter_sequence, concepts: [] });
    chapters.get(key).concepts.push(c);
  }
  return [...subjects.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([subject, chapters]) => {
      const list = [...chapters.values()].sort(byChapter).map((ch) => ({ ...ch, concepts: ch.concepts.sort(byPage) }));
      return { subject, count: list.reduce((n, ch) => n + ch.concepts.length, 0), chapters: list };
    });
}
