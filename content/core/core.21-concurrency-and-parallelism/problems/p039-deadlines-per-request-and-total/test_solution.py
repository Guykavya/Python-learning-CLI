import asyncio
import time

import httpx

from solution import fetch_with_deadlines

BASE = "https://svc.test"


class FakeServer:
    """Each path's delay comes from the dict; records running and cancelled requests."""

    def __init__(self, delays):
        self.delays = delays
        self.running = 0
        self.peak = 0
        self.cancelled = []

    async def handler(self, request):
        path = request.url.path
        self.running += 1
        self.peak = max(self.peak, self.running)
        try:
            await asyncio.sleep(self.delays[path])
        except asyncio.CancelledError:
            self.cancelled.append(path)
            raise
        finally:
            self.running -= 1
        return httpx.Response(200, text=f"{path[1:]} body")


def run(delays, urls, per_request, total):
    server = FakeServer(delays)

    async def main():
        async with httpx.AsyncClient(transport=httpx.MockTransport(server.handler)) as client:
            start = time.perf_counter()
            result = await fetch_with_deadlines(client, urls, per_request, total)
            elapsed = time.perf_counter() - start
            still_running = server.running
            return result, elapsed, still_running

    result, elapsed, still_running = asyncio.run(main())
    return result, elapsed, still_running, server


def test_fast_requests_return_their_text():
    urls = [BASE + "/a", BASE + "/b"]
    result, _, _, _ = run({"/a": 0.01, "/b": 0.02}, urls, per_request=1.0, total=2.0)
    assert result == {BASE + "/a": "a body", BASE + "/b": "b body"}, (
        f"Got {result}. Map each url to response.text when it arrives in time."
    )


def test_slow_request_hits_per_request_deadline():
    urls = [BASE + "/fast", BASE + "/slow"]
    result, elapsed, _, _ = run({"/fast": 0.02, "/slow": 5.0}, urls, per_request=0.2, total=3.0)
    assert result == {BASE + "/fast": "fast body", BASE + "/slow": "timeout"}, (
        f"Got {result}. Wrap each single request in 'async with asyncio.timeout(per_request)' "
        "and store 'timeout' when TimeoutError is raised."
    )
    assert elapsed < 1.0, (
        f"Took {elapsed:.2f}s; the slow request should be cut off after 0.2s, not awaited for 5s."
    )


def test_total_deadline_stops_everything():
    urls = [BASE + "/x", BASE + "/y", BASE + "/z"]
    delays = {"/x": 0.4, "/y": 0.4, "/z": 0.4}
    result, elapsed, _, _ = run(delays, urls, per_request=2.0, total=0.15)
    assert result == {u: "timeout" for u in urls}, (
        f"Got {result}. Nothing can finish within total=0.15s, so every url is 'timeout'."
    )
    assert elapsed < 0.35, (
        f"Took {elapsed:.2f}s, but total was 0.15s. The whole batch needs its own "
        "asyncio.timeout(total) around ALL the requests, not only per request."
    )


def test_total_deadline_keeps_what_finished():
    urls = [BASE + "/quick", BASE + "/medium"]
    result, _, _, _ = run({"/quick": 0.02, "/medium": 0.5}, urls, per_request=2.0, total=0.2)
    assert result == {BASE + "/quick": "quick body", BASE + "/medium": "timeout"}, (
        f"Got {result}. Results that finished before the total deadline must be kept; store "
        "them as they arrive instead of only at the end."
    )


def test_keys_keep_input_order():
    urls = [BASE + "/slow", BASE + "/fast", BASE + "/mid"]
    result, _, _, _ = run({"/slow": 5.0, "/fast": 0.01, "/mid": 0.05}, urls,
                          per_request=0.2, total=1.0)
    assert list(result) == urls, (
        f"Keys came out as {list(result)}. Use the input order (e.g. fill the dict from urls first)."
    )


def test_requests_run_concurrently():
    urls = [f"{BASE}/p{i}" for i in range(6)]
    delays = {f"/p{i}": 0.1 for i in range(6)}
    _, elapsed, _, server = run(delays, urls, per_request=1.0, total=2.0)
    assert server.peak == 6, (
        f"Only {server.peak} requests overlapped. Start them all as tasks before waiting."
    )
    assert elapsed < 0.4, f"Took {elapsed:.2f}s; 6 overlapping 0.1s requests take about 0.1s."


def test_nothing_left_running_after_return():
    urls = [BASE + "/a", BASE + "/b", BASE + "/c"]
    delays = {"/a": 0.01, "/b": 5.0, "/c": 5.0}
    _, _, still_running, server = run(delays, urls, per_request=0.1, total=1.0)
    assert still_running == 0, (
        f"{still_running} requests were still running when the function returned. Cancel the "
        "unfinished ones AND wait for them (asyncio.timeout + TaskGroup does both)."
    )
    assert sorted(server.cancelled) == ["/b", "/c"], (
        f"Cancelled requests: {server.cancelled}. The slow ones must be cancelled, not abandoned."
    )


def test_nothing_left_running_after_total_deadline():
    urls = [BASE + "/a", BASE + "/b"]
    _, _, still_running, _ = run({"/a": 5.0, "/b": 5.0}, urls, per_request=10.0, total=0.1)
    assert still_running == 0, (
        f"{still_running} requests kept running after the total deadline. asyncio.wait(timeout=...) "
        "alone does not cancel anything."
    )


def test_empty_list():
    result, _, _, _ = run({}, [], per_request=1.0, total=1.0)
    assert result == {}, "No urls means an empty dict."
