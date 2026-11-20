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
        self.hits = {}                      # api key -> list of request times, oldest first

    def __call__(self, x_api_key: Annotated[str, Header()], now: Annotated[float, Depends(get_clock)]) -> str:
        recent = [t for t in self.hits.get(x_api_key, []) if now - t < self.window]
        if len(recent) >= self.limit:
            retry = max(1, math.ceil(recent[0] + self.window - now))
            self.hits[x_api_key] = recent
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry)})
        recent.append(now)
        self.hits[x_api_key] = recent
        return x_api_key


def create_app() -> FastAPI:
    app = FastAPI()
    search_limit = RateLimit(3, 60)         # one object per endpoint: it keeps its own counts
    export_limit = RateLimit(1, 10)

    @app.get("/search")
    def search(key: Annotated[str, Depends(search_limit)]):
        return {"key": key, "results": []}

    @app.get("/export")
    def export(key: Annotated[str, Depends(export_limit)]):
        return {"key": key, "file": "export.csv"}

    return app
