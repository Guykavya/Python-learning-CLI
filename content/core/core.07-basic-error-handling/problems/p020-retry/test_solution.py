from solution import retry


def expect_raise(exc_type, func, *args, match=None, why=""):
    """Call func(*args). It must raise exc_type, with match in its message if match is given."""
    try:
        result = func(*args)
    except exc_type as e:
        if match is not None:
            assert match in str(e), (
                f"The {exc_type.__name__} message should contain {match!r}, but it was {str(e)!r}. {why}")
        return e
    except Exception as e:
        raise AssertionError(
            f"Expected {exc_type.__name__}, but {type(e).__name__} was raised: {e}. {why}") from e
    raise AssertionError(f"Expected {exc_type.__name__}, but the call returned {result!r}. {why}")


def failing_times(n, exc_type=ValueError, result="data"):
    """A function that raises exc_type on its first n calls, then returns result. Also returns the call log."""
    calls = []

    def func():
        calls.append(len(calls) + 1)
        if len(calls) <= n:
            raise exc_type(f"attempt {len(calls)} failed")
        return result

    return func, calls


def test_success_first_time():
    func, calls = failing_times(0)
    assert retry(func) == "data"
    assert calls == [1], "Stop calling as soon as one call succeeds."


def test_success_after_failures():
    func, calls = failing_times(2)
    assert retry(func) == "data", "Two ValueErrors then success: return the result of the third call."
    assert calls == [1, 2, 3]


def test_all_attempts_fail_raises_last_error():
    func, calls = failing_times(10)
    err = expect_raise(ValueError, retry, func, 4,
                       why="When every attempt fails, raise the last exception.")
    assert calls == [1, 2, 3, 4], f"Called {len(calls)} times; with attempts=4 call exactly 4 times."
    assert str(err) == "attempt 4 failed", (
        f"Got {str(err)!r}. Raise the exception from the LAST attempt, not the first or a new one.")


def test_other_errors_propagate_immediately():
    func, calls = failing_times(5, exc_type=KeyError)
    expect_raise(KeyError, retry, func, why="KeyError is not in errors: let it propagate.")
    assert calls == [1], "An exception not in `errors` must not be retried."


def test_custom_errors_tuple():
    func, calls = failing_times(1, exc_type=ZeroDivisionError)
    assert retry(func, 3, (ZeroDivisionError, ValueError)) == "data", "Retry every type listed in errors."
    func, calls = failing_times(1, exc_type=ValueError)
    expect_raise(ValueError, retry, func, 3, (ZeroDivisionError,),
                 why="With errors=(ZeroDivisionError,), a ValueError is NOT retried.")
    assert calls == [1]


def test_attempts_validated():
    func, calls = failing_times(0)
    expect_raise(ValueError, retry, func, 0, match="attempts must be at least 1")
    assert calls == [], "Check attempts before calling func."


def test_single_attempt():
    func, calls = failing_times(1)
    expect_raise(ValueError, retry, func, 1, match="attempt 1 failed")
