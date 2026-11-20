import pytest

from solution import CircuitBreaker, CircuitOpen


class Service:
    def __init__(self):
        self.calls = 0
        self.fail = True

    def __call__(self, x=0):
        self.calls += 1
        if self.fail:
            raise ValueError("down")
        return x + 1


def make(threshold=3, cooldown=10):
    t = [0.0]
    return CircuitBreaker(threshold, cooldown, lambda: t[0]), t, Service()


def fail_n(cb, svc, n):
    for _ in range(n):
        with pytest.raises(ValueError):
            cb.call(svc)


def test_starts_closed_and_passes_results_and_arguments():
    cb, t, svc = make()
    svc.fail = False
    assert cb.state == "closed"
    assert cb.call(svc, 41) == 42
    assert cb.call(svc, x=1) == 2


def test_failures_below_the_threshold_keep_it_closed_and_reraise():
    cb, t, svc = make(threshold=3)
    fail_n(cb, svc, 2)
    assert cb.state == "closed", "Two failures of three: still closed. The original exception is re-raised."


def test_opens_after_threshold_failures_in_a_row():
    cb, t, svc = make(threshold=3)
    fail_n(cb, svc, 3)
    assert cb.state == "open", "The third failure in a row opens the breaker."


def test_a_success_resets_the_count():
    cb, t, svc = make(threshold=3)
    fail_n(cb, svc, 2)
    svc.fail = False
    cb.call(svc)
    svc.fail = True
    fail_n(cb, svc, 2)
    assert cb.state == "closed", "Failures must be IN A ROW: the success in between reset the count."
    fail_n(cb, svc, 1)
    assert cb.state == "open"


def test_open_fails_fast_without_calling():
    cb, t, svc = make(threshold=2, cooldown=10)
    fail_n(cb, svc, 2)
    before = svc.calls
    t[0] = 5
    with pytest.raises(CircuitOpen):
        cb.call(svc)
    assert svc.calls == before, "While open, the function must not be called at all."
    assert cb.state == "open"


def test_half_open_after_the_cooldown():
    cb, t, svc = make(threshold=2, cooldown=10)
    fail_n(cb, svc, 2)
    t[0] = 9.99
    assert cb.state == "open"
    t[0] = 10
    assert cb.state == "half-open", "At exactly 'cooldown' seconds the breaker is half-open (state is computed from the clock)."


def test_successful_trial_closes():
    cb, t, svc = make(threshold=2, cooldown=10)
    fail_n(cb, svc, 2)
    t[0] = 10
    svc.fail = False
    assert cb.call(svc, 1) == 2
    assert cb.state == "closed"
    fail_n_ok = cb.call(svc, 5)
    assert fail_n_ok == 6
    svc.fail = True
    fail_n(cb, svc, 1)
    assert cb.state == "closed", "After closing, the failure count starts again from 0."


def test_failed_trial_reopens_and_restarts_the_cooldown():
    cb, t, svc = make(threshold=2, cooldown=10)
    fail_n(cb, svc, 2)
    t[0] = 10
    calls = svc.calls
    with pytest.raises(ValueError):
        cb.call(svc)
    assert svc.calls == calls + 1, "The trial runs the function once."
    assert cb.state == "open"
    t[0] = 19.9
    with pytest.raises(CircuitOpen):
        cb.call(svc)
    t[0] = 20
    assert cb.state == "half-open", "The cooldown restarts at the time of the failed trial (10 + 10)."


def test_circuit_open_is_an_exception_but_not_the_service_error():
    cb, t, svc = make(threshold=1)
    fail_n(cb, svc, 1)
    assert issubclass(CircuitOpen, Exception) and not issubclass(CircuitOpen, ValueError)
    with pytest.raises(CircuitOpen):
        cb.call(svc)
