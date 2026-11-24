class ProcessingError(Exception):
    """An error whose message is safe to show to the teacher."""


class QuotaExceededError(ProcessingError):
    """An AI call was refused before it was paid for: the AI kill switch is on, or a daily cap is used up.
    The message is written for the person who sees it. `kind` is "kill_switch", "user_cap" or "global_cap"."""

    def __init__(self, message: str, kind: str = "user_cap", retry_after: int | None = None):
        super().__init__(message)
        self.kind = kind
        self.retry_after = retry_after
