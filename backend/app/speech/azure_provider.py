"""Azure Speech to Text, short-audio REST API (https://learn.microsoft.com/azure/ai-services/speech-service/rest-speech-to-text-short).

Free tier (F0) is enough for a pilot. One call recognises up to about 60 seconds of WAV (PCM, 16 kHz, mono), which is what the
browser recorder in `frontend/src/speech/serverSpeech.js` sends. Languages used here: en-IN, hi-IN, te-IN.
The audio is forwarded and not kept; this class has no state and writes nothing."""
from .base import SpeechError, Transcript

from app.core.config import settings


class AzureSpeechToText:
    name = "azure"

    def __init__(self, key: str, region: str, timeout_s: int = 30):
        if not key or not region:
            raise RuntimeError("Azure speech is not configured. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION.")
        self.key, self.region, self.timeout_s = key, region, timeout_s

    def transcribe(self, audio: bytes, content_type: str, language: str) -> Transcript:
        import httpx  # already a dependency; imported here so the module loads without network libraries in tests

        url = f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
        try:
            r = httpx.post(url, params={"language": language, "format": "detailed", "profanity": "raw"}, content=audio, timeout=self.timeout_s,
                           headers={"Ocp-Apim-Subscription-Key": self.key, "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000",
                                    "Accept": "application/json"})
        except httpx.HTTPError as exc:
            raise SpeechError("The speech service is not available right now. Please type your answer.") from exc
        if r.status_code != 200:
            raise SpeechError("The speech service is not available right now. Please type your answer.")
        body = r.json()
        if body.get("RecognitionStatus") != "Success":
            raise SpeechError("We couldn't hear that clearly. Please try again, or type your answer.")
        best = (body.get("NBest") or [{}])[0]
        text = (best.get("Display") or body.get("DisplayText") or "").strip()
        confidence = best.get("Confidence")
        return Transcript(text, language, float(confidence) if isinstance(confidence, (int, float)) else None)


def build() -> AzureSpeechToText:
    return AzureSpeechToText(settings.azure_speech_key, settings.azure_speech_region)
