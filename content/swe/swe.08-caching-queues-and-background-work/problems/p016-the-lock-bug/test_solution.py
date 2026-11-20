import re

from solution import acquire, new_token, release


def test_acquire_and_release(r):
    assert acquire(r, "report", "A") is True, "acquire() must return True (a bool) when the lock is free."
    assert r.get("lock:report") == "A", "The lock key is lock:<name> and holds the token."
    assert r.ttl("lock:report") == 10, "The lock must have an expiry (ttl=10 by default), or a crashed holder blocks everyone for ever."
    assert release(r, "report", "A") is True, "Releasing your own lock returns True."
    assert r.get("lock:report") is None


def test_second_acquire_fails(r):
    acquire(r, "report", "A")
    assert acquire(r, "report", "B") is False, "While A holds the lock, B must get False (not None)."


def test_the_chapter_story(r, clock):
    assert acquire(r, "report", "A")
    clock.advance(15)
    assert acquire(r, "report", "B"), "A's lock expired after 10 s, so B can take it."
    assert release(r, "report", "A") is False, "A's release must fail: the lock now holds B's token."
    assert r.get("lock:report") == "B", "A must NOT delete B's lock."
    assert acquire(r, "report", "C") is False, "C must not get the lock while B holds it."


def test_release_is_one_atomic_command(r):
    acquire(r, "report", "A")
    r.calls.clear()
    release(r, "report", "A")
    assert r.calls == ["delete_if_equals"], \
        f"release must use ONE command, r.delete_if_equals(...); you called {r.calls}. GET then DELETE is two steps and another worker can take the lock in between."


def test_release_of_free_lock(r):
    assert release(r, "nothing", "A") is False, "Releasing a lock that does not exist returns False."


def test_custom_ttl(r, clock):
    acquire(r, "job", "A", ttl=3)
    clock.advance(3)
    assert acquire(r, "job", "B", ttl=3), "With ttl=3 the lock expires after 3 s."


def test_tokens_are_random():
    tokens = {new_token() for _ in range(50)}
    assert len(tokens) == 50, "Every call to new_token() must give a different token (secrets.token_hex(16))."
    assert all(re.fullmatch(r"[0-9a-f]{32}", t) for t in tokens), "Use secrets.token_hex(16): 32 lowercase hex characters."
