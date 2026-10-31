import time

import pytest

import solution
from solution import RateLimiter


@pytest.fixture
def clock(monkeypatch):
    state = {"t": 500.0, "reads": 0}

    def fake_now():
        state["reads"] += 1
        return state["t"]

    monkeypatch.setattr(solution, "now", fake_now)
    return state


def test_allows_up_to_the_limit(clock):
    limiter = RateLimiter(3, 10)
    assert [limiter.allow() for _ in range(3)] == [True, True, True], "The first 3 calls are allowed."
    assert limiter.allow() is False, "The 4th call inside the window must be refused."


def test_slot_frees_exactly_at_the_border(clock):
    limiter = RateLimiter(1, 10)
    assert limiter.allow() is True
    clock["t"] += 9.9
    assert limiter.allow() is False, "9.9 s later the slot is still taken."
    clock["t"] += 0.1
    assert limiter.allow() is True, "After exactly per_seconds the slot is free (now - t >= per_seconds)."


def test_refused_calls_are_not_recorded(clock):
    limiter = RateLimiter(1, 10)
    limiter.allow()
    clock["t"] += 5
    assert limiter.allow() is False
    clock["t"] += 5
    assert limiter.allow() is True, (
        "Only allowed calls count. The refused call at t=5 must not push the window forward.")


def test_window_slides(clock):
    limiter = RateLimiter(2, 10)
    assert limiter.allow() is True       # t=0
    clock["t"] += 6
    assert limiter.allow() is True       # t=6
    clock["t"] += 5                      # t=11: first call expired, second not
    assert limiter.allow() is True
    assert limiter.allow() is False, "At t=11 the calls from t=6 and t=11 fill the limit of 2."


def test_reads_the_clock_once_per_call(clock):
    limiter = RateLimiter(2, 10)
    limiter.allow()
    limiter.allow()
    limiter.allow()
    assert clock["reads"] == 3, "Call now() exactly once in each allow()."


def test_works_when_time_monotonic_is_patched(monkeypatch):
    values = iter([1.0, 1.0, 100.0])
    monkeypatch.setattr(time, "monotonic", lambda: next(values))
    limiter = RateLimiter(1, 10)
    assert limiter.allow() is True
    assert limiter.allow() is False
    assert limiter.allow() is True, (
        "now() must call time.monotonic() through the module (import time), "
        "so that patching time.monotonic reaches it.")


@pytest.mark.parametrize("args", [(0, 10), (3, 0), (3, -1)])
def test_bad_arguments(args):
    with pytest.raises(ValueError):
        RateLimiter(*args)
