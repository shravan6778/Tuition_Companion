import { Navigate, Route, Routes } from "react-router-dom";
import LoginPage from "./auth/LoginPage.jsx";
import SignupPage from "./auth/SignupPage.jsx";
import ParentDashboard from "./parent/ParentDashboard.jsx";
import ProtectedRoute from "./shared/ProtectedRoute.jsx";
import Landing from "./shared/Landing.jsx";
import StudentDashboard from "./student/StudentDashboard.jsx";
import RoomView from "./student/RoomView.jsx";
import TeacherDashboard from "./teacher/TeacherDashboard.jsx";
import Library from "./teacher/Library.jsx";
import SubjectDetail from "./teacher/SubjectDetail.jsx";
import RoomDetail from "./teacher/RoomDetail.jsx";

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
      <Route path="/teacher/library" element={guard("teacher", <Library />)} />
      <Route
        path="/teacher/library/:subjectId"
        element={guard("teacher", <SubjectDetail />)}
      />
      <Route
        path="/teacher/rooms/:roomId"
        element={guard("teacher", <RoomDetail />)}
      />
      <Route path="/student" element={guard("student", <StudentDashboard />)} />
      <Route
        path="/student/rooms/:roomId"
        element={guard("student", <RoomView />)}
      />
      <Route path="/parent" element={guard("parent", <ParentDashboard />)} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
