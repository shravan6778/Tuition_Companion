"""Request counters for the admin status page: requests and server errors per minute, kept for one hour.

In memory and per process (like core/ratelimit.py): with several API processes each one reports its own traffic.
Use the external uptime monitor and the log files for the whole picture."""
import threading
import time
from collections import deque

_KEEP_MINUTES = 60


class RequestMetrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._buckets: deque[list] = deque()  # [minute, requests, errors_5xx, errors_4xx, duration_ms_total]

    def record(self, status_code: int, duration_ms: float, now: float | None = None) -> None:
        minute = int((time.time() if now is None else now) // 60)
        with self._lock:
            if not self._buckets or self._buckets[-1][0] != minute:
                self._buckets.append([minute, 0, 0, 0, 0.0])
            while self._buckets and self._buckets[0][0] <= minute - _KEEP_MINUTES:
                self._buckets.popleft()
            b = self._buckets[-1]
            b[1] += 1
            b[2] += 1 if status_code >= 500 else 0
            b[3] += 1 if 400 <= status_code < 500 else 0
            b[4] += duration_ms

    def snapshot(self, window_min: int = 15, now: float | None = None) -> dict:
        minute = int((time.time() if now is None else now) // 60)
        requests = server_errors = client_errors = 0
        duration = 0.0
        with self._lock:
            for m, n, e5, e4, d in self._buckets:
                if m > minute - window_min:
                    requests += n
                    server_errors += e5
                    client_errors += e4
                    duration += d
        return {
            "window_minutes": window_min,
            "requests": requests,
            "server_errors": server_errors,
            "client_errors": client_errors,
            "error_rate": round(server_errors / requests, 4) if requests else 0.0,
            "avg_ms": round(duration / requests, 1) if requests else 0.0,
        }

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()


metrics = RequestMetrics()
