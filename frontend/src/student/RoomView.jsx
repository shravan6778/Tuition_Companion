import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api";
import Header from "../shared/Header";

export default function RoomView() {
  const { roomId } = useParams();
  const [room, setRoom] = useState(null);
  const [subjects, setSubjects] = useState(null); // [{...subject, chapters: []}]
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api("/student/rooms"),
      api(`/student/rooms/${roomId}/subjects`),
    ])
      .then(async ([rooms, subs]) => {
        setRoom(rooms.find((r) => r.id === roomId) ?? null);
        const withChapters = await Promise.all(
          subs.map(async (s) => ({
            ...s,
            chapters: await api(
              `/student/rooms/${roomId}/subjects/${s.id}/chapters`,
            ),
          })),
        );
        setSubjects(withChapters);
      })
      .catch((e) => setError(e.message));
  }, [roomId]);

  return (
    <div className="container">
      <Link className="back-link" to="/student">
        ← Back to my learning
      </Link>
      <Header title={room ? room.name : "Room"} />
      {error && <div className="error">{error}</div>}

      {subjects && subjects.length === 0 && (
        <div className="card">
          <h3>Nothing here yet</h3>
          <p className="small">
            Your teacher hasn't added any subjects to this room.
          </p>
        </div>
      )}

      {subjects?.map((s) => (
        <div className="card" key={s.id}>
          <h3>{s.name}</h3>
          {s.chapters.length === 0 ? (
            <p className="small">
              Chapters will appear here once they're ready.
            </p>
          ) : (
            <ol>
              {s.chapters.map((c) => (
                <li key={c.id}>{c.title}</li>
              ))}
            </ol>
          )}
        </div>
      ))}
    </div>
  );
}
