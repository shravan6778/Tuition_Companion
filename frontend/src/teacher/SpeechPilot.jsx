import { useRef, useState } from "react";
import Header from "../shared/Header";
import pilot from "../speech/pilotItems.json";
import { sourceFor, useSpeechConfig } from "../speech";

const csvCell = (v) => `"${String(v ?? "").replaceAll('"', '""')}"`;

// The speech pilot (docs/SPEECH_PILOT.md): each student reads the same five answers in each language, the transcript is kept here in the
// browser, and one CSV is downloaded for `python -m app.db.stt_pilot`. Nothing is sent to the server and no audio is kept.
export default function SpeechPilot() {
  const config = useSpeechConfig();
  const [participant, setParticipant] = useState("");
  const [language, setLanguage] = useState("te-IN");
  const [source, setSource] = useState("browser");
  const [rows, setRows] = useState([]);
  const [listening, setListening] = useState(null);
  const [heard, setHeard] = useState({});
  const [error, setError] = useState("");
  const session = useRef(null);
  const engine = sourceFor({ source });

  const start = (item) => {
    setError(""); setListening(item.id);
    session.current = engine.start({
      language,
      onText: (text) => setHeard((h) => ({ ...h, [item.id]: text })),
      onError: setError,
      onEnd: () => setListening(null),
    });
  };
  const keep = (item) => {
    setRows((r) => [...r.filter((x) => !(x.participant === participant && x.language === language && x.item === item.id && x.source === source)),
      { participant, language, item: item.id, source, reference: item[language].text, transcript: heard[item.id] || "" }]);
  };
  const download = () => {
    const head = ["participant", "language", "item", "source", "reference", "transcript"];
    const csv = [head.join(","), ...rows.map((r) => head.map((h) => csvCell(r[h])).join(","))].join("\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" }));
    a.download = "speech-pilot.csv"; a.click();
  };

  return (
    <>
      <Header title="Speech pilot" subtitle="Each student reads the five sentences in each language. Download the CSV and run app.db.stt_pilot." />
      <div className="container stack">
        <div className="card stack mb0">
          <div className="grid2">
            <div><label htmlFor="sp-who">Student (a code, not a name)</label><input id="sp-who" className="input" value={participant} onChange={(e) => setParticipant(e.target.value)} /></div>
            <div><label htmlFor="sp-lang">Language</label>
              <select id="sp-lang" className="input" value={language} onChange={(e) => setLanguage(e.target.value)}>{config.languages.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}</select></div>
            <div><label htmlFor="sp-src">Speech source</label>
              <select id="sp-src" className="input" value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="browser">Browser (free)</option>{config.server_available && <option value="server">Server (Azure)</option>}</select></div>
          </div>
          {!engine.supported() && <div className="callout warn">This browser can't listen. Use Chrome or Edge on a device with a microphone.</div>}
          {error && <div className="callout warn" role="alert">{error}</div>}
        </div>
        {pilot.items.map((item, n) => (
          <div className="card stack mb0" key={item.id}>
            <strong>{n + 1}. Read this aloud</strong>
            <p className="q-text" lang={language.slice(0, 2)}>{item[language].text}</p>
            <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
              <button className={`btn small-btn${listening === item.id ? " danger" : " secondary"}`} disabled={!participant.trim() || !engine.supported() || (listening && listening !== item.id)}
                onClick={listening === item.id ? () => session.current?.stop?.() : () => start(item)}>{listening === item.id ? "Stop" : "🎤 Speak"}</button>
              <button className="btn small-btn" disabled={!heard[item.id] || listening === item.id || !participant.trim()} onClick={() => keep(item)}>Keep this result</button>
            </div>
            {heard[item.id] && <p className="pre mb0"><strong>Heard:</strong> {heard[item.id]}</p>}
          </div>
        ))}
        <div className="row">
          <span className="small">{rows.length} results kept in this browser tab.</span>
          <button className="btn" disabled={rows.length === 0} onClick={download}>Download CSV</button>
        </div>
      </div>
    </>
  );
}
