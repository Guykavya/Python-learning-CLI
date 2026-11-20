from solution import allow


def test_limit_in_one_window(r, clock):
    got = [allow(r, "ada", 3, 60, clock) for _ in range(5)]
    assert got == [True, True, True, False, False], f"limit=3: the first 3 are allowed, the rest refused; got {got}"


def test_key_and_ttl(r, clock):
    allow(r, "ada", 3, 60, clock)
    assert r.ttl("rate:ada:0") == 60, "The key is rate:<user>:<window number> and has a TTL of one window."


def test_expiry_set_once_not_extended(r, clock):
    allow(r, "ada", 100, 60, clock)
    clock.advance(30)
    allow(r, "ada", 100, 60, clock)
    assert r.ttl("rate:ada:0") == 30, \
        "The TTL must come from the FIRST request only (set ... nx=True). Re-setting ex= on every call keeps the key alive too long."


def test_new_window_resets(r, clock):
    for _ in range(3):
        allow(r, "ada", 3, 60, clock)
    assert allow(r, "ada", 3, 60, clock) is False
    clock.advance(60)
    assert allow(r, "ada", 3, 60, clock) is True, "A new window (window number 1) starts a fresh count."


def test_users_are_separate(r, clock):
    for _ in range(3):
        allow(r, "ada", 3, 60, clock)
    assert allow(r, "bo", 3, 60, clock) is True, "Each user has their own counter."


def test_counter_keeps_ttl_after_many_calls(r, clock):
    for _ in range(10):
        allow(r, "ada", 3, 60, clock)
    assert r.ttl("rate:ada:0") == 60, "After many calls the key must still have its TTL (INCR keeps it)."


def test_two_workers_at_the_limit(slow_redis, two_workers_at_once):
    import time
    now = time.time
    for _ in range(2):
        allow(slow_redis, "ada", 3, 3600, now)        # count is now 2 = limit - 1
    results = two_workers_at_once(lambda: allow(slow_redis, "ada", 3, 3600, now))
    assert sorted(results) == [False, True], \
        f"With the count at limit - 1, two simultaneous requests must give exactly one True; got {results}. " \
        "GET-then-SET lets both read 2. Use INCR, which reads and writes in one atomic command."
