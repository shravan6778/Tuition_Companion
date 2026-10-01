import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./auth/LoginPage.jsx";
import SignupPage from "./auth/SignupPage.jsx";
import ParentDashboard from "./parent/ParentDashboard.jsx";
import ProtectedRoute from "./shared/ProtectedRoute.jsx";
import Landing from "./shared/Landing.jsx";
import StudentDashboard from "./student/StudentDashboard.jsx";
import TeacherDashboard from "./teacher/TeacherDashboard.jsx";
import RoomDetail from "./teacher/RoomDetail.jsx";

// Phase 2 Content Pipeline Components
import TeacherLibrary from "./components/TeacherLibrary.jsx";
import StudentDoubtUpload from "./components/StudentDoubtUpload.jsx";
import TeacherVerificationQueue from "./components/TeacherVerificationQueue.jsx";

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
        path="/teacher/library"
        element={guard("teacher", <TeacherLibrary />)}
      />
      <Route
        path="/teacher/verification"
        element={guard("teacher", <TeacherVerificationQueue />)}
      />

      {/* Student Routes */}
      <Route path="/student" element={guard("student", <StudentDashboard />)} />
      <Route
        path="/student/doubt"
        element={guard("student", <StudentDoubtUpload />)}
      />

      {/* Parent Routes */}
      <Route path="/parent" element={guard("parent", <ParentDashboard />)} />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
