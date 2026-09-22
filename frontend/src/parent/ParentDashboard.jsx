import { useEffect, useState } from "react";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function ParentDashboard() {
  const [children, setChildren] = useState(null);
  const [code, setCode] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api("/parent/children")
      .then(setChildren)
      .catch((e) => setError(e.message));
  useEffect(() => {
    load();
  }, []);

  async function link(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/parent/link", { method: "POST", body: { link_code: code } });
      setCode("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container stack">
      <Header title="My children" />

      <form className="card stack" onSubmit={link}>
        <h3>Link a student</h3>
        <label htmlFor="lc">Link code (from your child's dashboard)</label>
        <input
          id="lc"
          className="input"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          required
        />
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Link
        </button>
      </form>

      {children?.length === 0 && (
        <div className="card">
          <p className="small">No children linked yet.</p>
        </div>
      )}
      {children?.map((c) => (
        <div className="card" key={c.id}>
          <h3>{c.name}</h3>
          <p className="small">
            {c.rooms.length
              ? `In: ${c.rooms.map((r) => r.name).join(", ")}`
              : "Not in any room yet"}
          </p>
        </div>
      ))}
    </div>
  );
}
