import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ roles, adminOnly, children }) {
  const { user, loading, logout } = useAuth();

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

  // A teacher who signed up without an invite waits here until an administrator approves the account.
  if (user.status === "pending") {
    return (
      <div className="container" style={{ maxWidth: 480 }}>
        <div className="card stack">
          <h2>Waiting for approval</h2>
          <p>Thanks for signing up, {user.name}. An administrator has to approve teacher accounts before you can use Tuition Companion.
            Please check back later, or ask for an invite code.</p>
          <div><button className="btn secondary" onClick={logout}>Log out</button></div>
        </div>
      </div>
    );
  }

  if (adminOnly && !user.is_admin) {
    return <Navigate to="/" replace />;
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
