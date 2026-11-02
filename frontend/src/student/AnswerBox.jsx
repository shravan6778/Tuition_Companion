import { useEffect, useRef, useState } from "react";
import { sourceFor, useSpeechConfig } from "../speech";
import { emptyAnswer } from "./answerState";

// One written answer. Typing is the baseline: the mic only fills THIS box, and the student has to read the text and tick that it says
// what they meant before it can be submitted. Nothing is ever graded straight from speech (the server refuses it too).
// value = { text, method: "typed" | "voice", language, confirmed }
export default function AnswerBox({ id, value = emptyAnswer, onChange, long = false, voiceAllowed = false, disabled = false }) {
  const config = useSpeechConfig();
  const [language, setLanguage] = useState(config.default_language);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
  const session = useRef(null);
  const base = useRef("");
  const lang = config.languages.find((l) => l.code === language) || config.languages[0];
  const source = sourceFor(lang);
  const max = long ? 4000 : 1500;

  useEffect(() => () => session.current?.abort?.(), []);

  const listen = () => {
    setError("");
    base.current = value.text.trim();
    setListening(true);
    session.current = source.start({
      language: lang.code,
      onText: (heard) => onChange({ text: base.current ? `${base.current} ${heard}` : heard, method: "voice", language: lang.code, confirmed: false }),
      onError: (m) => setError(m),
      onEnd: () => setListening(false),
    });
  };
  const edit = (text) => onChange(value.method === "voice" && text.trim() ? { ...value, text, confirmed: false } : { text, method: "typed", language: null, confirmed: false });

  return (
    <div className="stack">
      <label htmlFor={`ans-${id}`} className="small">{long ? "Your answer (a few sentences)" : "Your answer"}</label>
      <textarea id={`ans-${id}`} className="input" rows={long ? 7 : 3} maxLength={max} value={value.text} disabled={disabled || listening}
        onChange={(e) => edit(e.target.value)} />
      {voiceAllowed && !disabled && (
        <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
          <label htmlFor={`lang-${id}`} className="small">Speak in</label>
          <select id={`lang-${id}`} className="input" style={{ width: "auto" }} value={language} disabled={listening} onChange={(e) => setLanguage(e.target.value)}>
            {config.languages.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
          </select>
          {source.supported() ? (
            <button type="button" className={`btn${listening ? " danger" : " secondary"} small-btn`} aria-pressed={listening}
              onClick={listening ? () => session.current?.stop?.() : listen}>{listening ? "Stop" : "🎤 Speak"}</button>
          ) : <span className="small">This browser can't listen. Type your answer, or use the microphone key on your keyboard.</span>}
          {listening && <span className="small" role="status">Listening...</span>}
        </div>
      )}
      {error && <div className="callout warn" role="alert">{error}</div>}
      {value.method === "voice" && value.text.trim() && !listening && (
        <div className="callout info">
          <strong>Check what we heard.</strong> Speech can get words wrong, so fix anything that isn't what you said.
          {lang.hold && value.language === lang.code && <> Your teacher will also check this before it is marked.</>}
          <div className="mt">
            <label><input type="checkbox" checked={value.confirmed} onChange={(e) => onChange({ ...value, confirmed: e.target.checked })} /> I read this and it says what I meant.</label>
          </div>
        </div>
      )}
    </div>
  );
}
