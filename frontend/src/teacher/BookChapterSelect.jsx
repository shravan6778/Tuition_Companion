import { bookLabel } from "../shared/ui";

// Book + chapter dropdowns over the teacher's visible books. Only chapters that finished processing can be used.
export default function BookChapterSelect({ books, bookId, chapterId, onChange, chapterRequired = true, idPrefix = "bc" }) {
  const book = books.find((b) => b.id === bookId);
  const ready = (book?.chapters || []).filter((c) => c.status === "ready");
  return (
    <>
      <div>
        <label htmlFor={`${idPrefix}-book`}>Book</label>
        <select id={`${idPrefix}-book`} className="input" value={bookId} required onChange={(e) => onChange({ bookId: e.target.value, chapterId: "" })}>
          <option value="">Choose a book...</option>
          {books.map((b) => <option key={b.id} value={b.id}>{bookLabel(b)}{b.is_reference ? " · official" : ""}</option>)}
        </select>
      </div>
      <div>
        <label htmlFor={`${idPrefix}-ch`}>Chapter</label>
        <select id={`${idPrefix}-ch`} className="input" value={chapterId} disabled={!book} required={chapterRequired} onChange={(e) => onChange({ bookId, chapterId: e.target.value })}>
          <option value="">{chapterRequired ? "Choose a chapter..." : "Whole book"}</option>
          {ready.map((c) => <option key={c.id} value={c.id}>Ch {c.sequence_num}: {c.title}</option>)}
        </select>
        {book && ready.length === 0 && <div className="small">No chapters are ready in this book yet.</div>}
      </div>
    </>
  );
}
