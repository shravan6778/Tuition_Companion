const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...options,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Teacher Endpoints ---

export async function fetchBooks(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/teacher/books${query ? `?${query}` : ""}`);
}

export async function createBook(bookData) {
  return request("/teacher/books", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bookData),
  });
}

export async function createChapter(bookId, chapterData) {
  return request(`/teacher/books/${bookId}/chapters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(chapterData),
  });
}

export async function uploadChapterPages(bookId, chapterId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return request(`/teacher/books/${bookId}/chapters/${chapterId}/pages/upload`, {
    method: "POST",
    body: formData,
  });
}

// --- Front pages first, whole-textbook upload, bulk link ---

// Step 1 of adding a book: cover + publisher/edition pages -> proposed metadata + matching known books.
export async function uploadFrontPages(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/teacher/book-drafts/front-pages", { method: "POST", body: formData });
}

export async function planWholeBook(bookId, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request(`/teacher/books/${bookId}/whole-book/plan`, { method: "POST", body: formData });
}

export async function confirmWholeBook(bookId, draftId, chapters) {
  return request(`/teacher/books/${bookId}/whole-book/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_id: draftId, chapters }),
  });
}

// Link a book to every student currently in a single-class room.
export async function bulkLinkBook(roomId, bookId) {
  return request(`/teacher/rooms/${roomId}/books/${bookId}/link`, { method: "POST" });
}

// --- Chapter requests (teacher inbox) ---

export async function fetchTeacherRequests(status = "open") {
  return request(`/teacher/chapter-requests?status=${status}`);
}

export async function dismissRequest(requestId) {
  return request(`/teacher/chapter-requests/${requestId}/dismiss`, { method: "POST" });
}

export async function fulfillRequest(requestId, chapterId = null) {
  return request(`/teacher/chapter-requests/${requestId}/fulfill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(chapterId ? { chapter_id: chapterId } : {}),
  });
}

// Per chapter: "your chapter X is identical to / an edition of chapter Y in book Z".
export async function fetchChapterMatches(bookId) {
  return request(`/teacher/books/${bookId}/chapter-matches`);
}

// "This looks like an edition of book X": suggestions, confirm, clear.
export async function fetchVariantSuggestions(bookId) {
  return request(`/teacher/books/${bookId}/variant-suggestions`);
}

export async function confirmVariant(bookId, baseBookId) {
  return request(`/teacher/books/${bookId}/variant-of`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_book_id: baseBookId }),
  });
}

export async function clearVariant(bookId) {
  return request(`/teacher/books/${bookId}/variant-of`, { method: "DELETE" });
}

// The chapter's prerequisite graph: { nodes, edges, report }.
export async function fetchChapterGraph(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}/graph`);
}

// Re-run processing on the already-uploaded file after a failure.
export async function retryChapter(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}/retry`, {
    method: "POST",
  });
}

// --- Student Endpoints ---

export async function fetchMyLinkedBooks() {
  return request("/student/books");
}

// Books this student may link: reference books + books of teachers whose room they joined.
export async function fetchStudentLibrary() {
  return request("/student/library");
}

export async function linkBook(bookId) {
  return request(`/student/books/${bookId}/link`, {
    method: "POST",
  });
}

export async function unlinkBook(bookId) {
  return request(`/student/books/${bookId}/link`, {
    method: "DELETE",
  });
}

export async function fetchChapterPages(bookId, chapterId) {
  return request(`/student/books/${bookId}/chapters/${chapterId}/pages`);
}

// --- Student: ask the teacher to add a chapter ---

export async function requestChapter(bookId, chapterHint) {
  return request(`/student/books/${bookId}/chapter-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chapter_hint: chapterHint }),
  });
}

export async function fetchMyRequests() {
  return request("/student/chapter-requests");
}

export async function cancelRequest(requestId) {
  return request(`/student/chapter-requests/${requestId}`, { method: "DELETE" });
}

// --- Delete (own books/chapters for teachers; official ones only for administrators) ---

export async function fetchMe() {
  return request("/auth/me");
}

export async function deleteMyBook(bookId) {
  return request(`/teacher/books/${bookId}`, { method: "DELETE" });
}

export async function deleteMyChapter(bookId, chapterId) {
  return request(`/teacher/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
}

export async function adminDeleteBook(bookId) {
  return request(`/admin/books/${bookId}`, { method: "DELETE" });
}

export async function adminDeleteChapter(bookId, chapterId) {
  return request(`/admin/books/${bookId}/chapters/${chapterId}`, { method: "DELETE" });
}

// "No, that is not the base of my book": the server remembers it and stops suggesting that book.
export async function dismissVariantSuggestion(bookId, baseBookId) {
  return request(`/teacher/books/${bookId}/variant-suggestions/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_book_id: baseBookId }),
  });
}
