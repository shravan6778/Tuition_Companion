import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ roles, children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>
        Verifying access...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Ensure case-insensitive role checking
  if (roles && roles.length > 0) {
    const userRole = user.role?.toLowerCase();
    const allowedRoles = roles.map((r) => r.toLowerCase());

    if (!allowedRoles.includes(userRole)) {
      // If a student tries to access /teacher, send them to / which will re-route them to /student
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
