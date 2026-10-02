import React from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Landing() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ padding: "2rem", textAlign: "center" }}>Loading...</div>
    );
  }

  // INTERCEPT: If the user is logged in, auto-redirect them to their specific dashboard
  if (user && user.role) {
    const role = user.role.toLowerCase();
    if (role === "teacher") return <Navigate to="/teacher" replace />;
    if (role === "student") return <Navigate to="/student" replace />;
    if (role === "parent") return <Navigate to="/parent" replace />;
  }

  return (
    <div
      style={{
        textAlign: "center",
        padding: "4rem 1rem",
        fontFamily: "sans-serif",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>
        Welcome to Tuition Companion
      </h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        The complete platform for teachers, students, and parents.
      </p>

      <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
        <Link
          to="/login"
          style={{
            padding: "0.8rem 1.5rem",
            background: "#0070f3",
            color: "white",
            textDecoration: "none",
            borderRadius: "5px",
            fontWeight: "bold",
          }}
        >
          Login
        </Link>
        <Link
          to="/signup"
          style={{
            padding: "0.8rem 1.5rem",
            background: "#eaeaea",
            color: "black",
            textDecoration: "none",
            borderRadius: "5px",
            fontWeight: "bold",
          }}
        >
          Sign Up
        </Link>
      </div>
    </div>
  );
}
