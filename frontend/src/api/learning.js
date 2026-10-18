// API calls for Phases 3-7: assignments, doubts, checks, quizzes, mastery, analytics, parent digest.
// Every function resolves to the response body (null for 204).
import api from "../shared/api";

const body = (p) => p.then((r) => r.data);
const qs = (params = {}) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== "")).toString();
  return q ? `?${q}` : "";
};

// ---- student: today's work, checks ----
export const getTodaysWork = () => body(api.get("/student/assignments"));
export const startCheck = (assignmentId) => body(api.post(`/student/assignments/${assignmentId}/complete`));
export const listChecks = () => body(api.get("/student/checks"));
export const getCheck = (id) => body(api.get(`/student/checks/${id}`));
export const submitCheck = (id, answers) => body(api.post(`/student/checks/${id}/submit`, { answers }));

// ---- student: doubts ----
export const askDoubt = (payload) => body(api.post("/student/doubts", payload));
export const askDoubtPhoto = (file, { assignmentId, chapterId } = {}) => {
  const fd = new FormData();
  fd.append("file", file);
  if (assignmentId) fd.append("assignment_id", assignmentId);
  if (chapterId) fd.append("chapter_id", chapterId);
  return body(api.post("/student/doubts/photo", fd));
};
export const myDoubts = (assignmentId) => body(api.get(`/student/doubts${qs({ assignment_id: assignmentId })}`));
export const browseForDoubts = () => body(api.get("/student/doubts/browse"));
export const postPath = (path, payload) => body(api.post(path, payload));

// ---- student: quizzes and practice ----
export const listMyQuizzes = () => body(api.get("/student/quizzes"));
export const getMyQuiz = (id) => body(api.get(`/student/quizzes/${id}`));
export const submitQuiz = (id, answers) => body(api.post(`/student/quizzes/${id}/submit`, { answers }));
export const generatePractice = (payload) => body(api.post("/student/practice/generate", payload));

// ---- student: mastery ----
export const getMastery = () => body(api.get("/student/mastery"));
export const getMasteryEvents = () => body(api.get("/student/mastery/events"));

// ---- student: reading ----
export const getMyBook = (bookId) => body(api.get(`/student/books/${bookId}`));
export const getChapterPages = (bookId, chapterId) => body(api.get(`/student/books/${bookId}/chapters/${chapterId}/pages`));
export const getStudentChapterGraph = (bookId, chapterId) => body(api.get(`/student/books/${bookId}/chapters/${chapterId}/graph`));
export const getMyRooms = () => body(api.get("/student/rooms"));
export const joinRoom = (code) => body(api.post("/student/rooms/join", { join_code: code }));
export const unlinkMyBook = (bookId) => body(api.delete(`/student/books/${bookId}/link`));

// ---- teacher: rooms ----
export const listRooms = () => body(api.get("/teacher/rooms"));
export const createRoom = (name, roomType) => body(api.post("/teacher/rooms", { name, room_type: roomType }));
export const listMembers = (roomId) => body(api.get(`/teacher/rooms/${roomId}/members`));

// ---- teacher: assignments ----
export const listAssignments = (params) => body(api.get(`/teacher/assignments${qs(params)}`));
export const createAssignment = (payload) => body(api.post("/teacher/assignments", payload));
export const deleteAssignment = (id) => body(api.delete(`/teacher/assignments/${id}`));
export const exerciseProposal = (payload) => body(api.post("/teacher/assignments/exercise-proposal", payload));
export const assignmentDoubts = (id, studentId) => body(api.get(`/teacher/assignments/${id}/doubts${qs({ student_id: studentId })}`));

// ---- teacher: books ----
export const listTeacherBooks = () => body(api.get("/teacher/books"));

// ---- teacher: quizzes ----
export const generateTeacherQuiz = (payload) => body(api.post("/teacher/quizzes/generate", payload));
export const listTeacherQuizzes = (params) => body(api.get(`/teacher/quizzes${qs(params)}`));
export const getTeacherQuiz = (id) => body(api.get(`/teacher/quizzes/${id}`));
export const assignTeacherQuiz = (id, payload) => body(api.post(`/teacher/quizzes/${id}/assign`, payload));
export const deleteTeacherQuiz = (id) => body(api.delete(`/teacher/quizzes/${id}`));

// ---- teacher: per-student ----
export const getTrends = (studentId, weeks) => body(api.get(`/teacher/students/${studentId}/trends${qs({ weeks })}`));
export const getBriefing = (studentId, refresh) => body(api.get(`/teacher/students/${studentId}/briefing${refresh ? "?refresh=true" : ""}`));
export const listSessions = (studentId) => body(api.get(`/teacher/students/${studentId}/sessions`));
export const addSession = (studentId, payload) => body(api.post(`/teacher/students/${studentId}/sessions`, payload));

// ---- parent ----
export const listChildren = () => body(api.get("/parent/children"));
export const linkChild = (code) => body(api.post("/parent/link", { link_code: code }));
export const getChildProgress = (childId, days = 7) => body(api.get(`/parent/children/${childId}/progress?days=${days}`));
