import asyncio
import time

import pytest

from solution import with_timeout


def make(value, delay, log=None):
    async def fn():
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            if log is not None:
                log.append("cancelled")
            raise
        return value
    return fn


def test_fast_call_returns_its_value():
    assert asyncio.run(with_timeout(make(21, 0.01), 0.5, "n/a")) == 21, (
        "A call that finishes in time must return its own result."
    )


def test_slow_call_returns_default_quickly():
    start = time.perf_counter()
    result = asyncio.run(with_timeout(make(99, 1.0), 0.1, "n/a"))
    elapsed = time.perf_counter() - start
    assert result == "n/a", (
        f"Got {result!r}. When the time runs out, return default. Use async with asyncio.timeout(...)."
    )
    assert elapsed < 0.5, (
        f"Took {elapsed:.2f} s with a 0.1 s timeout. The slow call was waited for instead of cancelled."
    )


def test_slow_call_is_cancelled():
    log = []
    asyncio.run(with_timeout(make(99, 1.0, log), 0.05, None))
    assert log == ["cancelled"], (
        f"The slow coroutine's log was {log}. asyncio.timeout must CANCEL it; do not start it "
        "as a separate task that keeps running after you return the default."
    )


def test_falsy_results_are_not_replaced():
    for value in (0, None, "", []):
        result = asyncio.run(with_timeout(make(value, 0.01), 0.5, "DEFAULT"))
        assert result == value, (
            f"The call returned {value!r} in time, but you gave {result!r}. Only a timeout "
            "means default; do not write 'result or default'."
        )


def test_other_errors_propagate():
    async def broken():
        await asyncio.sleep(0.01)
        raise ValueError("bad reading")

    with pytest.raises(ValueError, match="bad reading"):
        asyncio.run(with_timeout(broken, 0.5, "n/a"))


def test_default_can_be_anything():
    sentinel = object()
    assert asyncio.run(with_timeout(make(1, 0.5), 0.02, sentinel)) is sentinel, (
        "Return the default object itself."
    )
