"""Who is making the current request, for logs, the audit log and the AI usage meter.

The middleware (core/middleware.py) puts ONE mutable RequestContext into a ContextVar per request. FastAPI runs
synchronous dependencies and routes in worker threads that get a COPY of the context, so a route cannot re-assign the
variable for its caller; but the copy points at the same object, so `get_current_user` can fill in the user on it and
everything later in the request (and the background tasks it queues) sees it.
Outside a request (scripts, tests) the context is a throw-away one with no user."""
import contextvars
import re
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional

_SAFE_ID = re.compile(r"^[A-Za-z0-9._\-]{8,64}$")


@dataclass
class RequestContext:
    request_id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


_ctx: contextvars.ContextVar[Optional[RequestContext]] = contextvars.ContextVar("request_ctx", default=None)


def new_request_id() -> str:
    return uuid.uuid4().hex[:16]


def accept_request_id(value: Optional[str]) -> str:
    """Re-use a caller's X-Request-ID only when it is short and harmless (it ends up in log lines)."""
    if value and _SAFE_ID.match(value):
        return value
    return new_request_id()


def current() -> RequestContext:
    ctx = _ctx.get()
    return ctx if ctx is not None else RequestContext(request_id="-")


def set_user(user_id, username: Optional[str] = None, role=None) -> None:
    """Called once the session is verified. A no-op outside a request."""
    ctx = _ctx.get()
    if ctx is not None:
        ctx.user_id = str(user_id)
        ctx.username = username
        ctx.role = getattr(role, "value", role)


def start_request(request_id: str) -> contextvars.Token:
    return _ctx.set(RequestContext(request_id=request_id))


def end_request(token: contextvars.Token) -> None:
    _ctx.reset(token)


@contextmanager
def acting_as(user_id, request_id: Optional[str] = None) -> Iterator[RequestContext]:
    """Run a block (a background job, a script) on behalf of a user so its AI calls are metered against them."""
    inherited = _ctx.get()
    ctx = RequestContext(
        request_id=request_id or (inherited.request_id if inherited else new_request_id()),
        user_id=str(user_id) if user_id else None,
    )
    token = _ctx.set(ctx)
    try:
        yield ctx
    finally:
        _ctx.reset(token)
