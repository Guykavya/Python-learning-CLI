import threading
import time

from solution import fetch_all


class FakeWeb:
    def __init__(self, delay=0.2, bad=()):
        self.delay = delay
        self.bad = set(bad)
        self.running = 0
        self.peak = 0
        self.calls = []
        self.threads = set()
        self.lock = threading.Lock()

    def __call__(self, url):
        with self.lock:
            self.running += 1
            self.peak = max(self.peak, self.running)
            self.calls.append(url)
            self.threads.add(threading.current_thread())
        try:
            time.sleep(self.delay)
            if url in self.bad:
                raise ConnectionError(f"cannot reach {url}")
            return url.upper()
        finally:
            with self.lock:
                self.running -= 1


def test_values_by_url():
    web = FakeWeb(0.01)
    result = fetch_all(["a", "b", "c"], web, 2)
    assert result == {"a": "A", "b": "B", "c": "C"}, (
        f"Got {result}. Map each url to what fetch(url) returned (keep a dict future -> url)."
    )
    assert sorted(web.calls) == ["a", "b", "c"], f"fetch must run once per url, got {web.calls}."


def test_exception_object_is_stored():
    web = FakeWeb(0.01, bad={"down.org"})
    result = fetch_all(["ok.com", "down.org"], web, 2)
    assert result.get("ok.com") == "OK.COM", "A failure must not stop the other urls."
    err = result.get("down.org")
    assert isinstance(err, ConnectionError) and str(err) == "cannot reach down.org", (
        f"For a url whose fetch raised, store the exception object itself, got {err!r}. "
        "future.result() re-raises it: catch it around that call."
    )


def test_runs_in_parallel():
    web = FakeWeb(0.2)
    urls = [f"u{i}" for i in range(6)]
    start = time.perf_counter()
    result = fetch_all(urls, web, 6)
    elapsed = time.perf_counter() - start
    assert len(result) == 6, f"Expected 6 results, got {len(result)}."
    assert elapsed < 0.6, (
        f"6 fetches of 0.2 s with 6 workers took {elapsed:.2f} s (one by one: 1.2 s). Submit "
        "ALL jobs first, then collect; calling result() right after each submit waits each time."
    )
    assert threading.main_thread() not in web.threads, "fetch must run in pool threads."


def test_respects_worker_count():
    web = FakeWeb(0.05)
    fetch_all([f"u{i}" for i in range(8)], web, 2)
    assert web.peak <= 2, (
        f"{web.peak} fetches ran at once with workers=2. Pass max_workers=workers to the pool."
    )
    assert web.peak == 2, f"With 8 urls and 2 workers, 2 should run at once; peak was {web.peak}."


def test_all_errors_and_empty():
    web = FakeWeb(0.01, bad={"x", "y"})
    result = fetch_all(["x", "y"], web, 2)
    assert all(isinstance(v, ConnectionError) for v in result.values()) and len(result) == 2, (
        f"Both urls failed; both should map to their ConnectionError, got {result}."
    )
    assert fetch_all([], web, 3) == {}, "No urls: return {}."
