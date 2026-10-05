"""Small in-memory sliding-window rate limiter, keyed by (bucket, user).

Per-process: fine for one API instance (local, demo, a single container). Behind several instances each one
counts separately, so move this to a shared store (e.g. Redis) before scaling out."""
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:
    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, bucket: str, subject: str, limit: int, per_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[(bucket, subject)]
            while hits and now - hits[0] >= per_seconds:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = max(1, int(per_seconds - (now - hits[0])) + 1)
                raise HTTPException(
                    status_code=429,
                    detail="Too many attempts. Please wait a bit and try again.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = RateLimiter()
