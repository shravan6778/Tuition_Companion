import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ roles, children }) {
  const { profile, loading } = useAuth();
  if (loading) return <div className="container">Loading…</div>;
  if (!profile) return <Navigate to="/login" replace />;
  if (!roles.includes(profile.role))
    return <Navigate to={`/${profile.role}`} replace />;
  return children;
}
