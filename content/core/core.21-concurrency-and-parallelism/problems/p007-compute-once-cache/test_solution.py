import threading
import time

from solution import OnceCache


def run_together(n, target):
    """Start n threads that call target(i) at the same moment; return their results."""
    barrier = threading.Barrier(n)
    results = [None] * n

    def work(i):
        barrier.wait()
        results[i] = target(i)

    threads = [threading.Thread(target=work, args=(i,), daemon=True) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert not any(t.is_alive() for t in threads), (
        "Threads were still blocked after 5 s. Is a lock never released, or does a thread "
        "wait on a lock that it already holds?"
    )
    return results


class SlowLoader:
    def __init__(self, delay, value):
        self.delay = delay
        self.value = value
        self.calls = 0
        self._lock = threading.Lock()

    def __call__(self):
        with self._lock:
            self.calls += 1
        time.sleep(self.delay)
        return self.value


def test_returns_and_caches_value():
    cache = OnceCache()
    loader = SlowLoader(0, [1, 2])
    first = cache.get("a", loader)
    second = cache.get("a", loader)
    assert first == [1, 2], f"get must return what compute() returned, got {first!r}."
    assert second is first, "The second get must return the cached object itself."
    assert loader.calls == 1, f"compute ran {loader.calls} times for a cached key; expected 1."


def test_same_key_computed_once():
    cache = OnceCache()
    loader = SlowLoader(0.1, {"name": "Asha"})
    results = run_together(8, lambda i: cache.get("u1", loader))
    assert loader.calls == 1, (
        f"8 threads asked for the same key at once and compute ran {loader.calls} times. "
        "'if key in cache' and 'cache[key] = value' are separate steps: all threads passed "
        "the check before any of them stored a value. Make the others WAIT for the first one."
    )
    assert all(r is results[0] for r in results), (
        "All threads must get the same cached object, not separate copies."
    )


def test_different_keys_run_in_parallel():
    cache = OnceCache()
    loaders = [SlowLoader(0.2, f"v{i}") for i in range(4)]
    start = time.perf_counter()
    results = run_together(4, lambda i: cache.get(f"k{i}", loaders[i]))
    elapsed = time.perf_counter() - start
    assert results == ["v0", "v1", "v2", "v3"], f"Wrong values {results}."
    assert elapsed < 0.5, (
        f"4 different keys with a 0.2 s compute took {elapsed:.2f} s (one after another would "
        "be 0.8 s). Do not hold one global lock while compute() runs; lock per key."
    )


def test_mixed_keys():
    cache = OnceCache()
    loaders = {"x": SlowLoader(0.1, "X"), "y": SlowLoader(0.1, "Y")}
    keys = ["x", "y"] * 4
    results = run_together(8, lambda i: cache.get(keys[i], loaders[keys[i]]))
    assert results == ["X", "Y"] * 4, f"Each thread must get its own key's value, got {results}."
    assert (loaders["x"].calls, loaders["y"].calls) == (1, 1), (
        f"compute calls were x={loaders['x'].calls}, y={loaders['y'].calls}; expected 1 each."
    )


def test_error_is_raised_and_not_cached():
    cache = OnceCache()
    attempts = []

    def flaky():
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError("db down")
        return "ok"

    try:
        cache.get("k", flaky)
    except ConnectionError:
        pass
    else:
        raise AssertionError("compute raised ConnectionError, get must let it propagate.")
    assert cache.get("k", flaky) == "ok", (
        "After a failed compute, the next get must try again (nothing cached for the key). "
        "If this hangs or fails, check that a lock is released when compute raises."
    )
    assert len(attempts) == 2, f"compute should have run twice in total, ran {len(attempts)}."
