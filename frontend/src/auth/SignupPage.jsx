import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function SignupPage() {
  const { signup } = useAuth();
  const nav = useNavigate();
  const [form, setForm] = useState({
    name: "",
    username: "",
    phone: "",
    password: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const me = await signup(form);
      nav(`/${me.role}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <form className="card stack" onSubmit={submit}>
        <h2>Create your account</h2>
        <div>
          <label htmlFor="role">I am a…</label>
          <select
            id="role"
            className="input"
            value={form.role}
            onChange={set("role")}
          >
            <option value="teacher">Teacher</option>
            <option value="student">Student</option>
            <option value="parent">Parent</option>
          </select>
        </div>
        <div>
          <label htmlFor="name">Full name</label>
          <input
            id="name"
            className="input"
            value={form.name}
            onChange={set("name")}
            required
            minLength={2}
          />
        </div>
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            className="input"
            value={form.username}
            onChange={set("username")}
            placeholder="lowercase, letters/numbers/_"
            required
            minLength={3}
            maxLength={30}
          />
          <span className="small">
            This is what you'll log in with. Each family member needs a
            different one, even if you share a phone.
          </span>
        </div>
        <div>
          <label htmlFor="phone">Phone number</label>
          <input
            id="phone"
            className="input"
            type="tel"
            value={form.phone}
            onChange={set("phone")}
            placeholder="+919876543210"
            required
          />
        </div>
        <div>
          <label htmlFor="pw">Password (min 8 characters)</label>
          <input
            id="pw"
            className="input"
            type="password"
            value={form.password}
            onChange={set("password")}
            required
            minLength={8}
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" type="submit">
          Sign up
        </button>
        <span className="small">
          Already have an account? <Link to="/login">Log in</Link>
        </span>
      </form>
    </div>
  );
}
