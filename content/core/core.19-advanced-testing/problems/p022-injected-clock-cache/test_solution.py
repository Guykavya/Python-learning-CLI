import time

import pytest

from solution import ExpiringCache


class FakeClock:
    def __init__(self, start=1000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def cache(clock):
    return ExpiringCache(ttl=10, clock=clock)


def test_value_is_returned_while_fresh(cache, clock):
    cache.set("a", 1)
    clock.advance(9.9)
    assert cache.get("a") == 1, "An entry is valid while now - set_time < ttl."


def test_value_expires_exactly_at_ttl(cache, clock):
    cache.set("a", 1)
    clock.advance(10)
    assert cache.get("a") is None, "At now - set_time == ttl the entry has expired (use < not <=)."


def test_default_for_missing_and_expired(cache, clock):
    assert cache.get("nope", "dflt") == "dflt", "A missing key returns the default."
    cache.set("a", 1)
    clock.advance(50)
    assert cache.get("a", "dflt") == "dflt", "An expired key returns the default too."


def test_set_again_restarts_the_lifetime(cache, clock):
    cache.set("a", 1)
    clock.advance(8)
    cache.set("a", 2)
    clock.advance(8)
    assert cache.get("a") == 2, "A second set must replace the value and restart the lifetime."


def test_entries_expire_independently(cache, clock):
    cache.set("old", 1)
    clock.advance(6)
    cache.set("new", 2)
    clock.advance(6)
    assert cache.get("old") is None and cache.get("new") == 2, (
        "Each entry has its own set-time: old (12 s) is expired, new (6 s) is not.")


def test_len_counts_only_live_entries(cache, clock):
    cache.set("a", 1)
    clock.advance(6)
    cache.set("b", 2)
    assert len(cache) == 2
    clock.advance(5)
    assert len(cache) == 1, "len must not count expired entries."
    clock.advance(10)
    assert len(cache) == 0


@pytest.mark.parametrize("ttl", [0, -1])
def test_bad_ttl(ttl):
    with pytest.raises(ValueError):
        ExpiringCache(ttl=ttl, clock=lambda: 0)


def test_real_time_is_never_used(cache, clock, monkeypatch):
    def boom():
        raise AssertionError("the real clock was used; call self.clock() instead")
    for name in ("time", "monotonic", "perf_counter"):
        monkeypatch.setattr(time, name, boom)
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert len(cache) == 1
