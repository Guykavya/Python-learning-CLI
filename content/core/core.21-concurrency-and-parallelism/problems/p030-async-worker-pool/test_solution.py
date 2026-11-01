import asyncio
import time

from solution import process


def make_worker(fail_on=()):
    stats = {"running": 0, "peak": 0, "calls": 0}

    async def worker(n):
        stats["calls"] += 1
        stats["running"] += 1
        stats["peak"] = max(stats["peak"], stats["running"])
        try:
            await asyncio.sleep(0.01 * (n % 7 + 1))
        finally:
            stats["running"] -= 1
        if n in fail_on:
            raise ValueError(f"bad {n}")
        return n * 10

    return worker, stats


def run(coro):
    async def guarded():
        try:
            async with asyncio.timeout(3):
                return await coro
        except TimeoutError:
            raise AssertionError(
                "process() did not finish within 3 s. queue.join() is waiting for a task_done() "
                "that never came (call it in a finally), or a worker died on an exception."
            ) from None
    return asyncio.run(guarded())


def test_results_in_input_order():
    worker, _ = make_worker()
    results, errors = run(process([5, 1, 3, 2, 6, 0], worker, 3))
    assert results == [50, 10, 30, 20, 60, 0], (
        f"Got {results}. Store each result at its item's index (queue (index, item) pairs); "
        "appending gives finishing order."
    )
    assert errors == [], f"Nothing failed, but errors was {errors}."


def test_peak_is_exactly_n_workers():
    worker, stats = make_worker()
    run(process(list(range(20)), worker, 4))
    assert stats["peak"] == 4, (
        f"Peak concurrency was {stats['peak']}, expected 4. Start exactly n_workers worker tasks, "
        "each processing one item at a time."
    )
    assert stats["calls"] == 20, f"worker was called {stats['calls']} times for 20 items."


def test_errors_are_collected_and_workers_survive():
    worker, stats = make_worker(fail_on={3, 8})
    results, errors = run(process([3, 1, 8, 2, 4], worker, 2))
    assert results == [None, 10, None, 20, 40], (
        f"Got {results}. Failed items get None; the other items must still be processed. "
        "Catch the exception inside the worker loop so the worker keeps going."
    )
    assert [i for i, _ in errors] == [0, 2], (
        f"errors had indexes {[i for i, _ in errors]}; expected [0, 2], sorted by index."
    )
    assert all(isinstance(e, ValueError) for _, e in errors), "Store the exception objects themselves."


def test_no_tasks_left_running():
    worker, _ = make_worker()

    async def main():
        await process(list(range(6)), worker, 3)
        await asyncio.sleep(0)
        others = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        return others

    leftovers = run(main())
    assert leftovers == [], (
        f"{len(leftovers)} task(s) were still alive after process returned. Cancel the workers "
        "after queue.join() and await them (gather(..., return_exceptions=True))."
    )


def test_join_waits_for_failures_too():
    worker, _ = make_worker(fail_on={0, 1, 2})
    results, errors = run(process([0, 1, 2], worker, 3))
    assert results == [None, None, None] and len(errors) == 3, (
        "If task_done() is skipped when worker raises, queue.join() never returns. "
        "Call task_done() in a finally block."
    )


def test_more_workers_than_items():
    worker, stats = make_worker()
    results, _ = run(process([1, 2], worker, 5))
    assert results == [10, 20], "Extra workers just wait and are cancelled at the end."


def test_empty():
    worker, _ = make_worker()
    assert run(process([], worker, 3)) == ([], []), "No items: ([], [])."


def test_faster_than_sequential():
    async def slow(n):
        await asyncio.sleep(0.1)
        return n

    start = time.perf_counter()
    results, _ = run(process(list(range(8)), slow, 4))
    elapsed = time.perf_counter() - start
    assert results == list(range(8))
    assert elapsed < 0.45, (
        f"8 items of 0.1 s with 4 workers took {elapsed:.2f} s (sequential is 0.8 s)."
    )
