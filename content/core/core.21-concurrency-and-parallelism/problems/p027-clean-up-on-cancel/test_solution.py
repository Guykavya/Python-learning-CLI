import asyncio

import pytest

from solution import use_resource


class FakePool:
    def __init__(self, acquire_delay=0.0):
        self.acquire_delay = acquire_delay
        self.out = set()
        self.acquired = 0
        self.released = 0

    @property
    def in_use(self):
        return len(self.out)

    async def acquire(self):
        await asyncio.sleep(self.acquire_delay)
        self.acquired += 1
        conn = f"conn{self.acquired}"
        self.out.add(conn)
        return conn

    def release(self, conn):
        if conn not in self.out:
            raise RuntimeError(f"release({conn!r}): not borrowed (released twice, or never acquired)")
        self.out.remove(conn)
        self.released += 1


async def slow_work(conn):
    await asyncio.sleep(5)
    return "never"


async def cancel_after(coro, delay):
    task = asyncio.create_task(coro)
    await asyncio.sleep(delay)
    task.cancel()
    try:
        async with asyncio.timeout(2):
            await task
    except asyncio.CancelledError:
        pass
    return task


def test_success_returns_and_releases():
    pool = FakePool()

    async def work(conn):
        await asyncio.sleep(0.01)
        return f"rows from {conn}"

    assert asyncio.run(use_resource(pool, work)) == "rows from conn1", "Return what work(conn) returns."
    assert pool.in_use == 0 and pool.released == 1, (
        f"in_use={pool.in_use}, released={pool.released}. Release the connection once after success."
    )


def test_error_releases_and_propagates():
    pool = FakePool()

    async def work(conn):
        await asyncio.sleep(0.01)
        raise ValueError("bad query")

    with pytest.raises(ValueError, match="bad query"):
        asyncio.run(use_resource(pool, work))
    assert pool.in_use == 0, (
        "work raised and the connection was never released. A release after the await is "
        "skipped by the exception; put it in a finally block."
    )


def test_cancel_during_work_releases_connection():
    pool = FakePool()

    async def main():
        return await cancel_after(use_resource(pool, slow_work), 0.05)

    task = asyncio.run(main())
    assert pool.acquired == 1, "The connection should have been acquired before the cancel."
    assert pool.in_use == 0, (
        "The task was cancelled while work ran, and the connection leaked. CancelledError is an "
        "exception thrown in at the await: a finally block runs for it too."
    )


def test_cancellation_is_not_swallowed():
    pool = FakePool()

    async def main():
        return await cancel_after(use_resource(pool, slow_work), 0.05)

    task = asyncio.run(main())
    assert task.cancelled(), (
        "task.cancelled() is False: your code caught CancelledError and returned normally. "
        "Clean up in finally (or re-raise with a bare 'raise'), never swallow the cancellation."
    )


def test_cancel_while_acquiring_releases_nothing():
    pool = FakePool(acquire_delay=0.3)

    async def main():
        return await cancel_after(use_resource(pool, slow_work), 0.05)

    task = asyncio.run(main())
    assert pool.acquired == 0 and pool.released == 0, (
        f"acquired={pool.acquired}, released={pool.released}. The cancel came during acquire(), "
        "so there is no connection to give back. Keep acquire() OUTSIDE the try."
    )
    assert task.cancelled(), "Cancellation during acquire() must propagate too."


def test_many_requests_no_leaks():
    pool = FakePool()

    async def quick(conn):
        await asyncio.sleep(0.01)
        return conn

    async def main():
        tasks = [asyncio.create_task(use_resource(pool, quick if i % 2 else slow_work)) for i in range(10)]
        await asyncio.sleep(0.1)
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    asyncio.run(main())
    assert pool.acquired == 10 and pool.in_use == 0, (
        f"After 10 requests (5 finished, 5 cancelled) {pool.in_use} connection(s) are still out."
    )
