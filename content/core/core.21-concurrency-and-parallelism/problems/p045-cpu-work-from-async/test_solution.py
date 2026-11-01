import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from solution import handle_jobs


def blocking_double(job):
    time.sleep(0.1)          # a blocking call: holds this thread, not the event loop
    return job * 2


def run_with_heartbeat(jobs, cpu_fn, workers=4):
    ticks = []

    async def heartbeat():
        while True:
            ticks.append(time.perf_counter())
            await asyncio.sleep(0.02)

    async def main():
        beat = asyncio.create_task(heartbeat())
        await asyncio.sleep(0)                       # let the heartbeat start
        start = time.perf_counter()
        try:
            async with asyncio.timeout(10):
                result = await handle_jobs(jobs, cpu_fn, pool)
        finally:
            beat.cancel()
        return result, time.perf_counter() - start, start

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="test-pool") as pool:
        result, elapsed, start = asyncio.run(main())
    during = [t for t in ticks if start <= t <= start + elapsed]
    return result, elapsed, during


def test_results_in_job_order():
    result, _, _ = run_with_heartbeat([5, 1, 4, 2], blocking_double)
    assert result == [10, 2, 8, 4], f"Got {result}; results must follow the order of jobs."


def test_jobs_run_concurrently():
    result, elapsed, _ = run_with_heartbeat(list(range(8)), blocking_double, workers=4)
    assert result == [2 * i for i in range(8)]
    assert elapsed < 0.5, (
        f"8 jobs of 0.1s on 4 workers took {elapsed:.2f}s (one by one would be 0.8s). Start "
        "every run_in_executor call first, then await them all with asyncio.gather."
    )


def test_event_loop_stays_responsive():
    _, elapsed, during = run_with_heartbeat(list(range(8)), blocking_double, workers=4)
    assert len(during) >= 4, (
        f"The heartbeat ticked only {len(during)} time(s) in {elapsed:.2f}s. Calling cpu_fn "
        "directly inside async code freezes the event loop; hand it to the executor with "
        "loop.run_in_executor(executor, cpu_fn, job)."
    )


def test_uses_the_given_executor():
    names = []
    lock = threading.Lock()

    def record(job):
        with lock:
            names.append(threading.current_thread().name)
        return job

    run_with_heartbeat([1, 2, 3], record)
    assert names and all(n.startswith("test-pool") for n in names), (
        f"cpu_fn ran on threads {names}. Use the executor you were given "
        "(run_in_executor(executor, ...)); asyncio.to_thread or run_in_executor(None, ...) "
        "use the loop's default pool instead."
    )


def test_errors_propagate():
    def sometimes_fails(job):
        time.sleep(0.01)
        if job == 3:
            raise ValueError("bad image 3")
        return job

    with pytest.raises(ValueError, match="bad image 3"):
        run_with_heartbeat([1, 2, 3, 4], sometimes_fails)


def test_empty_jobs():
    result, _, _ = run_with_heartbeat([], blocking_double)
    assert result == [], "No jobs: return []."
