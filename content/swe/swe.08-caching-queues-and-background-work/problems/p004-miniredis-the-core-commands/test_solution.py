import threading

import pytest

from solution import MiniRedis


@pytest.fixture
def r(clock):
    return MiniRedis(now=clock)


def test_set_and_get(r):
    assert r.set("greeting", "hello") is True, "set() returns True when it stores the value."
    assert r.get("greeting") == "hello"
    assert r.get("missing") is None, "A missing key gives None."


def test_values_are_strings(r):
    r.set("n", 5)
    assert r.get("n") == "5", "Redis stores strings: set('n', 5) then get('n') gives '5' (use str(value))."


def test_set_nx(r):
    assert r.set("lock", "A", nx=True) is True, "nx=True on a new key stores it and returns True."
    assert r.set("lock", "B", nx=True) is None, "nx=True on an existing key must return None (not False) and not overwrite."
    assert r.get("lock") == "A", "The value must still be A: nx means 'only if it does not exist'."


def test_set_nx_after_expiry(r, clock):
    r.set("lock", "A", ex=10, nx=True)
    clock.advance(10)
    assert r.set("lock", "B", ex=10, nx=True) is True, "An expired key does not exist any more, so nx=True must succeed."
    assert r.get("lock") == "B"


def test_ex_and_ttl(r, clock):
    r.set("greeting", "hello", ex=30)
    assert r.ttl("greeting") == 30, "Right after set(ex=30) the TTL is 30."
    clock.advance(0.5)
    assert r.ttl("greeting") == 30, "TTL rounds UP (math.ceil): 29.5 s left shows as 30."
    clock.advance(29.5)
    assert r.get("greeting") is None, "At exactly the deadline the key is gone (deadline <= now)."
    assert r.ttl("greeting") == -2, "TTL of a missing (expired) key is -2."


def test_ttl_codes(r):
    r.set("forever", "x")
    assert r.ttl("forever") == -1, "A key without expiry has TTL -1."
    assert r.ttl("nothing") == -2, "A key that does not exist has TTL -2."


def test_plain_set_removes_old_expiry(r, clock):
    r.set("k", "v1", ex=10)
    r.set("k", "v2")
    assert r.ttl("k") == -1, "A plain set() replaces the value AND removes the old expiry, as in Redis."
    clock.advance(100)
    assert r.get("k") == "v2"


def test_incr(r):
    assert r.incr("visits") == 1, "INCR on a missing key starts from 0 and returns 1."
    assert r.incr("visits") == 2
    assert r.incr("visits", 10) == 12, "incr(key, 10) adds 10."
    assert r.get("visits") == "12", "The counter is stored as a string."
    assert r.incr("visits", -2) == 10, "A negative amount decrements."


def test_incr_keeps_ttl(r, clock):
    r.set("rate", 0, ex=60)
    r.incr("rate")
    assert r.ttl("rate") == 60, "INCR must KEEP the existing expiry. Did incr() remove the deadline like set() does?"
    clock.advance(60)
    assert r.get("rate") is None


def test_incr_after_expiry_restarts(r, clock):
    r.set("rate", 5, ex=10)
    clock.advance(10)
    assert r.incr("rate") == 1, "An expired counter is gone: INCR starts again from 0."
    assert r.ttl("rate") == -1, "The new key created by INCR has no expiry."


def test_incr_not_an_integer(r):
    r.set("name", "ada")
    with pytest.raises(ValueError, match="^ERR value is not an integer"):
        r.incr("name")
    assert r.get("name") == "ada", "A failed INCR must leave the value unchanged."


def test_expire(r, clock):
    assert r.expire("missing", 10) is False, "expire() on a missing key returns False."
    r.set("k", "v")
    assert r.expire("k", 10) is True
    assert r.ttl("k") == 10
    clock.advance(10)
    assert r.exists("k") == 0, "After the expiry the key is gone for exists() too."


def test_delete_and_exists(r, clock):
    r.set("a", 1)
    r.set("b", 2, ex=5)
    clock.advance(5)
    assert r.exists("a", "b", "c") == 1, "exists() counts live keys only: b expired, c never existed."
    assert r.delete("a", "b", "c") == 1, "delete() returns how many LIVE keys it removed: an expired key does not count."
    assert r.get("a") is None


def test_lazy_expiry_frees_memory(r, clock):
    r.set("tmp", "x", ex=1)
    clock.advance(2)
    r.get("tmp")
    assert "tmp" not in r._data and "tmp" not in r._expires, \
        "When a command finds an expired key it must remove it from BOTH dictionaries (lazy expiry)."


def test_incr_is_atomic_across_threads():
    r = MiniRedis()
    gate = threading.Barrier(8)

    def worker():
        gate.wait()
        for _ in range(500):
            r.incr("hits")

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    assert r.get("hits") == "4000", f"8 threads x 500 INCRs must give 4000, got {r.get('hits')}: hold the lock for the whole command."
