import { NavLink, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const NAV = {
  teacher: [
    ["/teacher", "Rooms", true],
    ["/teacher/library", "Content Library"],
    ["/teacher/tests", "Tests"],
  ],
  student: [
    ["/student", "Today's Work", true],
    ["/student/doubts", "Ask a Doubt"],
    ["/student/practice", "Practice Test"],
    ["/student/progress", "My Progress"],
    ["/student/books", "My Books"],
  ],
  parent: [["/parent", "My Children", true]],
};

// App bar with role navigation, then an optional page title.
export default function Header({ title, subtitle }) {
  const { profile, logout } = useAuth();
  const role = profile?.role?.toLowerCase();
  const links = NAV[role] || [];
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <Link to="/" className="brand">Tuition Companion</Link>
          <nav className="nav" aria-label="Main">
            {links.map(([to, label, end]) => (
              <NavLink key={to} to={to} end={!!end} className={({ isActive }) => (isActive ? "active" : "")}>
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="who">
            <span>{profile?.name}</span>
            <button className="btn secondary small-btn" onClick={logout}>Log out</button>
          </div>
        </div>
      </header>
      {title && (
        <div className="container pagehead">
          <h1>{title}</h1>
          {subtitle && <p className="muted mb0">{subtitle}</p>}
        </div>
      )}
    </>
  );
}
