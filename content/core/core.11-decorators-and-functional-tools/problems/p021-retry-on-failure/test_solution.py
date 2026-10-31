import pytest

from solution import retry


def flaky(failures, exc=ConnectionError):
    """A function that fails `failures` times, then works. state["calls"] counts the calls."""
    state = {"calls": 0}

    def fetch(url, timeout=1):
        """Fetch a page."""
        state["calls"] += 1
        if state["calls"] <= failures:
            raise exc(f"fail {state['calls']}")
        return f"page {url} {timeout}"
    return fetch, state


def test_success_first_time():
    waits = []
    fetch, state = flaky(0)
    fetch = retry(3, sleep=waits.append)(fetch)
    assert fetch("a") == "page a 1", "Return the function's result when it works."
    assert state["calls"] == 1, "A call that works must not be repeated."
    assert waits == [], "No failure means no sleep."


def test_success_after_failures():
    waits = []
    fetch, state = flaky(2)
    fetch = retry(3, exceptions=ConnectionError, delay=0.5, sleep=waits.append)(fetch)
    assert fetch("x.org") == "page x.org 1", "After two failures the third call works: return its result."
    assert state["calls"] == 3, "Two failures plus one success is three calls."
    assert waits == [0.5, 0.5], "Sleep `delay` once after each failure that will be retried."


def test_gives_up_and_reraises_last():
    waits = []
    fetch, state = flaky(10)
    fetch = retry(3, exceptions=(ConnectionError,), delay=2, sleep=waits.append)(fetch)
    with pytest.raises(ConnectionError) as info:
        fetch("x")
    assert str(info.value) == "fail 3", "Re-raise the LAST exception (from the third call), with a bare `raise`."
    assert state["calls"] == 3, "attempts=3 means three calls in total, not three retries after the first call."
    assert waits == [2, 2], "Do not sleep after the last attempt: there is nothing left to wait for."


def test_other_exceptions_are_not_retried():
    waits = []
    fetch, state = flaky(1, exc=ValueError)
    fetch = retry(5, exceptions=ConnectionError, delay=1, sleep=waits.append)(fetch)
    with pytest.raises(ValueError):
        fetch("x")
    assert state["calls"] == 1, "A ValueError does not match exceptions=ConnectionError: raise it at once."
    assert waits == [], "No sleep for an exception you do not retry."


def test_subclass_matches():
    waits = []
    fetch, state = flaky(1, exc=ConnectionResetError)
    fetch = retry(2, exceptions=ConnectionError, sleep=waits.append)(fetch)
    assert fetch("x") == "page x 1", "ConnectionResetError is a kind of ConnectionError, so it is retried (an except clause matches subclasses)."
    assert waits == [0.0], "The default delay is 0.0."


def test_one_attempt_means_no_retry():
    waits = []
    fetch, state = flaky(1)
    fetch = retry(1, sleep=waits.append)(fetch)
    with pytest.raises(ConnectionError):
        fetch("x")
    assert state["calls"] == 1 and waits == [], "attempts=1 calls once and never sleeps."


def test_bad_attempts():
    with pytest.raises(ValueError):
        retry(0)
    with pytest.raises(ValueError):
        retry(-2)


def test_arguments_and_metadata():
    waits = []
    fetch, state = flaky(1)
    wrapped = retry(2, sleep=waits.append)(fetch)
    assert wrapped("y", timeout=9) == "page y 9", "Pass keyword arguments through with **kwargs."
    assert wrapped.__name__ == "fetch", "Use functools.wraps so the name is kept."
    assert wrapped.__doc__ == "Fetch a page.", "Use functools.wraps so the docstring is kept."
