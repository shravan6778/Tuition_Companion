import { useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { bulkLinkBook, fetchBooks } from "../api/content";
import { listMembers, listRooms, listTeacherBooks } from "../api/learning";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, Tabs, bookLabel, fmtDate, useLoad, useSubmit } from "../shared/ui";
import AssignmentForm from "./AssignmentForm";
import AssignmentList from "./AssignmentList";
import QuizPanel from "./QuizPanel";
import { STUDENT_TABS } from "./StudentTabConfig";

const ROOM_TABS = [["students", "Students"], ["work", "Assigned Work"], ["tests", "Tests"], ["library", "Content Library"]];

function Students({ roomId }) {
  const state = useLoad(() => listMembers(roomId), [roomId]);
  return (
    <Async state={state}>
      {(members) => members.length === 0 ? (
        <div className="card"><Empty><p><strong>No students yet.</strong></p><p className="mb0">Share this room's join code. Students enter it under My Books.</p></Empty></div>
      ) : (
        <div className="stack">
          {members.map((m) => (
            <div className="card mb0" key={m.id}>
              <div className="row">
                <div><h3 className="mb0">{m.name}</h3><div className="small">Joined {fmtDate(m.joined_at)}</div></div>
              </div>
              <div className="chips mt" role="group" aria-label={`Tools for ${m.name}`}>
                {STUDENT_TABS.map(([id, label]) => (
                  <Link key={id} className="chip" to={`/teacher/rooms/${roomId}/students/${m.id}?tab=${id}`}>{label}</Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </Async>
  );
}

function Work({ roomId }) {
  const books = useLoad(listTeacherBooks);
  const [n, setN] = useState(0);
  return (
    <div className="stack">
      <Async state={books}>{(list) => <AssignmentForm books={list} roomId={roomId} onCreated={() => setN(n + 1)} />}</Async>
      <AssignmentList roomId={roomId} refreshKey={n} />
    </div>
  );
}

// Search the platform-wide library, link a book to everyone in the room, or go upload one that's missing.
function Library({ room }) {
  const [q, setQ] = useState("");
  const [term, setTerm] = useState("");
  const state = useLoad(() => fetchBooks(term ? { q: term } : {}), [term]);
  const [notes, setNotes] = useState({});
  const { busy, error, run } = useSubmit();
  const single = room.room_type === "single_class";

  const link = (b) =>
    run(async () => {
      const r = await bulkLinkBook(room.id, b.id);
      setNotes((n) => ({ ...n, [b.id]: `Linked for ${r.linked} student${r.linked === 1 ? "" : "s"}${r.already_linked ? `, ${r.already_linked} already had it` : ""}. Students who join later link it themselves.` }));
    });

  return (
    <div className="stack">
      {!single && <div className="callout info">This is a mixed class room, so books can't be linked to everyone at once. Students link the books they need themselves.</div>}
      <form className="row gap-s" style={{ flexWrap: "nowrap" }} onSubmit={(e) => { e.preventDefault(); setTerm(q.trim()); }}>
        <div style={{ flex: 1 }}>
          <label htmlFor="lib-q">Search the library</label>
          <input id="lib-q" className="input" value={q} placeholder="e.g. class 9 science ncert" onChange={(e) => setQ(e.target.value)} />
        </div>
        <button className="btn" style={{ alignSelf: "flex-end" }}>Search</button>
      </form>
      <ErrorNote error={error} />
      <Async state={state}>
        {(books) => books.length === 0 ? (
          <div className="card"><Empty><p><strong>{term ? "No book matches that search." : "The library is empty."}</strong></p><p className="mb0">Can't find yours? <Link to="/teacher/library">Upload it in the Content Library</Link>.</p></Empty></div>
        ) : (
          <div className="card items mb0">
            {books.map((b) => {
              const ready = b.chapters.filter((c) => c.status === "ready").length;
              return (
                <div className="item" key={b.id}>
                  <div className="row">
                    <div>
                      <strong>{b.board} · {bookLabel(b)}{b.edition ? `, ${b.edition}` : ""}</strong>
                      <div className="small">{b.is_reference ? "Official" : "Yours"} · {ready} of {b.chapters.length} chapters ready</div>
                    </div>
                    {single && <button className="btn secondary small-btn" disabled={busy} onClick={() => link(b)}>Link to this room</button>}
                  </div>
                  {notes[b.id] && <div className="callout ok mt" role="status">{notes[b.id]}</div>}
                </div>
              );
            })}
          </div>
        )}
      </Async>
      <p className="small">Upload new books, add chapters and review the concept map in the <Link to="/teacher/library">full Content Library</Link>.</p>
    </div>
  );
}

export default function RoomDetail() {
  const { roomId } = useParams();
  const [params, setParams] = useSearchParams();
  const tab = ROOM_TABS.some(([id]) => id === params.get("tab")) ? params.get("tab") : "students";
  const rooms = useLoad(listRooms);
  const room = rooms.data?.find((r) => r.id === roomId);

  return (
    <>
      <Header title={room?.name || "Room"} subtitle={room ? `${room.member_count} student${room.member_count === 1 ? "" : "s"} · join code ${room.join_code}` : ""} />
      <div className="container">
        <Link to="/teacher" className="back-link">← All rooms</Link>
        <Async state={rooms}>
          {() => room ? (
            <>
              <Tabs tabs={ROOM_TABS} value={tab} onChange={(t) => setParams({ tab: t }, { replace: true })} />
              {tab === "students" && <Students roomId={roomId} />}
              {tab === "work" && <Work roomId={roomId} />}
              {tab === "tests" && <QuizPanel target={{ room_id: roomId }} />}
              {tab === "library" && <Library room={room} />}
            </>
          ) : <div className="callout warn">Room not found.</div>}
        </Async>
      </div>
    </>
  );
}
