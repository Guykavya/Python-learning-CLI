import asyncio
import time

import pytest

from solution import load_all


def make_loader(name, delay, log, fail=None):
    async def loader():
        try:
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            log.append(f"{name} cancelled")
            raise
        if fail is not None:
            log.append(f"{name} failed")
            raise fail
        log.append(f"{name} ok")
        return name.upper()
    return loader


def test_all_succeed_in_order():
    log = []
    loaders = [make_loader("a", 0.1, log), make_loader("b", 0.01, log), make_loader("c", 0.05, log)]
    result = asyncio.run(load_all(loaders))
    assert result == ["A", "B", "C"], (
        f"Got {result}. Return results in the order of loaders, not in finishing order."
    )


def test_runs_concurrently():
    log = []
    loaders = [make_loader(f"x{i}", 0.2, log) for i in range(5)]
    start = time.perf_counter()
    asyncio.run(load_all(loaders))
    elapsed = time.perf_counter() - start
    assert elapsed < 0.6, (
        f"5 loaders of 0.2 s took {elapsed:.2f} s. Start them all as tasks before waiting."
    )


def test_failure_raises_exception_group():
    log = []
    loaders = [make_loader("ok", 0.05, log), make_loader("bad", 0.01, log, fail=ValueError("bad data"))]
    with pytest.raises(ExceptionGroup) as info:
        asyncio.run(load_all(loaders))
    errors = info.value.exceptions
    assert len(errors) == 1 and isinstance(errors[0], ValueError), (
        f"The group held {errors!r}; it should hold exactly the one ValueError."
    )


def test_siblings_are_cancelled_before_the_error_arrives():
    log = []
    caught = []

    async def main():
        loaders = [
            make_loader("slow1", 2.0, log),
            make_loader("bad", 0.05, log, fail=ConnectionError("down")),
            make_loader("slow2", 2.0, log),
        ]
        start = time.perf_counter()
        try:
            await load_all(loaders)
        except* ConnectionError as eg:
            caught.append(eg)
        elapsed = time.perf_counter() - start
        return elapsed, list(log)  # snapshot BEFORE asyncio.run cleans up

    elapsed, snapshot = asyncio.run(main())
    assert caught, (
        "except* ConnectionError caught nothing. Let the TaskGroup's ExceptionGroup propagate; "
        "do not catch it inside load_all."
    )
    assert "slow1 cancelled" in snapshot and "slow2 cancelled" in snapshot, (
        f"When the error reached the caller, the log was {snapshot}. The slow loaders were still "
        "running. A TaskGroup cancels the other tasks and waits for them before raising; "
        "gather does not."
    )
    assert elapsed < 0.6, (
        f"The call took {elapsed:.2f} s; the failure happened at 0.05 s. Siblings must be "
        "cancelled, not waited for."
    )


def test_two_failures_both_reported():
    log = []
    loaders = [
        make_loader("bad1", 0.05, log, fail=KeyError("k")),
        make_loader("bad2", 0.05, log, fail=TypeError("t")),
    ]
    with pytest.raises(ExceptionGroup) as info:
        asyncio.run(load_all(loaders))
    kinds = sorted(type(e).__name__ for e in info.value.exceptions)
    assert kinds == ["KeyError", "TypeError"], (
        f"The group held {kinds}. Two tasks failing at the same moment are both reported."
    )


def test_empty():
    assert asyncio.run(load_all([])) == [], "No loaders: return []."
