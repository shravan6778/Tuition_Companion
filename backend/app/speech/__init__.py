from typing import Optional

from app.assessment.subject_policy import csv_list, speech_languages
from app.core.config import settings

from .base import SpeechError, SpeechToText, Transcript
from .fake_provider import FakeSpeechToText

LANGUAGE_LABELS = {"en-IN": "English", "hi-IN": "हिन्दी (Hindi)", "te-IN": "తెలుగు (Telugu)"}


def get_speech_provider() -> Optional[SpeechToText]:
    """The SERVER speech-to-text, or None when speech is browser-only (the default: no backend, nothing to pay for)."""
    kind = settings.speech_provider.lower()
    if kind == "azure":
        from .azure_provider import build

        return build()
    if kind == "fake":
        return FakeSpeechToText()
    return None


def server_enabled() -> bool:
    return settings.speech_provider.lower() in ("azure", "fake")


def source_for(language: str) -> str:
    """'server' or 'browser': where this language's speech becomes text."""
    if not server_enabled():
        return "browser"
    return "server" if language in csv_list(settings.speech_server_languages) else "browser"


__all__ = ["FakeSpeechToText", "LANGUAGE_LABELS", "SpeechError", "SpeechToText", "Transcript", "get_speech_provider", "server_enabled",
           "source_for", "speech_languages", "csv_list"]
