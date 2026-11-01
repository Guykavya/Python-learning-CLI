import asyncio
import collections

import pytest

from solution import Service


class Jobs:
    """A job function that counts calls per worker and has its own async cleanup."""

    def __init__(self, fail_worker=None):
        self.calls = collections.Counter()
        self.cleaned = []
        self.fail_worker = fail_worker
        self.error = ValueError("worker crashed")

    async def __call__(self, worker_id):
        self.calls[worker_id] += 1
        if worker_id == self.fail_worker and self.calls[worker_id] == 2:
            raise self.error
        try:
            await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            await asyncio.sleep(0.02)                # slow cleanup, e.g. flush a buffer
            self.cleaned.append(worker_id)
            raise


def run(main):
    async def wrapper():
        async with asyncio.timeout(5):
            return await main()
    return asyncio.run(wrapper())


def others():
    return [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]


def test_start_runs_workers_in_background():
    jobs = Jobs()
    service = Service(jobs, workers=3)

    async def main():
        service.start()
        assert service.running, "running must be True after start()."
        await asyncio.sleep(0.05)
        await service.stop()

    run(main)
    assert sorted(jobs.calls) == [0, 1, 2], (
        f"Jobs ran for workers {sorted(jobs.calls)}; expected 0, 1, 2. Start one task per worker."
    )
    assert all(c >= 2 for c in jobs.calls.values()), (
        f"Calls per worker: {dict(jobs.calls)}. Each worker must call job in a loop, not once."
    )


def test_start_does_not_block():
    jobs = Jobs()
    service = Service(jobs, workers=2)

    async def main():
        result = service.start()
        assert not asyncio.iscoroutine(result), "start() is a plain method; it must not be async."
        assert jobs.calls == {}, "start() must only CREATE the tasks; they run when you await."
        await asyncio.sleep(0.03)
        await service.stop()

    run(main)


def test_stop_waits_for_cleanup():
    jobs = Jobs()
    service = Service(jobs, workers=3)

    async def main():
        service.start()
        await asyncio.sleep(0.05)
        await service.stop()
        return list(jobs.cleaned), list(service.log), others()

    cleaned, log, left = run(main)
    assert sorted(cleaned) == [0, 1, 2], (
        f"When stop() returned, only workers {cleaned} had finished their cleanup. cancel() only "
        "REQUESTS a stop; await the tasks (asyncio.gather(*tasks, return_exceptions=True))."
    )
    assert sorted(log) == ["start 0", "start 1", "start 2", "stop 0", "stop 1", "stop 2"], (
        f"Log was {log}. Each worker logs 'start i' once and 'stop i' once, in a finally block."
    )
    assert left == [], f"{len(left)} task(s) were still alive after stop()."
    assert not service.running, "running must be False after stop()."


def test_no_job_calls_after_stop():
    jobs = Jobs()
    service = Service(jobs, workers=2)

    async def main():
        service.start()
        await asyncio.sleep(0.03)
        await service.stop()
        before = sum(jobs.calls.values())
        await asyncio.sleep(0.05)
        return before, sum(jobs.calls.values())

    before, after = run(main)
    assert before == after, f"job was called {after - before} more time(s) after stop()."


def test_stop_twice_is_safe():
    jobs = Jobs()
    service = Service(jobs, workers=2)

    async def main():
        service.start()
        await asyncio.sleep(0.03)
        first = await service.stop()
        second = await service.stop()
        return first, second

    first, second = run(main)
    assert first == [] and second == [], f"stop() returned {first} then {second}; expected []."
    assert service.log.count("stop 0") == 1 and service.log.count("stop 1") == 1, (
        f"Log: {service.log}. A second stop() must not run any cleanup again."
    )


def test_stop_before_start():
    service = Service(Jobs(), workers=2)
    assert run(service.stop) == [], "stop() before start() has nothing to do: return []."


def test_start_twice_raises():
    jobs = Jobs()
    service = Service(jobs, workers=1)

    async def main():
        service.start()
        await asyncio.sleep(0.01)                # let the worker begin
        try:
            with pytest.raises(RuntimeError):
                service.start()
        finally:
            await service.stop()

    run(main)
    assert service.log.count("start 0") == 1, "The second start() must not start more workers."


def test_start_with_explicit_count():
    jobs = Jobs()
    service = Service(jobs, workers=2)

    async def main():
        service.start(4)
        await asyncio.sleep(0.03)
        await service.stop()

    run(main)
    assert sorted(jobs.calls) == [0, 1, 2, 3], "start(4) starts workers 0..3."


def test_crashed_worker_is_reported_not_raised():
    jobs = Jobs(fail_worker=1)
    service = Service(jobs, workers=3)

    async def main():
        service.start()
        await asyncio.sleep(0.08)
        return await service.stop()

    errors = run(main)
    assert errors == [jobs.error], (
        f"stop() returned {errors}. Return the exceptions workers died with (here the one "
        "ValueError), not the CancelledErrors of the workers you stopped, and do not raise."
    )
    assert service.log.count("stop 1") == 1, "The crashed worker's finally must log 'stop 1'."
    assert jobs.calls[0] > 2 and jobs.calls[2] > 2, (
        "One worker crashing must not stop the others."
    )


def test_async_with_starts_and_stops():
    jobs = Jobs()

    async def main():
        async with Service(jobs, workers=2) as service:
            assert service.running, "Inside 'async with', the service must be running."
            await asyncio.sleep(0.03)
        return service, others()

    service, left = run(main)
    assert not service.running and left == [], "Leaving 'async with' must stop every worker."
    assert sorted(jobs.cleaned) == [0, 1]


def test_async_with_does_not_swallow_errors():
    jobs = Jobs()
    holder = {}

    async def main():
        async with Service(jobs, workers=2) as service:
            holder["service"] = service
            await asyncio.sleep(0.02)
            raise KeyError("body failed")

    with pytest.raises(KeyError):
        run(main)
    assert sorted(holder["service"].log)[-2:] == ["stop 0", "stop 1"], (
        "Workers must be stopped even when the body raises, and the error must propagate."
    )
