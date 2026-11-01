import time

import pytest

from solution import first_success


def mirror(value, seconds, fail=False):
    def run():
        time.sleep(seconds)
        if fail:
            raise ConnectionError(f"{value} is down")
        return value
    return run


def test_fastest_success_wins():
    start = time.perf_counter()
    result = first_success([mirror("slow", 1.0), mirror("fast", 0.1)], timeout=5)
    elapsed = time.perf_counter() - start
    assert result == "fast", (
        f"Got {result!r}. The FIRST TO FINISH must win, not the first in the list. "
        "Start all functions at once and wait with return_when=FIRST_COMPLETED."
    )
    assert elapsed < 0.6, (
        f"Took {elapsed:.2f} s; the fast mirror answered after 0.1 s. Do not wait for the slow "
        "one: a 'with ThreadPoolExecutor()' block waits for every job when it ends. Use "
        "pool.shutdown(wait=False, cancel_futures=True) instead."
    )


def test_failures_are_skipped():
    funcs = [mirror("A", 0.6), mirror("B", 0.05, fail=True), mirror("C", 0.2)]
    result = first_success(funcs, timeout=5)
    assert result == "C", (
        f"Got {result!r}. B failed first; a failure is not a success. Remember the error and "
        "keep waiting for the futures that are still pending."
    )


def test_result_is_a_value_not_an_exception():
    result = first_success([mirror("B", 0.02, fail=True), mirror("C", 0.1)], timeout=5)
    assert not isinstance(result, BaseException), (
        "You returned an exception object. Check fut.exception() before using the result."
    )
    assert result == "C"


def test_all_fail_raises_runtime_error_with_count():
    funcs = [mirror("A", 0.05, fail=True), mirror("B", 0.1, fail=True), mirror("C", 0.02, fail=True)]
    with pytest.raises(RuntimeError) as info:
        first_success(funcs, timeout=5)
    assert "3" in str(info.value), (
        f"The message was {str(info.value)!r}. Say how many functions failed, e.g. "
        "'all 3 functions failed'."
    )
    assert isinstance(info.value.__cause__, ConnectionError), (
        "Chain the last real error: raise RuntimeError(...) from last_error, so the traceback "
        "shows what actually went wrong."
    )


def test_timeout_raises_timeout_error_quickly():
    start = time.perf_counter()
    with pytest.raises(TimeoutError):
        first_success([mirror("A", 0.8), mirror("B", 0.8)], timeout=0.15)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5, (
        f"The timeout was 0.15 s but the call took {elapsed:.2f} s. Pass the time LEFT to "
        "wait(..., timeout=...) and do not wait for the pool when you give up."
    )


def test_timeout_is_total_not_per_wait():
    # One failure at 0.1 s restarts nothing: the deadline is 0.3 s from the call.
    funcs = [mirror("A", 0.1, fail=True), mirror("B", 0.2, fail=True), mirror("C", 1.0)]
    start = time.perf_counter()
    with pytest.raises(TimeoutError):
        first_success(funcs, timeout=0.3)
    elapsed = time.perf_counter() - start
    assert elapsed < 0.6, (
        f"Took {elapsed:.2f} s. If you pass the full timeout to every wait() call, each "
        "failure restarts the clock. Compute a deadline once and pass deadline - now."
    )


def test_single_function():
    assert first_success([mirror(42, 0.01)], timeout=1) == 42, "One working function: return its value."


def test_empty_list_raises_value_error():
    with pytest.raises(ValueError):
        first_success([], timeout=1)
