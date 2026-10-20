import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./auth/LoginPage.jsx";
import SignupPage from "./auth/SignupPage.jsx";
import ParentDashboard from "./parent/ParentDashboard.jsx";
import ProtectedRoute from "./shared/ProtectedRoute.jsx";
import Landing from "./shared/Landing.jsx";
import TodayWork from "./student/TodayWork.jsx";
import AskDoubt from "./student/AskDoubt.jsx";
import Practice from "./student/Practice.jsx";
import Progress from "./student/Progress.jsx";
import MyBooks from "./student/MyBooks.jsx";
import ChapterReader from "./student/ChapterReader.jsx";
import CheckPage from "./student/CheckPage.jsx";
import QuizPage from "./student/QuizPage.jsx";
import TeacherDashboard from "./teacher/TeacherDashboard.jsx";
import RoomDetail from "./teacher/RoomDetail.jsx";
import StudentHub from "./teacher/StudentHub.jsx";
import TestsPage from "./teacher/TestsPage.jsx";

// Phase 2 content library
import TeacherLibrary from "./teacher/TeacherLibrary.jsx";

const guard = (role, el) => (
  <ProtectedRoute roles={[role]}>{el}</ProtectedRoute>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Teacher Routes */}
      <Route path="/teacher" element={guard("teacher", <TeacherDashboard />)} />
      <Route
        path="/teacher/rooms/:roomId"
        element={guard("teacher", <RoomDetail />)}
      />
      <Route
        path="/teacher/rooms/:roomId/students/:studentId"
        element={guard("teacher", <StudentHub />)}
      />
      <Route path="/teacher/tests" element={guard("teacher", <TestsPage />)} />
      <Route
        path="/teacher/library"
        element={guard("teacher", <TeacherLibrary />)}
      />

      {/* Student Routes */}
      <Route path="/student" element={guard("student", <TodayWork />)} />
      <Route path="/student/doubts" element={guard("student", <AskDoubt />)} />
      <Route path="/student/practice" element={guard("student", <Practice />)} />
      <Route path="/student/progress" element={guard("student", <Progress />)} />
      <Route path="/student/books" element={guard("student", <MyBooks />)} />
      <Route path="/student/books/:bookId/chapters/:chapterId" element={guard("student", <ChapterReader />)} />
      <Route path="/student/checks/:checkId" element={guard("student", <CheckPage />)} />
      <Route path="/student/quizzes/:quizId" element={guard("student", <QuizPage />)} />

      {/* Parent Routes */}
      <Route path="/parent" element={guard("parent", <ParentDashboard />)} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
