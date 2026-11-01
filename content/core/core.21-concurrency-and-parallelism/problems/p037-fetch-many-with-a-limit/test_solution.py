import asyncio
import time

import httpx

from solution import fetch_many


class FakeServer:
    """Answers after a short delay and records how many requests are inside at once."""

    def __init__(self, delay=0.05):
        self.delay = delay
        self.in_flight = 0
        self.peak = 0
        self.seen = []

    async def handler(self, request):
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        self.seen.append(str(request.url))
        try:
            await asyncio.sleep(self.delay)
        finally:
            self.in_flight -= 1
        if request.url.path == "/missing":
            return httpx.Response(404)
        if request.url.path == "/broken":
            return httpx.Response(500)
        return httpx.Response(200, text="ok")


def run(urls, limit, delay=0.05):
    server = FakeServer(delay)

    async def main():
        async with httpx.AsyncClient(transport=httpx.MockTransport(server.handler)) as client:
            return await fetch_many(client, urls, limit)

    return asyncio.run(main()), server


def pages(n):
    return [f"https://site.test/page/{i}" for i in range(n)]


def test_every_url_gets_its_status():
    urls = pages(3) + ["https://site.test/missing", "https://site.test/broken"]
    result, server = run(urls, limit=2)
    expected = {u: 200 for u in pages(3)}
    expected["https://site.test/missing"] = 404
    expected["https://site.test/broken"] = 500
    assert result == expected, (
        f"Got {result}. Map every url to response.status_code; 404 and 500 are results, so do "
        "not call raise_for_status() here."
    )


def test_each_url_requested_once():
    urls = pages(6)
    _, server = run(urls, limit=3)
    assert sorted(server.seen) == sorted(urls), (
        f"The server saw {len(server.seen)} requests for {len(urls)} urls. Request each url "
        "exactly once."
    )


def test_peak_never_exceeds_limit():
    _, server = run(pages(10), limit=3)
    assert server.peak <= 3, (
        f"{server.peak} requests were in flight at once, limit was 3. Hold the semaphore "
        "around the whole request: 'async with semaphore: response = await client.get(url)'."
    )


def test_peak_reaches_the_limit():
    _, server = run(pages(10), limit=3)
    assert server.peak == 3, (
        f"Peak was {server.peak}, so you are not using all 3 slots. Did you await each request "
        "one by one? Create all coroutines and run them with asyncio.gather."
    )


def test_limit_one_is_sequential():
    _, server = run(pages(4), limit=1)
    assert server.peak == 1, "With limit=1 only one request may be in flight."


def test_limit_bigger_than_list_runs_all_at_once():
    _, server = run(pages(4), limit=50)
    assert server.peak == 4, f"Peak was {server.peak}; with a big limit all 4 should overlap."


def test_concurrent_is_faster_than_serial():
    start = time.perf_counter()
    run(pages(8), limit=4, delay=0.1)
    elapsed = time.perf_counter() - start
    # serial: 8 x 0.1 = 0.8 s; with 4 slots about 0.2 s
    assert elapsed < 0.55, (
        f"Took {elapsed:.2f}s for 8 requests of 0.1s with limit 4 (serial would be 0.8s). "
        "The requests are not overlapping."
    )


def test_empty_list():
    result, server = run([], limit=3)
    assert result == {}, "No urls means an empty dict (and no requests)."
    assert server.seen == []
