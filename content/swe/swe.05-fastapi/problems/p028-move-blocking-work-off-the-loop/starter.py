import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


def make_report(n: int) -> dict:
    """An old, blocking function: it takes 0.3 s and must not run on the event loop."""
    time.sleep(0.3)
    return {"n": n, "total": sum(range(n))}


@app.get("/report/{n}")
async def report(n: int):
    # TODO: run make_report in a worker thread so the event loop stays free
    return make_report(n)
