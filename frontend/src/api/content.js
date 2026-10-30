const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, { credentials: "include", ...options });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// Teacher: reference corpus + privacy-safe student outline
export const fetchBooks = async (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return request(`/teacher/books${query ? `?${query}` : ""}`);
};
export const fetchStudentBookOutlines = (studentId) => request(`/teacher/students/${studentId}/books`);

// Student: reference books
export const fetchMyLinkedBooks = () => request("/student/books");
export const fetchStudentLibrary = () => request("/student/library");
export const linkBook = (bookId) => request(`/student/books/${bookId}/link`, { method: "POST" });
export const unlinkBook = (bookId) => request(`/student/books/${bookId}/link`, { method: "DELETE" });
export const fetchChapterPages = (bookId, chapterId) => request(`/student/books/${bookId}/chapters/${chapterId}/pages`);

// Student-owned books
export const uploadStudentFrontPages = (file) => {
  const fd = new FormData(); fd.append("file", file);
  return request("/student/book-drafts/front-pages", { method: "POST", body: fd });
};
export const createStudentBook = (bookData) => request("/student/books", {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(bookData),
});
export const createStudentChapter = (bookId, chapterData) => request(`/student/books/${bookId}/chapters`, {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(chapterData),
});
export const uploadStudentChapterPages = (bookId, chapterId, file) => {
  const fd = new FormData(); fd.append("file", file);
  return request(`/student/books/${bookId}/chapters/${chapterId}/pages/upload`, { method: "POST", body: fd });
};
export const planStudentWholeBook = (bookId, file) => {
  const fd = new FormData(); fd.append("file", file);
  return request(`/student/books/${bookId}/whole-book/plan`, { method: "POST", body: fd });
};
export const confirmStudentWholeBook = (bookId, draftId, chapters) => request(`/student/books/${bookId}/whole-book/confirm`, {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ draft_id: draftId, chapters }),
});
export const removeStudentBook = (bookId) => request(`/student/books/${bookId}`, { method: "DELETE" });

// Admin reference-content maintenance remains separate from student-owned content.
export const adminDeleteBook = (bookId) => request(`/admin/books/${bookId}`, { method: "DELETE" });
export const adminDeleteChapter = (bookId, chapterId) => request(`/admin/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
