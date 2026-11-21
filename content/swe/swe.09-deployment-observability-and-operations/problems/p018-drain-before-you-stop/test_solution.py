import sys
import threading

import pytest

from solution import Lifecycle


class FakeTime:
    """A clock and a sleep that move together; `on_tick` lets a test finish requests at chosen moments."""

    def __init__(self):
        self.now, self.sleeps, self.on_tick = 0.0, [], None

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        if self.on_tick:
            self.on_tick(self.now)


@pytest.fixture
def ft():
    return FakeTime()


@pytest.fixture
def lc(ft):
    return Lifecycle(clock=ft.clock, sleep=ft.sleep)


def test_starts_ready_and_idle(lc):
    assert (lc.draining, lc.in_flight) == (False, 0)
    assert lc.readiness() == (200, {"status": "ready"})


def test_track_counts_requests(lc):
    with lc.track():
        assert lc.in_flight == 1, "Inside the with block one request is in flight."
        with lc.track():
            assert lc.in_flight == 2
    assert lc.in_flight == 0, "After the blocks end nothing is in flight."


def test_track_counts_out_even_when_the_request_fails(lc):
    with pytest.raises(RuntimeError):
        with lc.track():
            raise RuntimeError("simulated bug")
    assert lc.in_flight == 0, "A failed request is no longer in flight: decrement in a finally."


def test_sigterm_turns_readiness_red_and_is_idempotent(lc):
    lc.on_sigterm()
    lc.on_sigterm()
    assert lc.draining is True
    assert lc.readiness() == (503, {"status": "not ready", "problems": {"draining": "shutting down"}}), \
        "While draining, readiness is 503 with the problem 'draining'."


def test_requests_arriving_while_draining_are_still_served(lc):
    lc.on_sigterm()
    with lc.track():
        assert lc.in_flight == 1, "track() must not refuse during draining: the load balancer needs a moment to stop sending traffic."


def test_wait_idle_returns_at_once_when_idle(lc, ft):
    assert lc.wait_idle(5) is True
    assert ft.sleeps == [], "Nothing in flight: return True without sleeping."


def test_wait_idle_waits_for_the_last_request(lc, ft):
    request = lc.track()
    request.__enter__()                                         # a request that is still running

    def finish_at_one_second(now):
        if now >= 1.0 and lc.in_flight:
            request.__exit__(None, None, None)

    ft.on_tick = finish_at_one_second
    assert lc.wait_idle(5, poll=0.5) is True, "The request ends at t=1: wait_idle must notice and return True."
    assert ft.sleeps == [0.5, 0.5], f"Poll every 0.5 s: two sleeps until t=1.0; got {ft.sleeps}"
    assert lc.in_flight == 0


def test_wait_idle_times_out(lc, ft):
    request = lc.track()
    request.__enter__()                                         # never finishes
    assert lc.wait_idle(2, poll=0.5) is False, "A request still running after the timeout: return False."
    assert ft.now == pytest.approx(2.0), f"Wait the whole timeout and not more; the fake clock ended at {ft.now}"
    assert sum(ft.sleeps) == pytest.approx(2.0)


def test_last_sleep_is_shortened_to_the_remaining_time(lc, ft):
    request = lc.track()
    request.__enter__()
    assert lc.wait_idle(1.0, poll=0.4) is False
    assert ft.sleeps == pytest.approx([0.4, 0.4, 0.2]), f"The last sleep is min(poll, remaining) = 0.2, so the total is exactly the timeout; got {ft.sleeps}"


def test_timeout_zero(lc, ft):
    request = lc.track()
    request.__enter__()
    assert lc.wait_idle(0) is False and ft.sleeps == [], "With timeout 0 and a request running: False at once."


def test_tracking_is_thread_safe(lc):
    previous = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)                                 # switch threads very often to expose a race
    try:
        def worker():
            for _ in range(2000):
                with lc.track():
                    pass

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
    finally:
        sys.setswitchinterval(previous)
    assert lc.in_flight == 0, f"After 16,000 balanced enter/exit pairs from 8 threads the count must be 0; got {lc.in_flight}. Protect the counter with a Lock."
