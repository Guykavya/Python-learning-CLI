import re
import time
import uuid

from fastapi import FastAPI, Request

VALID_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")

app = FastAPI()


@app.middleware("http")
async def request_id_and_timing(request: Request, call_next):
    incoming = request.headers.get("x-request-id", "")
    request_id = incoming if VALID_ID.fullmatch(incoming) else uuid.uuid4().hex
    request.state.request_id = request_id          # before call_next: endpoints can read it
    start = time.perf_counter()
    response = await call_next(request)            # the router, the endpoint (or the 404) run here
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.1f}"
    return response


@app.get("/ping")
def ping(request: Request):
    return {"request_id": getattr(request.state, "request_id", None)}
