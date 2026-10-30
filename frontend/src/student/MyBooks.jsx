import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import {
  fetchMyLinkedBooks,
  fetchStudentLibrary,
  linkBook,
} from "../api/content";
import {
  approveParentLink,
  cancelRoomRequest,
  getMyRooms,
  joinRoom,
  leaveRoom,
  listMyRoomRequests,
  listParentLinks,
  removeParentLink,
  unlinkMyBook,
} from "../api/learning";
import Header from "../shared/Header";
import {
  Async,
  Empty,
  ErrorNote,
  bookLabel,
  useLoad,
  useSubmit,
} from "../shared/ui";
import StudentBookUpload from "./StudentBookUpload";

function Books({ linked, available, reload }) {
  const [pick, setPick] = useState("");
  const { busy, error, run } = useSubmit();
  return (
    <div className="card stack">
      <h2>My textbooks</h2>
      {linked.length === 0 ? (
        <Empty>
          You haven't linked a textbook yet. Pick one below to get started.
        </Empty>
      ) : (
        <div className="items">
          {linked.map((b) => (
            <div className="item" key={b.id}>
              <div className="row">
                <strong>{bookLabel(b)}</strong>
                {!b.is_reference ? (
                  <span className="small">Private to you</span>
                ) : (
                  <button
                    className="btn ghost small-btn"
                    disabled={busy}
                    onClick={() =>
                      window.confirm("Unlink this book? Your history is kept.") &&
                      run(async () => { await unlinkMyBook(b.id); reload(); })
                    }
                  >Unlink</button>
                )}
              </div>
              {b.chapters.length === 0 ? (
                <p className="small mb0">No chapters are ready to read yet.</p>
              ) : (
                <div className="chips mt">
                  {b.chapters.map((c) => (
                    <Link
                      key={c.id}
                      className="chip"
                      to={`/student/books/${b.id}/chapters/${c.id}`}
                    >
                      Ch {c.sequence_num}: {c.title}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      {available.length > 0 && (
        <div>
          <label htmlFor="link-book">Link a textbook</label>
          <select
            id="link-book"
            className="input"
            value={pick}
            disabled={busy}
            onChange={(e) => {
              const id = e.target.value;
              setPick("");
              run(async () => {
                await linkBook(id);
                reload();
              });
            }}
          >
            <option value="" disabled>
              Choose a book...
            </option>
            {available.map((b) => (
              <option key={b.id} value={b.id}>
                {b.board} · {bookLabel(b)}
                {b.is_reference ? " · official" : ""}
              </option>
            ))}
          </select>
        </div>
      )}
      <ErrorNote error={error} />
    </div>
  );
}

function Rooms({ rooms, reload }) {
  const [code, setCode] = useState("");
  const requests = useLoad(listMyRoomRequests);
  const { busy, error, run } = useSubmit();
  return (
    <div className="card stack">
      <h2>My rooms</h2>
      {rooms.length === 0 ? (
        <Empty>You haven't joined a room yet.</Empty>
      ) : (
        <div className="chips">
          {rooms.map((r) => (
            <span className="chip" key={r.id}>
              {r.name}
              <button type="button" className="btn ghost small-btn" disabled={busy} onClick={() => {
                if (window.confirm(`Leave ${r.name}? Your mastery history will be kept.`)) {
                  run(async () => { await leaveRoom(r.id); reload(); });
                }
              }}>Leave</button>
            </span>
          ))}
        </div>
      )}
      <form
        className="row gap-s"
        style={{ flexWrap: "nowrap" }}
        onSubmit={(e) => {
          e.preventDefault();
          run(async () => {
            await joinRoom(code.trim());
            setCode("");
            requests.reload();
          });
        }}
      >
        <div style={{ flex: 1 }}>
          <label htmlFor="join">Request to join a room with your teacher's code</label>
          <input
            id="join"
            className="input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
            minLength={6}
            maxLength={12}
            placeholder="Code from teacher"
          />
        </div>
        <button
          className="btn"
          style={{ alignSelf: "flex-end" }}
          disabled={busy}
        >
          Join
        </button>
      </form>
      <div className="stack">
        <h3 className="mb0">Pending requests</h3>
        <Async state={requests}>
          {(items) => items.length === 0 ? <p className="small mb0">No pending room requests.</p> : (
            <div className="items">{items.map((r) => (
              <div className="item row" key={r.id}>
                <div><strong>{r.room_name}</strong><div className="small">Waiting for teacher approval</div></div>
                <button type="button" className="btn ghost small-btn" disabled={busy} onClick={() => run(async () => { await cancelRoomRequest(r.room_id); requests.reload(); })}>Cancel request</button>
              </div>
            ))}</div>
          )}
        </Async>
      </div>
      <ErrorNote error={error} />
    </div>
  );
}

function ParentLinks() {
  const state = useLoad(listParentLinks);
  const { busy, error, run } = useSubmit();

  return (
    <div className="card stack">
      <h2>Parent access</h2>
      <p className="small mb0">
        A parent can only see your read-only progress after you approve their
        request. You can remove access at any time.
      </p>
      <Async state={state}>
        {(links) =>
          links.length === 0 ? (
            <p className="small mb0">No parent has requested access yet.</p>
          ) : (
            <div className="items">
              {links.map((link) => (
                <div className="item row" key={link.id}>
                  <div>
                    <strong>{link.parent_name}</strong>
                    <div className="small">
                      {link.parent_username} · {link.status}
                    </div>
                  </div>
                  <div className="row gap-s">
                    {link.status === "pending" && (
                      <button
                        className="btn small-btn"
                        disabled={busy}
                        onClick={() =>
                          run(async () => {
                            await approveParentLink(link.id);
                            state.reload();
                          })
                        }
                      >
                        Approve
                      </button>
                    )}
                    <button
                      className="btn ghost small-btn"
                      disabled={busy}
                      onClick={() =>
                        run(async () => {
                          await removeParentLink(link.id);
                          state.reload();
                        })
                      }
                    >
                      {link.status === "pending" ? "Reject" : "Remove"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )
        }
      </Async>
      <ErrorNote error={error} />
    </div>
  );
}

export default function MyBooks() {
  const { profile } = useAuth();
  const state = useLoad(async () => {
    const [linked, available, rooms] = await Promise.all([
      fetchMyLinkedBooks(),
      fetchStudentLibrary(),
      getMyRooms(),
    ]);
    return {
      linked: linked || [],
      available: available || [],
      rooms: rooms || [],
    };
  });
  return (
    <>
      <Header
        title="My Books"
        subtitle="Your textbooks, rooms and parent link code."
      />
      <div className="container">
        <Async state={state}>
          {({ linked, available, rooms }) => (
            <>
              <Books
                linked={linked}
                available={available}
                reload={state.reload}
              />
              <StudentBookUpload books={linked} reload={state.reload} />
              <Rooms rooms={rooms} reload={state.reload} />
              <ParentLinks />
              <div className="card">
                <h2>Parent link code</h2>
                <p className="small">
                  Give this code to your parent so they can follow your
                  progress. They can only view it, not change anything.
                </p>
                <span className="code">{profile?.link_code || "N/A"}</span>
              </div>
            </>
          )}
        </Async>
      </div>
    </>
  );
}
