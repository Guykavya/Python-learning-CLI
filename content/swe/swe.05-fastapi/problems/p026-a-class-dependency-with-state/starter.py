import math
import time
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


def get_clock() -> float:
    return time.monotonic()


class RateLimit:
    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        # TODO: somewhere to remember the times of recent requests, per key

    def __call__(self, x_api_key: Annotated[str, Header()], now: Annotated[float, Depends(get_clock)]) -> str:
        # TODO: forget old times, 429 with Retry-After when full, else record now
        return x_api_key


def create_app() -> FastAPI:
    app = FastAPI()

    # TODO: protect each endpoint with its own RateLimit instance
    @app.get("/search")
    def search(key: Annotated[str, Header(alias="X-API-Key")]):
        return {"key": key, "results": []}

    @app.get("/export")
    def export(key: Annotated[str, Header(alias="X-API-Key")]):
        return {"key": key, "file": "export.csv"}

    return app
