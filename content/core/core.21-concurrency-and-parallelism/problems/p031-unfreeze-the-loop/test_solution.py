import asyncio
import threading
import time

import pytest

from solution import handle_all


def blocking_lookup(r):
    time.sleep(0.2)
    return f"result-{r}"


def run_with_heartbeat(requests, lookup):
    """Run handle_all next to a heartbeat task; return (result, ticks, elapsed)."""

    async def main():
        ticks = 0

        async def heartbeat():
            nonlocal ticks
            while True:
                await asyncio.sleep(0.02)
                ticks += 1

        hb = asyncio.create_task(heartbeat())
        await asyncio.sleep(0)
        start = time.perf_counter()
        try:
            result = await handle_all(requests, lookup)
        finally:
            elapsed = time.perf_counter() - start
            hb.cancel()
        return result, ticks, elapsed

    return asyncio.run(main())


def test_results_in_order():
    def lookup(r):
        time.sleep(0.01 * (5 - r))
        return r * r
    result, _, _ = run_with_heartbeat([1, 2, 3, 4], lookup)
    assert result == [1, 4, 9, 16], f"Got {result}. Keep the order of requests."


def test_loop_keeps_running():
    _, ticks, _ = run_with_heartbeat(list(range(5)), blocking_lookup)
    assert ticks >= 4, (
        f"The heartbeat ticked only {ticks} time(s) during the lookups (expected about 9 or 10). "
        "slow_lookup blocks the loop's thread. Run it with asyncio.to_thread so the loop stays free."
    )


def test_lookups_run_concurrently():
    _, _, elapsed = run_with_heartbeat(list(range(5)), blocking_lookup)
    assert elapsed < 0.6, (
        f"5 lookups of 0.2 s took {elapsed:.2f} s (one by one is 1.0 s). Start all to_thread "
        "calls and gather them, instead of awaiting each one in a loop."
    )


def test_lookups_run_in_other_threads():
    seen = []

    def lookup(r):
        seen.append(threading.current_thread() is threading.main_thread())
        return r

    run_with_heartbeat([1, 2, 3], lookup)
    assert seen and not any(seen), (
        "slow_lookup ran in the main thread, the event loop's thread. Offload it with "
        "asyncio.to_thread(slow_lookup, r)."
    )


def test_error_propagates():
    def lookup(r):
        time.sleep(0.01)
        if r == "bad":
            raise LookupError("no such record")
        return r

    try:
        run_with_heartbeat(["ok", "bad"], lookup)
    except LookupError as e:
        assert "no such record" in str(e), "Re-raise the lookup's own exception, not a new one."
    except ExceptionGroup:
        pytest.fail(
            "The LookupError came back wrapped in an ExceptionGroup: that is what TaskGroup does. "
            "This problem wants the original exception, so use asyncio.gather (which re-raises "
            "the first error as it is)."
        )
    else:
        pytest.fail("A lookup raised LookupError, but run_with_heartbeat returned normally. "
                    "Do not catch the error; let it propagate.")


def test_empty():
    result, _, _ = run_with_heartbeat([], blocking_lookup)
    assert result == [], "No requests: return []."
