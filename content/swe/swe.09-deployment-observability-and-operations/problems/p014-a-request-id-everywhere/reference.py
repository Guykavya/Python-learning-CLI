import contextvars
import logging
import re
import time
import uuid

from fastapi.responses import JSONResponse

request_id_var = contextvars.ContextVar("request_id", default="-")
VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
QUIET_PATHS = {"/healthz", "/readyz", "/metrics"}
log = logging.getLogger("pagebound")


class RequestContext:
    """Pure ASGI middleware: request id in, request id out, one access-log line."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if VALID_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(rid)
        started, status = time.perf_counter(), 500

        async def send_with_id(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", []).append((b"x-request-id", rid.encode()))
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            log.exception("unhandled error")                       # the traceback goes to the log...
            response = JSONResponse({"error": "internal error", "request_id": rid}, status_code=500)
            await response(scope, receive, send_with_id)           # ...the client only gets the id
        finally:
            if scope["path"] not in QUIET_PATHS:
                log.info("request finished", extra={"fields": {
                    "method": scope["method"], "path": scope["path"], "status": status,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1)}})
            request_id_var.reset(token)
