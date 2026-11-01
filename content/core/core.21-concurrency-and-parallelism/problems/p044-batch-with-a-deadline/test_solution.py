import asyncio
import time

from solution import gather_within


def returns(value, delay):
    async def fn():
        await asyncio.sleep(delay)
        return value
    return fn


def raises(error, delay):
    async def fn():
        await asyncio.sleep(delay)
        raise error
    return fn


def slow_with_cleanup(name, log, cleanup_delay=0.02):
    async def fn():
        try:
            await asyncio.sleep(10)
            return name
        except asyncio.CancelledError:
            log.append(f"{name} cancelled")
            raise
        finally:
            await asyncio.sleep(cleanup_delay)     # e.g. closing a connection takes a moment
            log.append(f"{name} cleaned up")
    return fn


def run(coro_fns, timeout):
    async def main():
        async with asyncio.timeout(5):
            start = time.perf_counter()
            result = await gather_within(coro_fns, timeout)
            elapsed = time.perf_counter() - start
        others = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        return result, elapsed, others

    return asyncio.run(main())


def test_all_finish_in_time():
    result, _, _ = run([returns("a", 0.02), returns("b", 0.01)], timeout=1.0)
    assert result == ["a", "b"], f"Got {result}. Results go in INPUT order, not finishing order."


def test_returns_early_when_all_done():
    _, elapsed, _ = run([returns(1, 0.01), returns(2, 0.02)], timeout=3.0)
    assert elapsed < 1.0, (
        f"Took {elapsed:.2f}s although everything was done after 0.02s. Do not sleep for the "
        "whole timeout; asyncio.wait(..., timeout=...) returns as soon as all are done."
    )


def test_late_ones_are_none():
    log = []
    result, elapsed, _ = run([returns("fast", 0.01), slow_with_cleanup("slow", log)], 0.1)
    assert result == ["fast", None], f"Got {result}. Unfinished calls give None in their slot."
    assert elapsed < 0.6, f"Took {elapsed:.2f}s; the deadline was 0.1s."


def test_failures_are_returned_not_raised():
    boom = KeyError("x")
    result, _, _ = run([returns("ok", 0.01), raises(boom, 0.02)], timeout=1.0)
    assert result[0] == "ok"
    assert result[1] is boom, (
        f"Slot 1 holds {result[1]!r}. A call that failed in time gives its exception object "
        "(task.exception()), and gather_within itself must not raise."
    )


def test_late_ones_are_cancelled():
    log = []
    run([slow_with_cleanup("s1", log), slow_with_cleanup("s2", log)], timeout=0.05)
    assert "s1 cancelled" in log and "s2 cancelled" in log, (
        f"Log: {log}. The unfinished tasks must be cancelled (task.cancel()), not just ignored."
    )


def test_cleanup_finished_before_return():
    log = []
    run([returns(1, 0.01), slow_with_cleanup("slow", log)], timeout=0.05)
    assert "slow cleaned up" in log, (
        f"Log when gather_within returned: {log}. Cancelling only REQUESTS cancellation; the "
        "finally block (which awaits) has not run yet. Await the cancelled tasks, e.g. "
        "await asyncio.gather(*pending, return_exceptions=True)."
    )


def test_no_tasks_left_behind():
    log = []
    _, _, others = run([slow_with_cleanup("a", log), slow_with_cleanup("b", log)], 0.05)
    assert others == [], f"{len(others)} task(s) still alive after return. Cancel and await them."


def test_runs_concurrently():
    fns = [returns(i, 0.1) for i in range(6)]
    result, elapsed, _ = run(fns, timeout=2.0)
    assert result == list(range(6))
    assert elapsed < 0.4, (
        f"Took {elapsed:.2f}s; six 0.1s calls should overlap (about 0.1s). Create all tasks "
        "first, then wait."
    )


def test_empty_list():
    result, _, _ = run([], timeout=0.1)
    assert result == [], (
        "No calls gives []. Careful: asyncio.wait([]) raises ValueError, so handle this case."
    )


def test_mixed_order():
    log = []
    boom = ValueError("bad")
    fns = [slow_with_cleanup("s", log), returns("r", 0.01), raises(boom, 0.01), returns("q", 0.02)]
    result, _, _ = run(fns, timeout=0.1)
    assert result == [None, "r", boom, "q"], f"Got {result}; expected [None, 'r', boom, 'q']."
