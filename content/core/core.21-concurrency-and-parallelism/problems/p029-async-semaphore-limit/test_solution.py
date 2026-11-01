import asyncio
import time

import pytest

from solution import run_limited


def make_jobs(delays):
    stats = {"running": 0, "peak": 0, "started": 0}

    def job(i, delay):
        async def run():
            stats["started"] += 1
            stats["running"] += 1
            stats["peak"] = max(stats["peak"], stats["running"])
            try:
                await asyncio.sleep(delay)
            finally:
                stats["running"] -= 1
            return i
        return run

    return [job(i, d) for i, d in enumerate(delays)], stats


async def guarded(coro):
    async with asyncio.timeout(5):
        return await coro


def test_peak_equals_limit():
    jobs, stats = make_jobs([0.05] * 10)
    asyncio.run(guarded(run_limited(jobs, 3)))
    assert stats["peak"] == 3, (
        f"Up to {stats['peak']} jobs ran at the same time; the limit was 3. Every job must "
        "hold the semaphore (async with sem:) while it runs."
    )
    assert stats["started"] == 10, f"Only {stats['started']} of 10 jobs ran."


def test_results_in_input_order():
    jobs, _ = make_jobs([0.08, 0.01, 0.05, 0.02, 0.03])
    result = asyncio.run(guarded(run_limited(jobs, 2)))
    assert result == [0, 1, 2, 3, 4], (
        f"Got {result}. Results must be in the order of coro_fns, not finishing order."
    )


def test_limit_one_is_sequential():
    jobs, stats = make_jobs([0.02] * 4)
    asyncio.run(guarded(run_limited(jobs, 1)))
    assert stats["peak"] == 1, f"With limit=1 only one job may run at a time; peak was {stats['peak']}."


def test_slots_are_reused_quickly():
    jobs, stats = make_jobs([0.1] * 8)
    start = time.perf_counter()
    asyncio.run(guarded(run_limited(jobs, 4)))
    elapsed = time.perf_counter() - start
    assert stats["peak"] == 4, f"peak was {stats['peak']}, expected 4."
    assert elapsed < 0.4, (
        f"8 jobs of 0.1 s with limit 4 should take about 0.2 s, took {elapsed:.2f} s. "
        "Are you running them in fixed batches or one by one?"
    )


def test_limit_bigger_than_job_count():
    jobs, stats = make_jobs([0.05] * 3)
    result = asyncio.run(guarded(run_limited(jobs, 10)))
    assert result == [0, 1, 2] and stats["peak"] == 3, (
        "With more slots than jobs, all jobs run at once."
    )


def test_semaphore_released_after_errors():
    async def bad():
        await asyncio.sleep(0.01)
        raise ValueError("boom")

    async def good():
        await asyncio.sleep(0.01)
        return "ok"

    async def main():
        with pytest.raises(ValueError):
            await run_limited([bad], 1)
        return await run_limited([good, good], 1)

    assert asyncio.run(guarded(main())) == ["ok", "ok"], (
        "After a failing job, the next call must still work. Use 'async with sem:' so the "
        "permit is released even when the job raises."
    )


def test_bad_limit_raises():
    jobs, _ = make_jobs([0.01])
    with pytest.raises(ValueError):
        asyncio.run(guarded(run_limited(jobs, 0)))


def test_empty():
    assert asyncio.run(guarded(run_limited([], 3))) == [], "No jobs: return []."
