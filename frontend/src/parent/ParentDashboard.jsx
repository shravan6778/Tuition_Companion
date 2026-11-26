import { useState } from "react";
import {
  getChildDailyProgress,
  getChildTrends,
  linkChild,
  listChildren,
} from "../api/learning";
import DailyProgressView from "../shared/DailyProgressView";
import Header from "../shared/Header";
import { ProgressTab, WeakAreasTab } from "../shared/TrendViews";
import {
  Async,
  Empty,
  ErrorNote,
  Tabs,
  useLoad,
  useSubmit,
} from "../shared/ui";

// A parent sees three read-only views of an approved child: day-by-day progress, analytics and weak areas.
const PARENT_TABS = [
  ["progress", "Progress"],
  ["analytics", "Analytics"],
  ["weak", "Weak Areas"],
];

function ChildView({ child }) {
  const [tab, setTab] = useState("progress");
  const trends = (weeks) => getChildTrends(child.id, weeks);
  return (
    <div className="stack">
      <span className="small">
        {child.rooms.length
          ? `In ${child.rooms.map((r) => r.name).join(", ")}`
          : "Not in any room yet"}
      </span>
      <Tabs tabs={PARENT_TABS} value={tab} onChange={setTab} />
      {tab === "progress" && (
        <DailyProgressView
          fetcher={(from, to) => getChildDailyProgress(child.id, from, to)}
        />
      )}
      {tab === "analytics" && (
        <ProgressTab studentId={child.id} fetchTrends={trends} />
      )}
      {tab === "weak" && (
        <WeakAreasTab studentId={child.id} fetchTrends={trends} readOnly />
      )}
    </div>
  );
}

export default function ParentDashboard() {
  const state = useLoad(() => listChildren(true));
  const [code, setCode] = useState("");
  const [pickedId, setPickedId] = useState("");
  const { busy, error, run } = useSubmit();

  const link = (e) => {
    e.preventDefault();
    run(async () => {
      await linkChild(code.trim());
      setCode("");
      state.reload();
    });
  };

  return (
    <>
      <Header
        title="My children"
        subtitle="A read-only view of how they're getting on. You can't change anything here."
      />
      <div className="container">
        <Async state={state}>
          {(children) => {
            const approved = children.filter((c) => c.status !== "pending");
            const pending = children.filter((c) => c.status === "pending");
            const child = approved.find((c) => c.id === pickedId) || approved[0];
            return (
              <>
                {children.length === 0 && (
                  <div className="card">
                    <Empty>
                      <p>
                        <strong>No children linked yet.</strong>
                      </p>
                      <p className="mb0">
                        Ask your child for the link code on their My Books page
                        and enter it below.
                      </p>
                    </Empty>
                  </div>
                )}

                {child && (
                  <section className="card" aria-label={child.name}>
                    {approved.length > 1 ? (
                      <div style={{ marginBottom: 12 }}>
                        <label htmlFor="child-pick" className="small">
                          Child
                        </label>
                        <select
                          id="child-pick"
                          className="input"
                          value={child.id}
                          onChange={(e) => setPickedId(e.target.value)}
                        >
                          {approved.map((c) => (
                            <option key={c.id} value={c.id}>
                              {c.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <h2>{child.name}</h2>
                    )}
                    <ChildView key={child.id} child={child} />
                  </section>
                )}

                {pending.map((c) => (
                  <section className="card" key={c.id} aria-label={c.name}>
                    <h2>{c.name}</h2>
                    <div className="callout info">
                      <strong>Waiting for approval</strong>
                      <p className="mb0 small">
                        Your child needs to approve this parent link from their
                        My Books page before you can view progress.
                      </p>
                    </div>
                  </section>
                ))}

                <form className="card stack" onSubmit={link}>
                  <h3>Link a student</h3>
                  <label htmlFor="lc">
                    Link code (from your child's My Books page)
                  </label>
                  <input
                    id="lc"
                    className="input"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    required
                    minLength={4}
                    maxLength={12}
                  />
                  <ErrorNote error={error} />
                  <div>
                    <button className="btn" disabled={busy}>
                      {busy ? "Linking..." : "Link student"}
                    </button>
                  </div>
                </form>
              </>
            );
          }}
        </Async>
      </div>
    </>
  );
}
