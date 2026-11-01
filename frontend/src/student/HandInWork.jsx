import { useEffect, useRef, useState } from "react";
import { handInWork } from "../api/learning";
import { ErrorNote, Tabs, useSubmit } from "../shared/ui";

const Recognition = typeof window !== "undefined" ? window.SpeechRecognition || window.webkitSpeechRecognition : undefined;

// How a student shows homework: a photo of it, or their answer spoken aloud. Speech is turned into text on their own device
// (the browser's speech recognition); only that text is sent, so no audio is stored, and the student can correct it first.
export default function HandInWork({ assignmentId, onSent }) {
  const [mode, setMode] = useState("photo");
  const [photo, setPhoto] = useState(null);
  const [note, setNote] = useState("");
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState("");
  const recognition = useRef(null);
  const { busy, error, run } = useSubmit();

  useEffect(() => () => recognition.current?.abort(), []);

  const listen = () => {
    setVoiceError("");
    const r = new Recognition();
    const before = text.trim();
    r.lang = navigator.language || "en-IN";
    r.continuous = true;
    r.interimResults = true;
    r.onresult = (e) => {
      const heard = Array.from(e.results, (res) => res[0].transcript).join(" ").trim();
      setText(before ? `${before} ${heard}` : heard);
    };
    r.onerror = (e) => {
      setVoiceError(e.error === "not-allowed" ? "Allow the microphone to say your answer, or type it instead." : "We couldn't hear that. Try again, or type it instead.");
      setListening(false);
    };
    r.onend = () => setListening(false);
    recognition.current = r;
    setListening(true);
    r.start();
  };

  const send = (e) => {
    e.preventDefault();
    run(async () => {
      if (mode === "photo") await handInWork(assignmentId, { source: "photo", photo, text: note.trim() });
      else await handInWork(assignmentId, { source: "voice", text: text.trim() });
      setPhoto(null); setNote(""); setText("");
      onSent?.();
    });
  };

  const ready = mode === "photo" ? !!photo : text.trim().split(/\s+/).filter(Boolean).length >= 3;

  return (
    <form className="stack" onSubmit={send}>
      <Tabs tabs={[["photo", "Send a photo"], ["voice", "Say your answer"]]} value={mode} onChange={setMode} />
      {mode === "photo" ? (
        <>
          <div>
            <label htmlFor={`hw-photo-${assignmentId}`}>Photo of your work</label>
            <input id={`hw-photo-${assignmentId}`} className="input" type="file" accept="image/png,image/jpeg" capture="environment"
              onChange={(e) => setPhoto(e.target.files?.[0] || null)} />
          </div>
          <div>
            <label htmlFor={`hw-note-${assignmentId}`}>A note for your teacher (optional)</label>
            <input id={`hw-note-${assignmentId}`} className="input" value={note} maxLength={500} onChange={(e) => setNote(e.target.value)} />
          </div>
        </>
      ) : (
        <>
          {Recognition ? (
            <div className="row gap-s" style={{ justifyContent: "flex-start" }}>
              <button type="button" className={`btn${listening ? " danger" : " secondary"}`} aria-pressed={listening}
                onClick={listening ? () => recognition.current?.stop() : listen}>
                {listening ? "Stop listening" : "Start speaking"}
              </button>
              {listening && <span className="small" role="status">Listening...</span>}
            </div>
          ) : (
            <p className="small mb0">This browser can't listen for you. Use the microphone key on your keyboard to dictate, or type your answer.</p>
          )}
          <div>
            <label htmlFor={`hw-text-${assignmentId}`}>What we heard (fix anything that's wrong)</label>
            <textarea id={`hw-text-${assignmentId}`} className="input" value={text} maxLength={4000} onChange={(e) => setText(e.target.value)} />
          </div>
          {voiceError && <div className="callout warn" role="alert">{voiceError}</div>}
        </>
      )}
      <ErrorNote error={error} />
      <div className="row" style={{ justifyContent: "flex-start" }}>
        <button className="btn" disabled={busy || !ready || listening}>{busy ? "Sending..." : "Hand in"}</button>
      </div>
    </form>
  );
}
