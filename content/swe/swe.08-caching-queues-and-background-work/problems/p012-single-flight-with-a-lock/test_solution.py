import json
import time

from solution import get_single_flight


def test_hit_does_not_load(r, make_loader):
    loader = make_loader(delay=0)
    r.set("hot", json.dumps({"key": "hot", "value": 1}))
    assert get_single_flight(r, "hot", loader) == {"key": "hot", "value": 1}
    assert loader.calls == 0, "A cache hit must not call the loader."


def test_single_miss_loads_and_stores(r, make_loader):
    loader = make_loader(delay=0)
    assert get_single_flight(r, "k", loader, ttl=60) == {"key": "k", "value": 42}
    assert json.loads(r.get("k")) == {"key": "k", "value": 42}, "After loading, store the value as JSON under the key."
    assert 0 < r.ttl("k") <= 60, "Store with ex=ttl."
    assert r.get("lock:k") is None, "Delete the lock after loading."


def test_twenty_concurrent_misses_load_once(r, make_loader, concurrently):
    loader = make_loader(delay=0.05)
    results = concurrently(lambda: get_single_flight(r, "hot", loader), n=20)
    errors = [x for x in results if isinstance(x, Exception)]
    assert not errors, f"No caller may fail: {errors[:1]}"
    assert loader.calls == 1, \
        f"20 simultaneous misses must load ONCE, got {loader.calls}. Take the lock with cache.set('lock:hot', '1', ex=lock_ttl, nx=True) and let the losers wait."
    assert len(results) == 20 and all(x == {"key": "hot", "value": 42} for x in results), \
        "All 20 callers must get the value: waiters poll the cache until it appears."
    assert r.get("lock:hot") is None, "The lock must be released after the load."


def test_lock_released_when_loader_raises(r, make_loader):
    loader = make_loader(delay=0, fail=True)
    try:
        get_single_flight(r, "k", loader)
    except ConnectionError:
        pass
    else:
        raise AssertionError("The loader's exception must reach the caller (do not swallow it).")
    assert r.get("lock:k") is None, \
        "A loader that raises must still release the lock (try/finally), or every caller waits until the lock expires."
    assert r.get("k") is None, "Nothing may be cached when the load failed."


def test_waiter_falls_back_after_timeout(r, make_loader):
    loader = make_loader(delay=0)
    r.set("lock:k", "1", ex=10)                 # someone took the lock and then died without loading
    start = time.monotonic()
    value = get_single_flight(r, "k", loader, poll=0.01, timeout=0.2)
    took = time.monotonic() - start
    assert value == {"key": "k", "value": 42}, "After the timeout the waiter loads the value itself."
    assert loader.calls == 1
    assert 0.15 <= took < 3, f"The waiter should wait about `timeout` (0.2 s) before loading itself; it took {took:.2f} s."


def test_waiter_returns_as_soon_as_value_appears(r, make_loader):
    loader = make_loader(delay=0)
    r.set("lock:k", "1", ex=10)
    import threading

    def fill_later():
        time.sleep(0.1)
        r.set("k", json.dumps({"key": "k", "value": 7}))

    threading.Thread(target=fill_later).start()
    start = time.monotonic()
    assert get_single_flight(r, "k", loader, poll=0.01, timeout=3) == {"key": "k", "value": 7}, \
        "A waiter must return the value the other caller stored."
    assert loader.calls == 0, "The waiter must not load when the value appears in time."
    assert time.monotonic() - start < 2, "Return as soon as the value is in the cache; do not wait for the full timeout."
