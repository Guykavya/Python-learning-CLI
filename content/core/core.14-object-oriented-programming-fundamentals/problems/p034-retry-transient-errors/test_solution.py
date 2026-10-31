import pytest

from solution import PermanentError, RetryExhausted, TransientError, retry, retrying


class Flaky:
    """Raises the given errors one by one, then returns 'ok'. Counts calls."""

    def __init__(self, *errors):
        self.errors = list(errors)
        self.raised = []
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.errors:
            err = self.errors.pop(0)
            self.raised.append(err)
            raise err
        return "ok"


class Timeout(TransientError):
    pass


def test_success_first_time():
    f = Flaky()
    assert retry(f) == "ok", "Return the function's result."
    assert f.calls == 1, "A function that works the first time is called once."


def test_retries_transient_then_succeeds():
    f = Flaky(TransientError("t1"), TransientError("t2"))
    assert retry(f, attempts=3) == "ok", "Two transient failures, then success on the 3rd attempt."
    assert f.calls == 3, "Call again after each TransientError."


def test_subclass_of_transient_is_retried():
    f = Flaky(Timeout("slow"))
    assert retry(f, attempts=2) == "ok", "Catch TransientError, so its subclasses (like Timeout) are retried too."


def test_permanent_error_not_retried():
    f = Flaky(PermanentError("wrong password"))
    try:
        retry(f, attempts=5)
    except PermanentError as e:
        assert str(e) == "wrong password", "Let the PermanentError propagate unchanged."
    else:
        pytest.fail("The PermanentError did not reach the caller: it was retried. Catch only TransientError.")
    assert f.calls == 1, "A PermanentError must not be retried: call the function only once."


def test_other_errors_propagate_unchanged():
    err = KeyError("x")
    f = Flaky(err)
    try:
        retry(f, attempts=5)
    except KeyError as e:
        caught = e
    else:
        pytest.fail("The KeyError did not reach the caller: it was retried. Catch only TransientError.")
    assert caught is err, "Do not wrap or replace other exceptions; let them propagate as they are."
    assert f.calls == 1, "Only TransientError is retried."


def test_permanent_after_transient():
    f = Flaky(TransientError("t"), PermanentError("p"))
    with pytest.raises(PermanentError):
        retry(f, attempts=5)
    assert f.calls == 2, "Retry the transient error, then stop at the permanent one."


def test_exhausted():
    f = Flaky(TransientError("a"), TransientError("b"), TransientError("c"))
    with pytest.raises(RetryExhausted) as info:
        retry(f, attempts=2)
    assert f.calls == 2, "attempts=2 means at most 2 calls in total, not 1 call plus 2 retries."
    err = info.value
    assert str(err) == "gave up after 2 attempts", "The message is 'gave up after {attempts} attempts'."
    assert err.attempts == 2, "Store attempts on the exception."
    assert err.last_error is f.raised[-1], "last_error is the exception from the LAST attempt."
    assert err.__cause__ is f.raised[-1], (
        "Chain it: raise RetryExhausted(attempts, err) from err, so __cause__ is the last TransientError."
    )


def test_one_attempt():
    f = Flaky(TransientError("x"))
    with pytest.raises(RetryExhausted):
        retry(f, attempts=1)
    assert f.calls == 1, "attempts=1 means try once, no retries."


def test_bad_attempts():
    for bad in (0, -1, 2.5, "3"):
        f = Flaky()
        with pytest.raises(ValueError):
            retry(f, attempts=bad)
        assert f.calls == 0, "Check attempts before calling the function."


def test_on_retry_called_between_attempts():
    seen = []
    f = Flaky(TransientError("t1"), Timeout("t2"))
    assert retry(f, attempts=5, on_retry=lambda n, e: seen.append((n, str(e)))) == "ok"
    assert seen == [(1, "t1"), (2, "t2")], "on_retry(number, err) runs after each failed attempt that will be retried."


def test_on_retry_not_called_after_last():
    seen = []
    f = Flaky(TransientError("a"), TransientError("b"))
    with pytest.raises(RetryExhausted):
        retry(f, attempts=2, on_retry=lambda n, e: seen.append(n))
    assert seen == [1], "on_retry is not called after the last attempt: nothing is retried then."


def test_retrying_decorator():
    calls = []

    @retrying(4)
    def add(a, b):
        calls.append((a, b))
        if len(calls) < 3:
            raise TransientError("busy")
        return a + b

    assert add(2, b=3) == 5, "The decorated function passes *args and **kwargs through and retries."
    assert len(calls) == 3, "Two transient failures, then success."
    assert add.__name__ == "add", "Use functools.wraps(func) so the wrapper keeps the name 'add'."


def test_retrying_gives_up():
    @retrying(2)
    def down():
        raise TransientError("down")

    with pytest.raises(RetryExhausted, match="2 attempts"):
        down()


def test_retrying_each_call_starts_fresh():
    count = {"n": 0}

    @retrying(2)
    def flaky():
        count["n"] += 1
        if count["n"] % 2 == 1:
            raise TransientError("odd call")
        return count["n"]

    assert flaky() == 2, "First call: fails once, works on the 2nd try."
    assert flaky() == 4, "Each call of the decorated function gets its own full set of attempts."
