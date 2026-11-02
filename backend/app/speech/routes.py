"""Speech for answers.

    GET  /student/speech/config       the mic's languages, and for each one where the speech becomes text (browser or server),
                                      which languages are "confirm before grading", and whether long/spoken answers apply
    POST /student/speech/transcribe   SERVER mode only: one short recording in (raw WAV body, ?language=te-IN), text out

The server never stores audio. The recording is read into memory for this one request (a raw body, so it never becomes a
multipart temp file on disk), handed to the speech provider, and dropped; nothing is written to the database, the storage
folder or the log. The text it returns is NOT saved either: it only lands in the student's answer box, and is stored when the
student submits that answer (with the language and input_method='voice'). In browser mode this route is never called."""
import io
import wave

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.auth.dependencies import require_student
from app.core.config import settings
from app.core.ratelimit import limiter
from app.speech import LANGUAGE_LABELS, SpeechError, csv_list, get_speech_provider, server_enabled, source_for, speech_languages

router = APIRouter(prefix="/student/speech", tags=["speech"], dependencies=[Depends(require_student)])


class LanguageOut(BaseModel):
    code: str
    label: str
    source: str  # browser | server
    hold: bool  # a spoken answer in this language is not graded until the teacher confirms the transcript


class SpeechConfigOut(BaseModel):
    languages: list[LanguageOut]
    default_language: str
    server_available: bool


class TranscriptOut(BaseModel):
    text: str
    language: str
    confidence: float | None = None


@router.get("/config", response_model=SpeechConfigOut)
def speech_config():
    hold = csv_list(settings.speech_hold_languages)
    langs = [LanguageOut(code=c, label=LANGUAGE_LABELS.get(c, c), source=source_for(c), hold=c in hold) for c in speech_languages()]
    default = settings.speech_default_language if settings.speech_default_language in speech_languages() else (langs[0].code if langs else "en-IN")
    return SpeechConfigOut(languages=langs, default_language=default, server_available=server_enabled())


async def _read_capped(request: Request, limit: int) -> bytes:
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        raise HTTPException(413, "That recording is too long. Please say a shorter answer.")
    buf = bytearray()
    async for chunk in request.stream():
        buf += chunk
        if len(buf) > limit:
            raise HTTPException(413, "That recording is too long. Please say a shorter answer.")
    return bytes(buf)


def check_wav(data: bytes) -> None:
    """The recorder sends WAV (PCM, 16 kHz, mono, 16-bit). Anything else, or a recording that is too long, is refused."""
    try:
        with wave.open(io.BytesIO(data)) as w:
            ok = w.getnchannels() == 1 and w.getframerate() == 16000 and w.getsampwidth() == 2
            seconds = w.getnframes() / float(w.getframerate() or 1)
    except (wave.Error, EOFError):
        raise HTTPException(415, "Send a WAV recording (16 kHz, mono)") from None
    if not ok:
        raise HTTPException(415, "Send a WAV recording (16 kHz, mono)")
    if seconds > settings.speech_max_audio_seconds:
        raise HTTPException(413, "That recording is too long. Please say a shorter answer.")
    if seconds < 0.3:
        raise HTTPException(422, "We didn't hear anything. Please try again.")


@router.post("/transcribe", response_model=TranscriptOut)
async def transcribe(request: Request, language: str, student=Depends(require_student)):
    if not server_enabled():
        raise HTTPException(404, "Speech runs in your browser here, so there is nothing to send")
    if language not in speech_languages():
        raise HTTPException(422, "Choose English, Hindi or Telugu")
    ctype = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
    if ctype not in ("audio/wav", "audio/x-wav", "audio/wave"):
        raise HTTPException(415, "Send a WAV recording (16 kHz, mono)")
    limiter.check("speech", str(student.id), settings.rate_speech_per_hour, 3600)
    audio = await _read_capped(request, settings.speech_max_audio_mb * 1024 * 1024)
    try:
        check_wav(audio)
        try:
            provider = get_speech_provider()
        except RuntimeError:
            raise HTTPException(503, "Speech isn't set up on this server. Please type your answer.") from None
        if provider is None:
            raise HTTPException(404, "Speech runs in your browser here, so there is nothing to send")
        try:
            result = await run_in_threadpool(provider.transcribe, audio, "audio/wav", language)
        except SpeechError as exc:
            raise HTTPException(422, str(exc)) from exc
    finally:
        audio = b""  # the recording is dropped here, success or failure: it was never written anywhere
    if not result.text.strip():
        raise HTTPException(422, "We didn't catch that. Please try again, or type your answer.")
    return TranscriptOut(text=result.text.strip(), language=result.language, confidence=result.confidence)
