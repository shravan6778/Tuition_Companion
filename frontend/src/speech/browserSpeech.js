// BROWSER speech-to-text: the student's own browser recognises the speech (Web Speech API). Needs no backend and costs nothing;
// the server never receives any audio. Quality for Telugu depends on the browser, which is why a pilot decides (see docs/SPEECH_PILOT.md).
const Recognition = typeof window !== "undefined" ? window.SpeechRecognition || window.webkitSpeechRecognition : undefined;

export const browserSpeech = {
  name: "browser",
  supported: () => !!Recognition,
  // start({ language, onText(text, isFinal), onError(message), onEnd() }) -> { stop(), abort() }
  start({ language, onText, onError, onEnd }) {
    const r = new Recognition();
    r.lang = language;
    r.continuous = true;
    r.interimResults = true;
    r.onresult = (e) => onText(Array.from(e.results, (res) => res[0].transcript).join(" ").trim(), Array.from(e.results).every((res) => res.isFinal));
    r.onerror = (e) => onError(e.error === "not-allowed" ? "Allow the microphone to say your answer, or type it instead." : "We couldn't hear that. Try again, or type it instead.");
    r.onend = () => onEnd();
    r.start();
    return { stop: () => r.stop(), abort: () => r.abort() };
  },
};
