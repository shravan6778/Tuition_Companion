"""The speech-to-text seam.

Everything that turns speech into text sits behind `SpeechToText`. Two sources exist, and the rest of the app does not care which:

  * BROWSER (the default). The student's own browser recognises the speech (Web Speech API). No backend is involved, it costs
    nothing, and the server never receives any audio. The matching interface on the front end is `frontend/src/speech/`.
  * SERVER. The browser sends a short recording and this side transcribes it: `AzureSpeechToText` (Azure Speech, free tier) or
    `FakeSpeechToText` (tests). Use it only for the languages the pilot (`app.db.stt_pilot`) shows the browser handles badly,
    which is expected to be Telugu if anything: SPEECH_PROVIDER=azure and SPEECH_SERVER_LANGUAGES=te-IN.

Either way the result is only TEXT that lands in the answer box; the student reviews or edits it and it is graded as typed text.
AUDIO IS NEVER STORED: server mode keeps it in memory for the length of one request and drops it right after transcription
(`speech/routes.py`); there is no file, no table and no log line for it.
"""
from dataclasses import dataclass
from typing import Optional, Protocol

from app.core.errors import ProcessingError


class SpeechError(ProcessingError):
    """Safe to show to the student: they are asked to try again or to type."""


@dataclass(frozen=True)
class Transcript:
    text: str
    language: str
    confidence: Optional[float] = None


class SpeechToText(Protocol):
    name: str

    def transcribe(self, audio: bytes, content_type: str, language: str) -> Transcript:
        """`audio` is one short recording (WAV, 16 kHz mono) and `language` a BCP-47 tag such as `te-IN`.
        Raises `SpeechError` when nothing could be recognised or the service is down."""
        ...
