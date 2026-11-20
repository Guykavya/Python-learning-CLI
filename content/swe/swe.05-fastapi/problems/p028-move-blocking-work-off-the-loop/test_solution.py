import asyncio
import inspect
import threading
import time

import httpx
from fastapi.testclient import TestClient

import solution
from solution import app


async def at_once(paths):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        responses = await asyncio.gather(*[client.get(p) for p in paths])
        return time.perf_counter() - start, responses


def report_endpoint():
    for route in app.routes:
        if getattr(route, "path", None) == "/report/{n}":
            return route.endpoint
    raise AssertionError("There is no route GET /report/{n}.")


def test_endpoint_is_still_async():
    assert inspect.iscoroutinefunction(report_endpoint()), (
        "Keep the endpoint 'async def'. Turning it into a plain def would also be fast, but the task is to call a "
        "blocking function from async code.")


def test_result_is_unchanged():
    with TestClient(app) as client:
        assert client.get("/report/4").json() == {"n": 4, "total": 6}, "make_report(4) gives total 0+1+2+3 = 6."
        assert client.get("/report/0").json() == {"n": 0, "total": 0}


def test_make_report_runs_in_a_worker_thread(monkeypatch):
    threads = []
    real = solution.make_report

    def recording(n):
        threads.append(threading.current_thread().name)
        return real(n)

    monkeypatch.setattr(solution, "make_report", recording)
    elapsed, responses = asyncio.run(at_once(["/report/3"]))
    assert responses[0].json() == {"n": 3, "total": 3}, f"Got {responses[0].text}"
    assert threads, "make_report was not called. Call it by its name in solution.py."
    assert threads[0] != "MainThread", (
        "make_report ran on the main thread, i.e. on the event loop. "
        "Use await asyncio.to_thread(make_report, n) so it runs in a worker thread.")


def test_three_requests_overlap():
    elapsed, responses = asyncio.run(at_once(["/report/10", "/report/20", "/report/30"]))
    assert [r.json()["total"] for r in responses] == [45, 190, 435], f"Got {[r.text for r in responses]}"
    assert elapsed < 0.6, (
        f"Three concurrent reports took {elapsed:.2f} s; they should overlap (about 0.3 s). "
        "About 0.9 s means make_report still blocks the event loop.")
