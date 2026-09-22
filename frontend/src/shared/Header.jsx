import { useAuth } from "../auth/AuthContext";

export default function Header({ title }) {
  const { profile, logout } = useAuth();
  return (
    <div className="row" style={{ marginBottom: 16 }}>
      <div>
        <h1>{title}</h1>
        <span className="small">Signed in as {profile.name}</span>
      </div>
      <button className="btn secondary" onClick={logout}>
        Log out
      </button>
    </div>
  );
}
