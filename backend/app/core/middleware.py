"""One ASGI middleware: request id in, request id out, one access-log line, and the counters for the status page.

Written as plain ASGI (not BaseHTTPMiddleware) so the request context stays visible to everything downstream,
including background tasks that run after the response is sent."""
import logging
import re
import time

from app.core import requestctx
from app.core.metrics import metrics

logger = logging.getLogger("app.access")
_UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_h = b"x-request-id"


class RequestContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = next((v.decode("latin-1") for k, v in scope.get("headers", []) if k == _h), None)
        request_id = requestctx.accept_request_id(incoming)
        token = requestctx.start_request(request_id)
        status = {"code": 500}
        started = time.perf_counter()

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                status["code"] = message["status"]
                message["headers"] = [*message.get("headers", []), (_h, request_id.encode("latin-1"))]
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            status["code"] = 500
            logger.exception("Unhandled error in %s %s", scope.get("method"), scope.get("path"))
            raise
        finally:
            ms = (time.perf_counter() - started) * 1000
            route = scope.get("route")
            path = getattr(route, "path", None) or _UUID.sub("{id}", scope.get("path", ""))
            if path not in ("/health", "/health/ready"):  # the uptime pinger would drown everything else
                metrics.record(status["code"], ms)
                logger.info("%s %s -> %s %.0fms", scope.get("method"), path, status["code"], ms)
            requestctx.end_request(token)
