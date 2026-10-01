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

export async function fetchUnverifiedPages() {
  return request("/teacher/pages/unverified");
}

export async function verifyPage(pageId) {
  return request(`/teacher/pages/${pageId}/verify`, {
    method: "POST",
  });
}

// --- Student Endpoints ---

export async function fetchMyLinkedBooks() {
  return request("/student/books");
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

export async function uploadStudentDoubtPage(bookId, chapterId, file) {
  const formData = new FormData();
  formData.append("file", file);

  return request(`/student/books/${bookId}/chapters/${chapterId}/doubt-upload`, {
    method: "POST",
    body: formData,
  });
}