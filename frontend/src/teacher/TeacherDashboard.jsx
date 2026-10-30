import { useState } from "react";
import { Link } from "react-router-dom";
import { createRoom, listRooms } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, useLoad, useSubmit } from "../shared/ui";

export default function TeacherDashboard() {
  const state = useLoad(listRooms);
  const [name, setName] = useState("");
  const [type, setType] = useState("single_class");
  const { busy, error, run } = useSubmit();

  const create = (e) => {
    e.preventDefault();
    run(async () => { await createRoom(name.trim(), type); setName(""); state.reload(); });
  };

  return (
    <>
      <Header title="Your rooms" subtitle="A room groups students. Open one to see its students, assign work and inspect textbook outlines." />
      <div className="container">
        <Async state={state}>
          {(rooms) => (
            <>
              <div className="tiles">
                <div className="tile"><div className="num">{rooms.length}</div><div className="lbl">Rooms</div></div>
                <div className="tile"><div className="num">{rooms.reduce((n, r) => n + r.member_count, 0)}</div><div className="lbl">Students</div></div>
              </div>

              <div className="grid2" style={{ marginBottom: 16 }}>
                {rooms.length === 0 && <div className="card mb0" style={{ gridColumn: "1 / -1" }}><Empty><p><strong>No rooms yet.</strong></p><p className="mb0">Create your first room below, then share its join code with your students.</p></Empty></div>}
                {rooms.map((r) => (
                  <div className="card mb0" key={r.id}>
                    <div className="row" style={{ alignItems: "flex-start" }}>
                      <div>
                        <h3 className="mb0"><Link to={`/teacher/rooms/${r.id}`} style={{ textDecoration: "none" }}>{r.name}</Link></h3>
                        <div className="small">{r.room_type === "single_class" ? "Single class" : "Mixed class"} · {r.member_count} student{r.member_count === 1 ? "" : "s"}</div>
                      </div>
                      <Link className="btn secondary small-btn" to={`/teacher/rooms/${r.id}`}>Open</Link>
                    </div>
                    <div className="mt small">Join code</div>
                    <span className="code">{r.join_code}</span>
                  </div>
                ))}
              </div>

              <form className="card stack" onSubmit={create}>
                <h3>Create a room</h3>
                <div className="grid2">
                  <div><label htmlFor="rn">Room name</label><input id="rn" className="input" value={name} required minLength={2} maxLength={100} placeholder="e.g. Class 9 Science" onChange={(e) => setName(e.target.value)} /></div>
                  <div>
                    <label htmlFor="rt">Room type</label>
                    <select id="rt" className="input" value={type} onChange={(e) => setType(e.target.value)}>
                      <option value="single_class">Single class (one grade)</option>
                      <option value="mixed_class">Mixed class (several grades)</option>
                    </select>
                  </div>
                </div>
                <ErrorNote error={error} />
                <div><button className="btn" disabled={busy}>{busy ? "Creating..." : "Create room"}</button></div>
              </form>
            </>
          )}
        </Async>
      </div>
    </>
  );
}
