// SERVER speech-to-text: record a short clip as 16 kHz mono WAV, send it to POST /student/speech/transcribe, get text back.
// Used only for the languages the backend routes to the server (GET /student/speech/config). The clip lives in memory for
// the length of the request; nothing is saved on either side.
import api from "../shared/api";

const RATE = 16000;

function encodeWav(chunks, inputRate) {
  const length = chunks.reduce((n, c) => n + c.length, 0);
  const flat = new Float32Array(length);
  let off = 0;
  for (const c of chunks) { flat.set(c, off); off += c.length; }
  const ratio = inputRate / RATE;
  const n = Math.floor(flat.length / ratio);
  const buf = new ArrayBuffer(44 + n * 2);
  const v = new DataView(buf);
  const str = (o, s) => [...s].forEach((ch, i) => v.setUint8(o + i, ch.charCodeAt(0)));
  str(0, "RIFF"); v.setUint32(4, 36 + n * 2, true); str(8, "WAVE"); str(12, "fmt "); v.setUint32(16, 16, true);
  v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, RATE, true); v.setUint32(28, RATE * 2, true);
  v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, "data"); v.setUint32(40, n * 2, true);
  for (let i = 0; i < n; i++) {
    const s = Math.max(-1, Math.min(1, flat[Math.floor(i * ratio)]));
    v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return new Blob([buf], { type: "audio/wav" });
}

export const serverSpeech = {
  name: "server",
  supported: () => typeof navigator !== "undefined" && !!navigator.mediaDevices?.getUserMedia && !!(window.AudioContext || window.webkitAudioContext),
  start({ language, onText, onError, onEnd }) {
    let stream, ctx, node, source, stopped = false;
    const chunks = [];
    const cleanup = () => { node?.disconnect(); source?.disconnect(); stream?.getTracks().forEach((t) => t.stop()); ctx?.close(); };
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        source = ctx.createMediaStreamSource(stream);
        node = ctx.createScriptProcessor(4096, 1, 1);
        node.onaudioprocess = (e) => { if (!stopped) chunks.push(new Float32Array(e.inputBuffer.getChannelData(0))); };
        source.connect(node); node.connect(ctx.destination);
      } catch {
        onError("Allow the microphone to say your answer, or type it instead.");
        onEnd();
      }
    })();
    return {
      abort: () => { stopped = true; cleanup(); },
      stop: async () => {
        stopped = true;
        const rate = ctx?.sampleRate || RATE;
        cleanup();
        try {
          const wav = encodeWav(chunks, rate);
          const res = await api.post(`/student/speech/transcribe?language=${encodeURIComponent(language)}`, wav, { headers: { "Content-Type": "audio/wav" } });
          onText(res.data.text, true);
        } catch (e) {
          onError(e.response?.data?.detail || "We couldn't turn that into text. Try again, or type it instead.");
        } finally {
          chunks.length = 0;
          onEnd();
        }
      },
    };
  },
};
