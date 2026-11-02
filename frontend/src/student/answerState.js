// State of one written answer: { text, method: "typed" | "voice", language, confirmed }.
export const emptyAnswer = { text: "", method: "typed", language: null, confirmed: false };
export const answerReady = (a) => !!a?.text?.trim() && (a.method !== "voice" || a.confirmed);
export const answerPayload = (id, a) => ({
  question_id: id, answer_text: (a?.text || "").trim() || null, input_method: a?.method === "voice" && a.text.trim() ? "voice" : "typed",
  language: a?.method === "voice" && a.text.trim() ? a.language : null, transcript_confirmed: !!a?.confirmed,
});
