import pytest

from solution import Retry


class Flaky:
    """Fails `n` times with `error`, then returns 'done'."""

    def __init__(self, n, error=ValueError):
        self.n = n
        self.error = error
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.n:
            raise self.error(f"failure {self.calls}")
        return "done"


def test_success_on_first_try():
    f = Flaky(0)
    assert Retry(times=3)(f)() == "done", "A function that works is called once and its result returned."
    assert f.calls == 1, "Do not call the function again after a success."


def test_retries_until_success():
    f = Flaky(2)
    r = Retry(times=3)
    assert r(f)() == "done", "Two failures and then a success, with 3 attempts allowed: the result must be returned."
    assert f.calls == 3, "The function should have been called 3 times in total."
    assert r.failures == 2, "failures counts every caught exception (here 2)."


def test_gives_up_and_reraises_the_last_exception():
    f = Flaky(10)
    r = Retry(times=3)
    with pytest.raises(ValueError) as info:
        r(f)()
    assert str(info.value) == "failure 3", "After the last attempt fails, re-raise THAT exception (the third one)."
    assert f.calls == 3, "times=3 means 3 attempts in total, not 3 retries after the first try."
    assert r.failures == 3, "All 3 failures are counted, including the last one."


def test_only_listed_exceptions_are_retried():
    f = Flaky(1, error=KeyError)
    r = Retry(times=5, exceptions=(ValueError, OSError))
    with pytest.raises(KeyError):
        r(f)()
    assert f.calls == 1, "A KeyError is not in `exceptions`: it must propagate at once, with no retry."
    assert r.failures == 0, "Only the listed exceptions count as failures."


def test_arguments_and_decorator_syntax():
    state = {"n": 0}

    @Retry(times=2, exceptions=(RuntimeError,))
    def divide(a, b=1):
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("first time")
        return a / b

    assert divide(10, b=4) == 2.5, "Forward *args and **kwargs, return the result."
    assert state["n"] == 2, "The first call failed, the second succeeded."


def test_wrapper_keeps_metadata():
    @Retry()
    def documented():
        """Docstring."""

    assert documented.__name__ == "documented" and documented.__doc__ == "Docstring.", "Use functools.wraps(func) on the wrapper."


def test_times_validation():
    for bad in (0, -1):
        with pytest.raises(ValueError):
            Retry(times=bad)
    assert Retry(times=1).times == 1, "times=1 is allowed: one attempt, no retry."


def test_times_one_means_no_retry():
    f = Flaky(1)
    with pytest.raises(ValueError):
        Retry(times=1)(f)()
    assert f.calls == 1, "times=1: exactly one attempt."


def test_one_retry_object_can_decorate_two_functions():
    r = Retry(times=2)
    a, b = Flaky(1), Flaky(1)
    assert r(a)() == "done" and r(b)() == "done", "The same Retry object can decorate several functions."
    assert r.failures == 2, "The failure counter belongs to the Retry object and adds up across the functions it decorates."
