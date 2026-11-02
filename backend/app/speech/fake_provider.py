from typing import Optional

from .base import SpeechError, Transcript


class FakeSpeechToText:
    """For tests and keyless local dev: returns a fixed transcript per language and remembers each call (never the audio itself).

    `fail=True` makes every call raise SpeechError; `silent=True` returns an empty transcript."""

    name = "fake"

    def __init__(self, transcripts: Optional[dict[str, str]] = None, fail: bool = False, silent: bool = False):
        self.transcripts = transcripts or {}
        self.fail, self.silent = fail, silent
        self.calls: list[tuple[int, str, str]] = []  # (audio length, content type, language): the audio is NOT kept

    def transcribe(self, audio: bytes, content_type: str, language: str) -> Transcript:
        self.calls.append((len(audio), content_type, language))
        if self.fail:
            raise SpeechError("We couldn't turn that into text. Please try again, or type your answer.")
        if self.silent:
            return Transcript("", language, None)
        return Transcript(self.transcripts.get(language, f"fake transcript in {language}"), language, 0.9)
