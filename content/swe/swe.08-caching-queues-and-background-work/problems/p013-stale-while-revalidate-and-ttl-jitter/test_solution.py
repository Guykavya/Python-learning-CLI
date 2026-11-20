import json

import pytest

from solution import get_swr, jittered

MID = lambda: 0.5        # with this rng, jittered(x, MID) == x


class Loader:
    def __init__(self, values=(1, 2, 3, 4, 5), fail=False):
        self.values, self.fail, self.calls = list(values), fail, 0

    def __call__(self, key):
        self.calls += 1
        if self.fail:
            raise ConnectionError("database is down")
        return self.values[self.calls - 1]


def test_jitter_range():
    assert jittered(100, lambda: 0.0) == pytest.approx(90), "rng()=0 gives 90% of the value."
    assert jittered(100, lambda: 0.5) == pytest.approx(100), "rng()=0.5 gives the value itself."
    assert jittered(100, lambda: 0.999) == pytest.approx(109.98), "rng() near 1 gives almost 110%: 100 * (0.9 + 0.2 * 0.999)."


def test_cold_miss_then_fresh(r, clock):
    loader = Loader()
    assert get_swr(r, "k", loader, clock, rng=MID) == (1, "cold miss"), "No entry: load and return status 'cold miss'."
    clock.advance(59)
    assert get_swr(r, "k", loader, clock, rng=MID) == (1, "fresh"), "Before the soft deadline (60 s): the cached value, 'fresh'."
    assert loader.calls == 1


def test_entry_format_and_hard_ttl(r, clock):
    get_swr(r, "k", Loader(), clock, soft=60, hard=600, rng=MID)
    entry = json.loads(r.get("k"))
    assert entry == {"value": 1, "soft_expires": clock() + 60}, f"Store JSON {{'value': ..., 'soft_expires': now + soft}}; got {entry}"
    assert r.ttl("k") == 600, "The Redis expiry is the HARD deadline (600 s with no jitter)."


def test_jitter_is_applied(r, clock):
    get_swr(r, "k", Loader(), clock, soft=60, hard=600, rng=lambda: 0.0)
    assert r.ttl("k") == 540, "With rng()=0 the hard TTL must be 90% of 600 = 540: apply jittered() to hard."
    assert json.loads(r.get("k"))["soft_expires"] == pytest.approx(clock() + 54), "And soft_expires = now + jittered(soft) = now + 54."


def test_one_caller_refreshes_after_soft(r, clock):
    loader = Loader()
    get_swr(r, "k", loader, clock, rng=MID)
    clock.advance(60)
    assert get_swr(r, "k", loader, clock, rng=MID) == (2, "refreshed"), \
        "At the soft deadline the caller that wins lock:k reloads and returns the NEW value with status 'refreshed'."
    assert r.get("lock:k") is None, "Delete the lock after refreshing."
    assert get_swr(r, "k", loader, clock, rng=MID) == (2, "fresh"), "After a refresh the entry is fresh again."


def test_others_get_stale_without_waiting(r, clock):
    loader = Loader()
    get_swr(r, "k", loader, clock, rng=MID)
    clock.advance(70)
    r.set("lock:k", "1", ex=10)
    assert get_swr(r, "k", loader, clock, rng=MID) == (1, "stale"), \
        "Past the soft deadline with the lock taken: return the OLD value at once, status 'stale'."
    assert loader.calls == 1, "A caller that did not get the lock must not call the loader."
    assert r.get("lock:k") == "1", "Do not delete someone else's lock."


def test_lock_uses_nx_and_ex(r, clock):
    calls = []
    real_set = r.set

    def spy(key, value, **kw):
        calls.append((key, kw))
        return real_set(key, value, **kw)

    r.set = spy
    loader = Loader()
    get_swr(r, "k", loader, clock, rng=MID)
    clock.advance(61)
    get_swr(r, "k", loader, clock, rng=MID)
    lock_calls = [kw for key, kw in calls if key == "lock:k"]
    assert lock_calls and lock_calls[0].get("nx") is True and lock_calls[0].get("ex") == 10, \
        f"Take the lock with cache.set('lock:k', '1', ex=10, nx=True); got {lock_calls}"


def test_hard_expiry_is_cold(r, clock):
    loader = Loader()
    get_swr(r, "k", loader, clock, rng=MID)
    clock.advance(600)
    assert get_swr(r, "k", loader, clock, rng=MID) == (2, "cold miss"), "After the hard TTL the entry is gone: a cold miss."


def test_failed_refresh_serves_stale(r, clock):
    good = Loader()
    get_swr(r, "k", good, clock, rng=MID)
    clock.advance(61)
    bad = Loader(fail=True)
    assert get_swr(r, "k", bad, clock, rng=MID) == (1, "stale"), \
        "If the refresh fails, keep serving the old value ('stale') instead of failing the request."
    assert r.get("lock:k") is None, "Release the lock after a failed refresh, so the next caller can try again."


def test_failed_cold_miss_raises(r, clock):
    with pytest.raises(ConnectionError):
        get_swr(r, "k", Loader(fail=True), clock, rng=MID)
