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
    return await asyncio.to_thread(make_report, n)      # waits in a worker thread; the loop stays free
