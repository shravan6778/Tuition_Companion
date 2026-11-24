import { useState } from "react";
import * as admin from "../api/admin";
import Header from "../shared/Header";
import { Async, Empty, ErrorNote, Pill, Tabs, fmtDateTime, useLoad, useSubmit } from "../shared/ui";

const QUOTA_LABEL = {
  llm_tokens: "AI text (tokens)",
  ocr_pages: "Page reading (pages)",
  embedding_tokens: "Search index (tokens)",
  speech_calls: "Voice (calls)",
};
const n = (v) => (v == null ? "-" : Number(v).toLocaleString());
const cap = (v) => (v ? n(v) : "no limit");

export default function AdminDashboard() {
  const [tab, setTab] = useState("status");
  return (
    <>
      <Header title="Administration" subtitle="People, failed chapters, AI usage, invites, the audit log and system status." />
      <div className="container">
        <Tabs
          value={tab}
          onChange={setTab}
          tabs={[["status", "Status"], ["people", "People"], ["chapters", "Failed chapters"], ["usage", "AI usage"], ["invites", "Teacher invites"], ["audit", "Audit log"]]}
        />
        {tab === "status" && <StatusTab />}
        {tab === "people" && <PeopleTab />}
        {tab === "chapters" && <ChaptersTab />}
        {tab === "usage" && <UsageTab />}
        {tab === "invites" && <InvitesTab />}
        {tab === "audit" && <AuditTab />}
      </div>
    </>
  );
}

// ---- status -----------------------------------------------------------------------------------------------

function Component({ name, c }) {
  const kind = c.ok === true ? "ok" : c.ok === false ? "failed" : "stable";
  const label = c.ok === true ? "Working" : c.ok === false ? "Down" : "Off";
  return (
    <tr>
      <td>{name}</td>
      <td><Pill kind={kind}>{label}</Pill></td>
      <td className="small">{c.latency_ms != null ? `${c.latency_ms} ms` : ""}</td>
      <td className="small">{typeof c.detail === "string" ? c.detail : c.detail ? JSON.stringify(c.detail) : ""}</td>
    </tr>
  );
}

function StatusTab() {
  const state = useLoad(admin.getStatus);
  return (
    <Async state={state}>
      {(s) => (
        <>
          <div className={`callout ${s.overall === "ok" ? "ok" : s.overall === "down" ? "warn" : "risk"}`} role="status">
            <strong>System is {s.overall === "ok" ? "healthy" : s.overall}.</strong> Checked {fmtDateTime(s.checked_at)}.{" "}
            <button className="btn link" onClick={state.reload}>Check again</button>
          </div>
          <div className="tiles mt">
            <div className={`tile ${s.chapters?.failed ? "weak" : "ok"}`}><div className="num">{s.chapters?.failed ?? "-"}</div><div className="lbl">Failed chapters</div></div>
            <div className={`tile ${s.chapters?.stuck ? "risk" : ""}`}><div className="num">{s.chapters?.stuck ?? "-"}</div><div className="lbl">Stuck chapters</div></div>
            <div className={`tile ${s.traffic.error_rate >= 0.05 ? "weak" : "ok"}`}><div className="num">{(s.traffic.error_rate * 100).toFixed(1)}%</div><div className="lbl">Server errors, last {s.traffic.window_minutes} min ({s.traffic.requests} requests)</div></div>
            <div className={`tile ${s.people?.pending_teachers ? "risk" : ""}`}><div className="num">{s.people?.pending_teachers ?? "-"}</div><div className="lbl">Teachers waiting</div></div>
          </div>
          <div className="card tablewrap">
            <h3>Services</h3>
            <table className="table">
              <thead><tr><th>Service</th><th>State</th><th>Reply time</th><th>Detail</th></tr></thead>
              <tbody>
                <Component name="Database (PostgreSQL)" c={s.components.database} />
                <Component name="Login service (SuperTokens)" c={s.components.supertokens} />
                <Component name="Knowledge graph (Memgraph)" c={s.components.memgraph} />
              </tbody>
            </table>
            <p className="small mt mb0">Error rate and request counts are for this API process only and reset when it restarts.</p>
          </div>
          {s.ai && (
            <div className="card">
              <h3>AI and data safety</h3>
              <div className="stack">
                <div>AI kill switch: {s.ai.kill_switch.engaged ? <Pill kind="failed">ON — all AI calls refused</Pill> : <Pill kind="ok">off</Pill>}</div>
                <div>
                  Student data sent to the AI provider ({s.ai.llm_provider}): {s.ai.llm_no_training_confirmed
                    ? <Pill kind="ok">confirmed no-training plan</Pill>
                    : <Pill kind="at_risk">not confirmed — do not use real students' data on a free tier that trains on inputs</Pill>}
                </div>
                <div className="small">Today: {Object.entries(s.ai.usage_today).map(([q, v]) => `${QUOTA_LABEL[q]}: ${n(v)}`).join(" · ")}</div>
                <div className="small">
                  Teacher signup: <strong>{s.monitoring.teacher_signup_mode}</strong> · SuperTokens API key: {s.monitoring.supertokens_api_key_set ? "set" : <strong>NOT set</strong>} ·
                  Uptime heartbeat: {s.monitoring.uptime_ping_configured ? "configured" : "not configured"}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </Async>
  );
}

// ---- people -----------------------------------------------------------------------------------------------

function PeopleTab() {
  const [q, setQ] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState("");
  const state = useLoad(() => admin.listUsers({ q, role, status, limit: 100 }), [q, role, status]);
  const { busy, error, setError, run } = useSubmit();
  const [msg, setMsg] = useState("");

  const act = (fn, done) => run(async () => { await fn(); setMsg(done); state.reload(); });
  const disable = (u) => {
    const reason = window.prompt(`Disable ${u.username}? Their sessions end and every request is refused. Reason (optional):`, "");
    if (reason !== null) act(() => admin.disableUser(u.id, reason || null), `${u.username} is disabled and signed out.`);
  };
  const reject = (u) => window.confirm(`Reject ${u.username}? Their account is removed.`) && act(() => admin.rejectUser(u.id), `${u.username} was rejected.`);
  const caps = (u) => {
    const cur = u.caps.llm_tokens;
    const v = window.prompt(`Daily AI text cap for ${u.username} (tokens; 0 = unlimited; blank = back to default). Now: ${cur || "unlimited"}`, "");
    if (v === null) return;
    act(() => admin.setUserCaps(u.id, { llm_tokens: v.trim() === "" ? null : Math.max(0, parseInt(v, 10) || 0) }), `Cap updated for ${u.username}.`);
  };
  const remove = (u) => run(async () => {
    const p = await admin.deletePreview(u.id);
    const summary = `${p.own_books} own books (${p.own_chapters} chapters), ${p.rooms_owned} rooms, ${p.doubts} doubts, ${p.mastery_records} mastery records, ${p.assignments_made} assignments`;
    const typed = window.prompt(`DELETE ${u.username} and all their data: ${summary}.\nThis cannot be undone. Type the username to confirm:`);
    if (typed === null) return;
    await admin.deleteUser(u.id, typed);
    setMsg(`${u.username} and their data were deleted.`);
    state.reload();
  });

  return (
    <>
      <div className="card">
        <div className="grid2">
          <div><label htmlFor="uq">Search name or username</label><input id="uq" className="input" value={q} onChange={(e) => setQ(e.target.value)} /></div>
          <div className="row" style={{ alignItems: "flex-end" }}>
            <div style={{ flex: 1 }}><label htmlFor="ur">Role</label>
              <select id="ur" className="input" value={role} onChange={(e) => setRole(e.target.value)}><option value="">All</option><option value="teacher">Teachers</option><option value="student">Students</option><option value="parent">Parents</option></select></div>
            <div style={{ flex: 1 }}><label htmlFor="us">Status</label>
              <select id="us" className="input" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">All</option><option value="active">Active</option><option value="pending">Waiting for approval</option><option value="disabled">Disabled</option></select></div>
          </div>
        </div>
      </div>
      {msg && <div className="callout ok mb0" role="status" style={{ marginBottom: 16 }}>{msg}</div>}
      <ErrorNote error={error} onRetry={() => setError("")} />
      <Async state={state}>
        {(r) => (
          <div className="card tablewrap">
            <div className="small" style={{ marginBottom: 8 }}>{r.total} user{r.total === 1 ? "" : "s"}</div>
            {r.items.length === 0 ? <Empty>No one matches.</Empty> : (
              <table className="table">
                <thead><tr><th>Person</th><th>Role</th><th>Status</th><th>AI today</th><th>Actions</th></tr></thead>
                <tbody>
                  {r.items.map((u) => (
                    <tr key={u.id}>
                      <td><strong>{u.name}</strong><div className="small">{u.username} · {u.phone_masked}{u.is_admin ? " · admin" : ""}</div></td>
                      <td>{u.role}</td>
                      <td>{u.status === "active" ? <Pill kind="ok">Active</Pill> : u.status === "pending" ? <Pill kind="at_risk">Waiting</Pill> : <Pill kind="failed">Disabled</Pill>}</td>
                      <td className="small">{n(u.usage_today.llm_tokens || 0)} / {cap(u.caps.llm_tokens)} tokens<br />{n(u.usage_today.ocr_pages || 0)} / {cap(u.caps.ocr_pages)} pages</td>
                      <td>
                        <div className="chips">
                          {u.status === "pending" && <><button className="btn small-btn" disabled={busy} onClick={() => act(() => admin.approveUser(u.id), `${u.username} approved.`)}>Approve</button>
                            <button className="btn danger small-btn" disabled={busy} onClick={() => reject(u)}>Reject</button></>}
                          {u.status === "active" && !u.is_admin && <button className="btn secondary small-btn" disabled={busy} onClick={() => disable(u)}>Disable</button>}
                          {u.status === "disabled" && <button className="btn secondary small-btn" disabled={busy} onClick={() => act(() => admin.enableUser(u.id), `${u.username} enabled.`)}>Enable</button>}
                          {u.status !== "pending" && <button className="btn ghost small-btn" disabled={busy} onClick={() => caps(u)}>AI cap</button>}
                          {!u.is_admin && u.status !== "pending" && <button className="btn danger small-btn" disabled={busy} onClick={() => remove(u)}>Delete…</button>}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </Async>
    </>
  );
}

// ---- failed chapters ---------------------------------------------------------------------------------------

function ChaptersTab() {
  const state = useLoad(admin.failedChapters);
  const { busy, error, run } = useSubmit();
  const [note, setNote] = useState("");
  return (
    <>
      <ErrorNote error={error} />
      {note && <div className="callout ok" style={{ marginBottom: 16 }} role="status">{note}</div>}
      <Async state={state}>
        {(rows) => rows.length === 0 ? <div className="card"><Empty>No failed or stuck chapters.</Empty></div> : (
          <div className="card tablewrap">
            <table className="table">
              <thead><tr><th>Chapter</th><th>Owner</th><th>Why</th><th /></tr></thead>
              <tbody>
                {rows.map((c) => (
                  <tr key={c.id}>
                    <td><strong>{c.title}</strong><div className="small">{c.book_label}{c.is_reference ? " · official" : ""}</div></td>
                    <td className="small">{c.owner_name ? `${c.owner_name} (${c.owner_username})` : "Official library"}</td>
                    <td><Pill kind={c.state === "failed" ? "failed" : "processing"}>{c.state === "failed" ? "Failed" : "Stuck"}</Pill>
                      <div className="small">{c.error_message || "Stopped while processing (the server may have restarted)."}</div>
                      <div className="small">{fmtDateTime(c.processing_started_at)}</div></td>
                    <td>{c.can_retry
                      ? <button className="btn small-btn" disabled={busy} onClick={() => run(async () => { await admin.retryChapter(c.id); setNote(`"${c.title}" is being processed again.`); state.reload(); })}>Retry</button>
                      : <span className="small">Upload lost: ask the owner to upload again</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Async>
    </>
  );
}

// ---- AI usage ------------------------------------------------------------------------------------------------

function UsageTab() {
  const state = useLoad(() => admin.getUsage(7));
  const status = useLoad(admin.getStatus);
  const { busy, error, run } = useSubmit();
  const engaged = status.data?.ai?.kill_switch?.engaged;
  const flip = () => {
    const reason = engaged ? null : window.prompt("Stop ALL AI calls (reading pages, answers, search, voice) until you release the switch? Reason:", "");
    if (!engaged && reason === null) return;
    run(async () => { await admin.setKillSwitch(!engaged, reason || null); status.reload(); state.reload(); });
  };
  return (
    <>
      <div className={`callout ${engaged ? "warn" : "info"}`} style={{ marginBottom: 16 }}>
        <div className="row">
          <div><strong>AI kill switch is {engaged ? "ON" : "off"}.</strong> {engaged ? "Every AI call is refused." : "Use it if a free quota is being drained."}
            {engaged && status.data.ai.kill_switch.source === "env" && " It is set in the server settings (AI_KILL_SWITCH) and can only be released there."}</div>
          <button className={`btn ${engaged ? "" : "danger"}`} disabled={busy || !status.data || (engaged && status.data.ai.kill_switch.source === "env")} onClick={flip}>{engaged ? "Turn AI back on" : "Stop all AI"}</button>
        </div>
      </div>
      <ErrorNote error={error} />
      <Async state={state}>
        {(u) => (
          <>
            <div className="tiles">
              {Object.entries(QUOTA_LABEL).map(([q, label]) => (
                <div className="tile" key={q}><div className="num">{n(u.totals_today[q])}</div><div className="lbl">{label} today{u.global_caps[q] ? ` (app limit ${n(u.global_caps[q])})` : ""}</div></div>
              ))}
              <div className={`tile ${u.blocked_today ? "risk" : ""}`}><div className="num">{u.blocked_today}</div><div className="lbl">Calls refused by a limit</div></div>
            </div>
            <div className="card tablewrap">
              <h3>Heaviest users today</h3>
              {u.top_users.length === 0 ? <Empty>No AI use yet today.</Empty> : (
                <table className="table"><thead><tr><th>User</th>{Object.keys(QUOTA_LABEL).map((q) => <th key={q}>{QUOTA_LABEL[q]}</th>)}</tr></thead>
                  <tbody>{u.top_users.map((r) => <tr key={r.user_id}><td>{r.name}<div className="small">{r.username} · {r.role}</div></td>{Object.keys(QUOTA_LABEL).map((q) => <td key={q}>{n(r.used[q] || 0)}</td>)}</tr>)}</tbody></table>
              )}
            </div>
            <div className="card tablewrap">
              <h3>Daily totals</h3>
              <table className="table"><thead><tr><th>Day</th>{Object.keys(QUOTA_LABEL).map((q) => <th key={q}>{QUOTA_LABEL[q]}</th>)}</tr></thead>
                <tbody>{[...u.daily].reverse().map((d) => <tr key={d.date}><td>{d.date}</td>{Object.keys(QUOTA_LABEL).map((q) => <td key={q}>{n(d[q] || 0)}</td>)}</tr>)}</tbody></table>
              <p className="small mt mb0">Daily caps per user — students/parents: {Object.entries(u.default_caps.student_parent).map(([q, v]) => `${QUOTA_LABEL[q]} ${cap(v)}`).join(" · ")}. Teachers get more. Change one person's cap on the People tab.</p>
            </div>
          </>
        )}
      </Async>
    </>
  );
}

// ---- teacher invites ----------------------------------------------------------------------------------------

function InvitesTab() {
  const state = useLoad(admin.listInvites);
  const { busy, error, run } = useSubmit();
  const [note, setNote] = useState("");
  const [days, setDays] = useState(7);
  const [fresh, setFresh] = useState(null);
  return (
    <>
      <form className="card stack" onSubmit={(e) => { e.preventDefault(); run(async () => { setFresh(await admin.createInvite(note.trim() || null, Number(days))); setNote(""); state.reload(); }); }}>
        <h3>New teacher invite</h3>
        <p className="small mb0">A teacher who enters this code when signing up is activated at once. Each code works once.</p>
        <div className="grid2">
          <div><label htmlFor="in">Who is it for? (optional)</label><input id="in" className="input" value={note} maxLength={120} onChange={(e) => setNote(e.target.value)} /></div>
          <div><label htmlFor="id">Valid for (days, 0 = never expires)</label><input id="id" className="input" type="number" min="0" max="90" value={days} onChange={(e) => setDays(e.target.value)} /></div>
        </div>
        <ErrorNote error={error} />
        <div><button className="btn" disabled={busy}>Create invite</button></div>
        {fresh && <div className="callout ok" role="status">Code (shown only now — copy it): <span className="code">{fresh.code}</span></div>}
      </form>
      <Async state={state}>
        {(rows) => (
          <div className="card tablewrap">
            {rows.length === 0 ? <Empty>No invites yet.</Empty> : (
              <table className="table"><thead><tr><th>For</th><th>State</th><th>Created</th><th>Expires</th><th /></tr></thead>
                <tbody>{rows.map((i) => (
                  <tr key={i.id}><td>{i.note || "—"}<div className="small">by {i.created_by_username || "cli"}</div></td>
                    <td><Pill kind={i.state === "active" ? "info" : i.state === "used" ? "ok" : "stable"}>{i.state}</Pill>{i.used_by_username && <div className="small">{i.used_by_username}</div>}</td>
                    <td className="small">{fmtDateTime(i.created_at)}</td><td className="small">{i.expires_at ? fmtDateTime(i.expires_at) : "never"}</td>
                    <td>{i.state === "active" && <button className="btn danger small-btn" disabled={busy} onClick={() => run(async () => { await admin.revokeInvite(i.id); state.reload(); })}>Revoke</button>}</td></tr>
                ))}</tbody></table>
            )}
          </div>
        )}
      </Async>
    </>
  );
}

// ---- audit log -----------------------------------------------------------------------------------------------

function AuditTab() {
  const [action, setAction] = useState("");
  const [actor, setActor] = useState("");
  const [target, setTarget] = useState("");
  const [page, setPage] = useState(0);
  const size = 50;
  const state = useLoad(() => admin.auditLog({ action, actor, target, limit: size, offset: page * size }), [action, actor, target, page]);
  const reset = (set) => (e) => { set(e.target.value); setPage(0); };
  return (
    <>
      <div className="card"><div className="grid2">
        <div><label htmlFor="aa">Action</label>
          <select id="aa" className="input" value={action} onChange={reset(setAction)}>
            <option value="">All</option><option value="user.">People (disable, delete, approve…)</option><option value="room.">Rooms (joins, removals, resets)</option>
            <option value="parent.">Parent links</option><option value="book.">Book deletions</option><option value="chapter.">Chapters</option><option value="ai.">AI switch</option><option value="invite.">Invites</option><option value="auth.">Login lockouts</option>
          </select></div>
        <div><label htmlFor="ac">Done by (username)</label><input id="ac" className="input" value={actor} onChange={reset(setActor)} /></div>
        <div><label htmlFor="at">About (name contains)</label><input id="at" className="input" value={target} onChange={reset(setTarget)} /></div>
      </div></div>
      <Async state={state}>
        {(r) => (
          <div className="card tablewrap">
            {r.items.length === 0 ? <Empty>Nothing recorded for this filter.</Empty> : (
              <table className="table"><thead><tr><th>When</th><th>Who</th><th>Action</th><th>About</th><th>Details</th></tr></thead>
                <tbody>{r.items.map((a) => (
                  <tr key={a.id}><td className="small nowrap">{fmtDateTime(a.created_at)}</td><td>{a.actor_username || "—"}<div className="small">{a.actor_role}</div></td>
                    <td><code>{a.action}</code></td><td>{a.target_label || a.target_id || "—"}<div className="small">{a.target_type}</div></td>
                    <td className="small">{a.detail ? JSON.stringify(a.detail) : ""}{a.request_id ? <div>req {a.request_id}</div> : null}</td></tr>
                ))}</tbody></table>
            )}
            <div className="row" style={{ marginTop: 12 }}>
              <span className="small">{r.total} entries</span>
              <span className="chips">
                <button className="btn ghost small-btn" disabled={page === 0} onClick={() => setPage(page - 1)}>Newer</button>
                <button className="btn ghost small-btn" disabled={(page + 1) * size >= r.total} onClick={() => setPage(page + 1)}>Older</button>
              </span>
            </div>
          </div>
        )}
      </Async>
    </>
  );
}
