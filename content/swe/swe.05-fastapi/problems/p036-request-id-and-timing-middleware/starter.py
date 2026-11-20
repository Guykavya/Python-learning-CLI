import re
import time
import uuid

from fastapi import FastAPI, Request

VALID_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")

app = FastAPI()


# TODO: one @app.middleware("http") function:
#   choose the request id (reuse a valid incoming X-Request-ID, else uuid.uuid4().hex),
#   store it in request.state.request_id, time call_next with time.perf_counter(),
#   add X-Request-ID and Server-Timing ("app;dur=<ms with one decimal>") to the response.


@app.get("/ping")
def ping(request: Request):
    return {"request_id": getattr(request.state, "request_id", None)}
