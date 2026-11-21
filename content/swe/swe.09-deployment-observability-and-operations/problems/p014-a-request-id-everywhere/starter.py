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
        # TODO: the five steps of problem.md. This version only passes the request on.
        await self.app(scope, receive, send)
