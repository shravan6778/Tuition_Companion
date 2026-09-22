import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./auth/LoginPage.jsx";
import SignupPage from "./auth/SignupPage.jsx";
import ParentDashboard from "./parent/ParentDashboard.jsx";
import ProtectedRoute from "./shared/ProtectedRoute.jsx";
import Landing from "./shared/Landing.jsx";
import StudentDashboard from "./student/StudentDashboard.jsx";
import TeacherDashboard from "./teacher/TeacherDashboard.jsx";

const guard = (role, el) => (
  <ProtectedRoute roles={[role]}>{el}</ProtectedRoute>
);

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/teacher" element={guard("teacher", <TeacherDashboard />)} />
      <Route path="/student" element={guard("student", <StudentDashboard />)} />
      <Route path="/parent" element={guard("parent", <ParentDashboard />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
