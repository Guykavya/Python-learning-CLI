import pytest

from solution import cache, logger, rate_limit, retry, timer


def make_clock(start=0.0):
    """A fake clock. clock() reads the time; advance(s) moves it forward. No real waiting."""
    now = [start]

    def clock():
        return now[0]

    def advance(seconds):
        now[0] += seconds

    return clock, advance


def flaky(failures, exc=ConnectionError):
    """A function that raises `exc` for its first `failures` calls, then returns 'ok <x>'."""
    state = {"calls": 0}

    def fetch(x):
        """Fetch something."""
        state["calls"] += 1
        if state["calls"] <= failures:
            raise exc(f"fail {state['calls']}")
        return f"ok {x}"
    return fetch, state


# ---------------------------------------------------------------- timer

def test_timer_records_elapsed():
    clock, advance = make_clock(100.0)
    log = []

    @timer(log, clock=clock)
    def work(seconds):
        advance(seconds)
        return seconds * 2

    assert work(3) == 6, "timer must return the function's result."
    assert work(0.5) == 1
    assert log == [("work", 3.0), ("work", 0.5)], "Append (name, clock() after - clock() before) for each call."


def test_timer_records_even_on_error():
    clock, advance = make_clock()
    log = []

    @timer(log, clock=clock)
    def boom():
        advance(2)
        raise KeyError("x")

    with pytest.raises(KeyError):
        boom()
    assert log == [("boom", 2)], "Record the time even when the call raises: use try/finally, and do not swallow the error."


# ---------------------------------------------------------------- retry

def test_retry_backoff():
    waits = []
    fetch, state = flaky(3)
    fetch = retry(attempts=4, exceptions=(ConnectionError,), delay=1, backoff=2, sleep=waits.append)(fetch)
    assert fetch("a") == "ok a", "The fourth attempt works: return its result."
    assert state["calls"] == 4
    assert waits == [1, 2, 4], "Wait delay, then delay*backoff, then delay*backoff**2 ... between attempts."


def test_retry_gives_up_with_last_error():
    waits = []
    fetch, state = flaky(10)
    fetch = retry(attempts=3, delay=0.5, backoff=3, sleep=waits.append)(fetch)
    with pytest.raises(ConnectionError) as info:
        fetch("a")
    assert str(info.value) == "fail 3", "Re-raise the exception from the LAST attempt."
    assert state["calls"] == 3, "attempts=3 is three calls in total."
    assert waits == [0.5, 1.5], "No sleep after the last attempt."


def test_retry_only_listed_exceptions():
    waits = []
    fetch, state = flaky(1, exc=ValueError)
    fetch = retry(attempts=5, exceptions=(ConnectionError, TimeoutError), sleep=waits.append)(fetch)
    with pytest.raises(ValueError):
        fetch("a")
    assert state["calls"] == 1 and waits == [], "An exception that is not listed is raised at once: no retry, no sleep."


def test_retry_checks_settings():
    with pytest.raises(ValueError):
        retry(attempts=0)
    with pytest.raises(ValueError):
        retry(delay=-1)
    with pytest.raises(ValueError):
        retry(backoff=0.5)


# ---------------------------------------------------------------- cache

def test_cache_hits_and_info():
    calls = []

    @cache()
    def square(n):
        calls.append(n)
        return n * n

    assert square(3) == 9 and square(3) == 9 and square(4) == 16
    assert calls == [3, 4], "A repeated call must be answered from the cache."
    assert square.cache_info() == {"hits": 1, "misses": 2, "size": 2}, "cache_info() returns hits, misses and size as a dict."
    square.cache_clear()
    assert square.cache_info() == {"hits": 0, "misses": 0, "size": 0}, "cache_clear() empties the cache and resets the counters."
    square(3)
    assert calls == [3, 4, 3]


def test_cache_keywords_and_none():
    calls = []

    @cache()
    def find(a, b=0):
        calls.append((a, b))
        return None

    assert find(1, b=2) is None
    assert find(1, b=2) is None
    assert calls == [(1, 2)], "None is a real result: it must be cached too (check `key in store`)."


def test_cache_maxsize_lru():
    calls = []

    @cache(maxsize=2)
    def f(n):
        calls.append(n)
        return n

    f(1)
    f(2)
    f(1)          # hit: 1 is now the most recently used
    f(3)          # full: evict 2, the least recently used
    assert f.cache_info()["size"] == 2, "Never keep more than maxsize entries."
    f(1)
    assert calls == [1, 2, 3], "1 was used recently, so it must still be cached. Evict the LEAST RECENTLY USED entry."
    f(2)
    assert calls == [1, 2, 3, 2], "2 was evicted when 3 came in, so it is computed again."


def test_cache_ttl_with_fake_clock():
    clock, advance = make_clock()
    calls = []

    @cache(ttl=10, clock=clock)
    def price(item):
        calls.append(item)
        return len(calls)

    assert price("pen") == 1
    advance(9.9)
    assert price("pen") == 1, "9.9 seconds after storing, the entry is still fresh (ttl=10)."
    advance(0.1)
    assert price("pen") == 2, "At exactly ttl seconds the entry has expired: compute again."
    assert price.cache_info() == {"hits": 1, "misses": 2, "size": 1}, "An expired entry counts as a miss and is replaced, not added twice."


def test_cache_ttl_is_from_store_time():
    clock, advance = make_clock()
    calls = []

    @cache(ttl=5, clock=clock)
    def get(k):
        calls.append(k)
        return k

    get("a")
    advance(4)
    get("a")           # hit; reading does not refresh the time
    advance(2)
    get("a")
    assert calls == ["a", "a"], "ttl counts from when the result was STORED, not from the last read."


def test_cache_does_not_store_errors():
    attempts = []

    @cache()
    def risky(x):
        attempts.append(x)
        if len(attempts) == 1:
            raise ValueError("first time")
        return x

    with pytest.raises(ValueError):
        risky(1)
    assert risky(1) == 1 and len(attempts) == 2, "A call that raised must not leave anything in the cache."


def test_cache_checks_settings():
    with pytest.raises(ValueError):
        cache(maxsize=0)
    with pytest.raises(ValueError):
        cache(ttl=0)


# ---------------------------------------------------------------- rate_limit

def test_rate_limit_blocks_extra_calls():
    clock, advance = make_clock()
    calls = []

    @rate_limit(calls=2, period=10, clock=clock)
    def ping(x):
        calls.append(x)
        return x

    assert ping(1) == 1 and ping(2) == 2, "The first `calls` calls are allowed."
    with pytest.raises(RuntimeError) as info:
        ping(3)
    msg = str(info.value)
    assert "rate limit" in msg and "ping" in msg, f"The error message must say 'rate limit' and name the function. Got: {msg}"
    assert calls == [1, 2], "A blocked call must not run the function."


def test_rate_limit_window_slides():
    clock, advance = make_clock()

    @rate_limit(calls=2, period=10, clock=clock)
    def ping():
        return "pong"

    ping()             # t = 0
    advance(4)
    ping()             # t = 4
    advance(5)         # t = 9: both still count
    with pytest.raises(RuntimeError):
        ping()
    advance(1)         # t = 10: the call at t = 0 stops counting
    assert ping() == "pong", "A call made at time t stops counting at t + period."
    with pytest.raises(RuntimeError):
        ping()         # t = 10: calls at 4 and 10 count
    advance(4)         # t = 14: the call at 4 stops counting
    assert ping() == "pong"


def test_rate_limit_rejected_calls_do_not_count():
    clock, advance = make_clock()

    @rate_limit(calls=1, period=5, clock=clock)
    def go():
        return True

    go()               # t = 0
    for _ in range(3):
        advance(1)
        with pytest.raises(RuntimeError):
            go()       # t = 1, 2, 3: blocked, and NOT recorded
    advance(2)         # t = 5
    assert go() is True, "Blocked calls must not be recorded, or the limit never opens again."


def test_rate_limit_per_function():
    clock, advance = make_clock()
    limit = rate_limit(calls=1, period=60, clock=clock)

    @limit
    def a():
        return "a"

    @limit
    def b():
        return "b"

    assert a() == "a" and b() == "b", "Each decorated function has its own window: create the list of times in decorator()."


def test_rate_limit_checks_settings():
    with pytest.raises(ValueError):
        rate_limit(calls=0, period=1)
    with pytest.raises(ValueError):
        rate_limit(calls=1, period=0)


# ---------------------------------------------------------------- logger

def test_logger_records_calls_and_results():
    log = []

    @logger(log)
    def add(a, b=0):
        return a + b

    assert add(2, b=3) == 5
    assert log == [("call", "add", (2,), {"b": 3}), ("return", "add", 5)], (
        "Record ('call', name, args, kwargs) before and ('return', name, result) after."
    )


def test_logger_records_exceptions():
    log = []

    @logger(log)
    def div(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        div(1, 0)
    assert log == [("call", "div", (1, 0), {}), ("raise", "div", "ZeroDivisionError")], (
        "On an exception record ('raise', name, class name) and re-raise it."
    )


# ---------------------------------------------------------------- metadata

def test_all_use_wraps():
    clock, _ = make_clock()
    decorators = [
        timer([], clock=clock),
        retry(sleep=lambda s: None),
        cache(),
        rate_limit(5, 1, clock=clock),
        logger([]),
    ]
    for deco in decorators:
        def target(x):
            """The docstring."""
            return x

        wrapped = deco(target)
        assert wrapped is not target, "Each decorator must return a new wrapper function."
        assert wrapped.__name__ == "target" and wrapped.__doc__ == "The docstring.", (
            "Every decorator in the toolkit must use functools.wraps."
        )
        assert wrapped.__wrapped__ is target, "functools.wraps also sets __wrapped__ to the original function."
        assert wrapped(7) == 7


# ---------------------------------------------------------------- stacking

def test_logger_outside_retry_sees_one_call():
    log, waits = [], []
    fetch, state = flaky(2)

    @logger(log)
    @retry(attempts=3, exceptions=(ConnectionError,), delay=1, backoff=2, sleep=waits.append)
    def get(x):
        return fetch(x)

    assert get("p") == "ok p"
    assert log == [("call", "get", ("p",), {}), ("return", "get", "ok p")], (
        "With logger OUTSIDE retry, the logger sees one call: the retries happen inside it."
    )
    assert waits == [1, 2]


def test_retry_outside_logger_sees_every_attempt():
    log, waits = [], []
    fetch, state = flaky(2)

    @retry(attempts=3, exceptions=(ConnectionError,), delay=1, backoff=2, sleep=waits.append)
    @logger(log)
    def get(x):
        return fetch(x)

    assert get("p") == "ok p"
    assert [entry[0] for entry in log] == ["call", "raise", "call", "raise", "call", "return"], (
        "With retry OUTSIDE logger, every attempt goes through the logger."
    )
    assert log[1] == ("raise", "get", "ConnectionError")


def test_cache_outside_rate_limit_saves_quota():
    clock, advance = make_clock()
    calls = []

    @cache()
    @rate_limit(calls=2, period=60, clock=clock)
    def lookup(word):
        calls.append(word)
        return word.upper()

    assert [lookup("a"), lookup("a"), lookup("a"), lookup("b")] == ["A", "A", "A", "B"], (
        "Cache hits never reach the rate limiter below, so they do not use up the limit."
    )
    with pytest.raises(RuntimeError):
        lookup("c")
    assert lookup("a") == "A", "A cached answer is still available while the limit is reached."
    assert calls == ["a", "b"]


def test_timer_outside_cache_measures_hits():
    clock, advance = make_clock()
    log = []

    @timer(log, clock=clock)
    @cache()
    def slow(n):
        advance(5)
        return n

    slow(1)
    slow(1)
    assert log == [("slow", 5), ("slow", 0)], "The second call is a cache hit: the body does not run, so no time passes."


def test_full_stack_keeps_metadata_and_works():
    clock, advance = make_clock()
    log, times, waits = [], [], []
    fetch, state = flaky(1)

    @logger(log)
    @timer(times, clock=clock)
    @retry(attempts=2, delay=3, sleep=lambda s: (waits.append(s), advance(s)))
    @cache(maxsize=10)
    @rate_limit(calls=5, period=60, clock=clock)
    def get(x):
        """Get x."""
        return fetch(x)

    assert get("q") == "ok q"
    assert get("q") == "ok q"
    assert state["calls"] == 2, "First attempt fails, retry works, then the cache answers the second get."
    assert waits == [3]
    assert times == [("get", 3), ("get", 0)], "timer is outside retry, so it includes the 3 seconds of (fake) sleep."
    assert [entry[0] for entry in log] == ["call", "return", "call", "return"]
    assert get.__name__ == "get" and get.__doc__ == "Get x.", "With wraps in every layer, the name survives five layers."
