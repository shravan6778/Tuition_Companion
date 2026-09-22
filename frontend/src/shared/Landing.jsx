import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="container stack">
      <h1>Tuition Companion</h1>
      <p>
        Doubts answered, homework verified, weak areas tracked, for teachers,
        students and parents.
      </p>
      <div className="row" style={{ justifyContent: "flex-start" }}>
        <Link className="btn" to="/signup">
          Get started
        </Link>
        <Link className="btn secondary" to="/login">
          Log in
        </Link>
      </div>
    </div>
  );
}
