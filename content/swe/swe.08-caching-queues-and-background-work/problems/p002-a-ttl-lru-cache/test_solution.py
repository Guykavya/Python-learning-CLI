import pytest

from solution import TTLCache


def test_set_then_get(clock):
    cache = TTLCache(maxsize=3, ttl=10, now=clock)
    cache.set("a", "A")
    assert cache.get("a") == "A", "A value just stored must come back from get()."
    assert len(cache) == 1, f"One entry stored: len() must be 1, got {len(cache)}"


def test_missing_key_returns_default(clock):
    cache = TTLCache(now=clock)
    assert cache.get("nope") is None, "A missing key returns None by default."
    assert cache.get("nope", "fallback") == "fallback", "get(key, default) must return the default on a miss."


def test_expires_exactly_at_ttl(clock):
    cache = TTLCache(maxsize=3, ttl=10, now=clock)
    cache.set("a", "A")
    clock.advance(9.999)
    assert cache.get("a") == "A", "Before the ttl is over the entry is still valid."
    clock.advance(0.001)
    assert cache.get("a") is None, "At exactly ttl seconds the entry counts as expired (expires_at <= now)."


def test_expired_entry_is_removed(clock):
    cache = TTLCache(maxsize=3, ttl=10, now=clock)
    cache.set("a", "A")
    clock.advance(11)
    cache.get("a")
    assert len(cache) == 0, "get() of an expired entry must delete it (lazy expiry), so len() drops to 0."


def test_per_entry_ttl(clock):
    cache = TTLCache(ttl=10, now=clock)
    cache.set("short", 1, ttl=2)
    cache.set("normal", 2)
    clock.advance(5)
    assert cache.get("short") is None, "set(..., ttl=2) must override the cache's ttl for that entry."
    assert cache.get("normal") == 2, "ttl=None means: use the cache's ttl (10 s)."


def test_set_again_resets_expiry(clock):
    cache = TTLCache(ttl=10, now=clock)
    cache.set("a", 1)
    clock.advance(8)
    cache.set("a", 2)
    clock.advance(8)
    assert cache.get("a") == 2, "Storing a key again replaces the value and starts a new ttl from now."


def test_evicts_least_recently_used(clock):
    cache = TTLCache(maxsize=3, ttl=100, now=clock)
    for key in "abc":
        cache.set(key, key.upper())
    assert cache.get("a") == "A"
    cache.set("d", "D")
    assert len(cache) == 3, f"maxsize=3: after adding a 4th key the size must stay 3, got {len(cache)}"
    assert cache.get("b") is None, "b was the least RECENTLY USED (a was just read), so b must be evicted."
    assert cache.get("a") == "A", "a was read just before d was added: it must survive. Did you evict the oldest INSERTED key (FIFO)?"
    assert cache.get("c") == "C" and cache.get("d") == "D"


def test_set_counts_as_use(clock):
    cache = TTLCache(maxsize=2, ttl=100, now=clock)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("a", 10)          # a is used again
    cache.set("c", 3)
    assert cache.get("b") is None, "Updating a with set() makes it the most recently used, so b is evicted."
    assert cache.get("a") == 10


def test_hits_misses_ratio(clock):
    cache = TTLCache(maxsize=3, ttl=10, now=clock)
    assert cache.hit_ratio == 0.0, "With no gets yet, hit_ratio must be 0.0 (not a ZeroDivisionError)."
    cache.set("a", 1)
    cache.get("a")
    cache.get("a")
    cache.get("x")
    clock.advance(20)
    cache.get("a")
    assert (cache.hits, cache.misses) == (2, 2), f"Expected 2 hits and 2 misses (one missing, one expired), got {(cache.hits, cache.misses)}"
    assert cache.hit_ratio == pytest.approx(0.5), "hit_ratio = hits / (hits + misses)."


def test_set_does_not_count_as_hit_or_miss(clock):
    cache = TTLCache(now=clock)
    cache.set("a", 1)
    cache.set("b", 2)
    assert (cache.hits, cache.misses) == (0, 0), "Only get() counts hits and misses, not set()."


def test_delete(clock):
    cache = TTLCache(now=clock)
    cache.set("a", 1)
    cache.delete("a")
    cache.delete("never-there")
    assert cache.get("a") is None and len(cache) == 0, "delete() removes the key and does not fail for a missing one."


def test_falsy_values_are_hits(clock):
    cache = TTLCache(now=clock)
    cache.set("zero", 0)
    cache.set("empty", "")
    assert cache.get("zero", "MISS") == 0, "0 is a real cached value: test 'is None' on the stored entry, not truthiness."
    assert cache.get("empty", "MISS") == ""
    assert cache.hits == 2


def test_skewed_traffic_hit_ratio():
    import random
    clock = [0.0]
    cache = TTLCache(maxsize=10, ttl=1000, now=lambda: clock[0])
    rng = random.Random(7)
    for _ in range(2000):
        k = min(int(rng.paretovariate(1.2)), 30)
        if cache.get(k) is None:
            cache.set(k, k)
    assert cache.hit_ratio > 0.8, f"Skewed traffic with room for 10 keys should give a high hit ratio; got {cache.hit_ratio:.2f}. Is LRU working?"
