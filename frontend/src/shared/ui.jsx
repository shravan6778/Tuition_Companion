/* eslint-disable react-refresh/only-export-components -- this kit deliberately mixes small components with hooks and formatters */
import { useCallback, useEffect, useRef, useState } from "react";

// Load something on mount / when deps change. Late responses from an older request are ignored.
export function useLoad(fn, deps = []) {
  const [state, setState] = useState({ data: null, error: "", loading: true });
  const seq = useRef(0);
  // eslint-disable-next-line react-hooks/exhaustive-deps, react-hooks/use-memo
  const run = useCallback(fn, deps);
  const reload = useCallback(async () => {
    const mine = ++seq.current;
    setState((s) => ({ ...s, loading: true, error: "" }));
    try {
      const data = await run();
      if (mine === seq.current) setState({ data, error: "", loading: false });
    } catch (e) {
      if (mine === seq.current) setState({ data: null, error: e.message, loading: false });
    }
  }, [run]);
  useEffect(() => {
    reload(); // eslint-disable-line react-hooks/set-state-in-effect -- loading state must flip when the inputs change
  }, [reload]);
  return { ...state, reload };
}

export function Loading({ children = "Loading..." }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" aria-hidden="true" /> {children}
    </div>
  );
}

export function ErrorNote({ error, onRetry }) {
  if (!error) return null;
  return (
    <div className="callout warn" role="alert">
      {error}{" "}
      {onRetry && (
        <button type="button" className="btn link" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function Empty({ children }) {
  return <div className="empty">{children}</div>;
}

// Renders the loading / error states, then the children with the data.
export function Async({ state, children }) {
  if (state.loading && state.data == null) return <Loading />;
  if (state.error) return <ErrorNote error={state.error} onRetry={state.reload} />;
  if (state.data == null) return null;
  return children(state.data);
}

export function Tabs({ tabs, value, onChange }) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map(([id, label]) => (
        <button
          key={id}
          type="button"
          role="tab"
          aria-selected={value === id}
          className={`tab${value === id ? " active" : ""}`}
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

const PILLS = {
  weak: ["⚠", "Weak"],
  at_risk: ["◆", "At risk"],
  ok: ["✓", "On track"],
  improving: ["↑", "Improving"],
  declining: ["↓", "Declining"],
  stable: ["→", "Stable"],
  insufficient_data: ["·", "Not enough data"],
  ready: ["✓", "Ready"],
  pending: ["…", "Writing"],
  failed: ["!", "Failed"],
  open: ["○", "To do"],
  submitted: ["✓", "Done"],
};
export function Pill({ kind, children }) {
  const [icon, label] = PILLS[kind] || ["", kind];
  const cls = kind === "submitted" ? "done" : kind === "open" ? "info" : kind;
  return (
    <span className={`pill ${cls}`}>
      {icon && <span aria-hidden="true">{icon}</span>}
      {children || label}
    </span>
  );
}

// value 0..1
export function ScoreBar({ value, label }) {
  if (value == null) return <span className="small">no score yet</span>;
  const p = Math.round(value * 100);
  const tone = value < 0.6 ? "weak" : value < 0.8 ? "mid" : "";
  return (
    <div className="row gap-s" style={{ justifyContent: "flex-start", flexWrap: "nowrap" }}>
      <div className={`bar ${tone}`} role="img" aria-label={`${label || "Score"} ${p} percent`} style={{ flex: 1 }}>
        <span style={{ width: `${p}%` }} />
      </div>
      <span className="small nowrap" style={{ minWidth: 36, textAlign: "right" }}>{p}%</span>
    </div>
  );
}

// points: numbers 0..1 (null = gap). Draws a small line; colour is never the only signal (the numbers are shown beside it).
export function Sparkline({ points, width = 120, height = 32 }) {
  const pts = points.map((v, i) => ({ v, i })).filter((p) => p.v != null);
  if (pts.length === 0) return <span className="small">no data</span>;
  const n = Math.max(points.length - 1, 1);
  const x = (i) => 4 + (i / n) * (width - 8);
  const y = (v) => height - 4 - v * (height - 8);
  const d = pts.map((p, k) => `${k ? "L" : "M"}${x(p.i).toFixed(1)},${y(p.v).toFixed(1)}`).join(" ");
  return (
    <svg className="spark" width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img"
      aria-label={`Trend: ${pts.map((p) => Math.round(p.v * 100) + "%").join(", ")}`}>
      <line x1="4" x2={width - 4} y1={y(0.6)} y2={y(0.6)} stroke="#d6d3d1" strokeDasharray="3 3" />
      <path d={d} fill="none" stroke="#0f766e" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      {pts.map((p) => <circle key={p.i} cx={x(p.i)} cy={y(p.v)} r="2.5" fill="#0f766e" />)}
    </svg>
  );
}

export const pct = (v) => (v == null ? "-" : `${Math.round(v * 100)}%`);
export const fmtDate = (d) => (d ? new Date(d).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "");
export const fmtDateTime = (d) =>
  d ? new Date(d).toLocaleString(undefined, { day: "numeric", month: "short", hour: "numeric", minute: "2-digit" }) : "";
export const signedPct = (v) => (v == null ? "-" : `${v > 0 ? "+" : ""}${Math.round(v * 100)} pts`);
export const bookLabel = (b) => `${b.class_name} ${b.subject}${b.publisher ? ` (${b.publisher})` : ""}`;
export const isOverdue = (due) => !!due && new Date(due + "T23:59:59") < new Date();

export function useSubmit() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function run(fn) {
    setBusy(true);
    setError("");
    try {
      return await fn();
    } catch (e) {
      setError(e.message);
      return undefined;
    } finally {
      setBusy(false);
    }
  }
  return { busy, error, setError, run };
}
