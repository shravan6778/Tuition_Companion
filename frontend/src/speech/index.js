// The speech-to-text seam on the front end. Callers ask for the source of a language and get an object with the same shape either way:
//   { name, supported(), start({ language, onText(text, isFinal), onError(msg), onEnd() }) -> { stop(), abort() } }
// The backend decides which source each language uses (GET /student/speech/config): browser by default, server for the languages the pilot
// found the browser poor at (expected: Telugu, if any).
import { useEffect, useState } from "react";
import api from "../shared/api";
import { browserSpeech } from "./browserSpeech";
import { serverSpeech } from "./serverSpeech";

export const sourceFor = (lang) => (lang?.source === "server" ? serverSpeech : browserSpeech);

const FALLBACK = { default_language: "en-IN", server_available: false, languages: [
  { code: "en-IN", label: "English", source: "browser", hold: false },
  { code: "hi-IN", label: "हिन्दी (Hindi)", source: "browser", hold: false },
  { code: "te-IN", label: "తెలుగు (Telugu)", source: "browser", hold: false },
] };

let cached = null;
export function useSpeechConfig() {
  const [config, setConfig] = useState(cached || FALLBACK);
  useEffect(() => {
    if (cached) return;
    api.get("/student/speech/config").then((r) => { cached = r.data; setConfig(r.data); }).catch(() => {});
  }, []);
  return config;
}
