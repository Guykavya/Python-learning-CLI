import asyncio
import time

import pytest

from solution import RateLimiter


class FakeTime:
    """A clock that only moves when someone sleeps on it."""

    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def clock(self):
        return self.now

    async def sleep(self, seconds):
        self.sleeps.append(seconds)
        wake_at = self.now + seconds
        await asyncio.sleep(0)                 # let other tasks run, like a real sleep
        self.now = max(self.now, wake_at)


def make(rate, per):
    fake = FakeTime()
    return RateLimiter(rate, per, clock=fake.clock, sleep=fake.sleep), fake


def test_first_rate_starts_do_not_wait():
    limiter, fake = make(3, 1.0)

    async def main():
        for _ in range(3):
            async with limiter:
                pass

    asyncio.run(main())
    assert fake.sleeps == [], (
        f"Slept {fake.sleeps} although only 3 starts were made with rate=3. Only wait when the "
        "window already holds `rate` starts."
    )


def test_sequential_starts_follow_the_window():
    limiter, fake = make(3, 1.0)
    starts = []

    async def main():
        for _ in range(7):
            async with limiter:
                starts.append(fake.now)

    asyncio.run(main())
    assert starts == pytest.approx([0, 0, 0, 1, 1, 1, 2]), (
        f"Start times were {starts}. With rate=3 per 1.0 s: three at 0, three at 1, one at 2. "
        "Read the time with the injected clock() and wait with the injected sleep()."
    )
    assert fake.sleeps == pytest.approx([1.0, 1.0]), (
        f"Sleeps were {fake.sleeps}. Sleep exactly until the oldest start expires "
        "(oldest + per - now), not a fixed amount and not in small polling steps."
    )


def test_sliding_not_fixed_window():
    limiter, fake = make(2, 1.0)
    starts = []

    async def go():
        async with limiter:
            starts.append(fake.now)

    async def main():
        await go()              # t = 0.0
        fake.now = 0.5
        await go()              # t = 0.5
        fake.now = 0.6
        await go()              # must wait until 1.0
        await go()              # must wait until 1.5

    asyncio.run(main())
    assert starts == pytest.approx([0.0, 0.5, 1.0, 1.5]), (
        f"Start times were {starts}, expected [0.0, 0.5, 1.0, 1.5]. Count the starts in the "
        "last `per` seconds (a deque of start times), not starts per whole second."
    )


def test_start_exactly_per_ago_has_expired():
    limiter, fake = make(1, 1.0)
    starts = []

    async def main():
        async with limiter:
            starts.append(fake.now)
        fake.now = 1.0
        async with limiter:
            starts.append(fake.now)

    asyncio.run(main())
    assert fake.sleeps == [], (
        "A start at 0.0 stops counting at exactly 0.0 + 1.0. At t=1.0 there must be no wait: "
        "drop starts with start + per <= now."
    )


def test_concurrent_waiters_respect_the_rate():
    limiter, fake = make(3, 1.0)
    starts = []

    async def go(i):
        async with limiter:
            starts.append((fake.now, i))

    async def main():
        async with asyncio.timeout(5):
            await asyncio.gather(*(go(i) for i in range(7)))

    asyncio.run(main())
    times = sorted(t for t, _ in starts)
    assert times == pytest.approx([0, 0, 0, 1, 1, 1, 2]), (
        f"Start times with 7 concurrent tasks were {times}. Several waiters must not all slip "
        "in when one slot frees; check the window again after every sleep."
    )


def test_waiters_are_served_in_arrival_order():
    limiter, fake = make(1, 1.0)
    order = []

    async def go(i):
        async with limiter:
            order.append(i)

    async def main():
        async with asyncio.timeout(5):
            tasks = []
            for i in range(5):
                tasks.append(asyncio.create_task(go(i)))
                await asyncio.sleep(0)          # task i arrives before task i + 1
            await asyncio.gather(*tasks)

    asyncio.run(main())
    assert order == [0, 1, 2, 3, 4], (
        f"Order was {order}. Waiters must enter first come, first served. An asyncio.Lock "
        "around the check-and-wait gives FIFO order."
    )


def test_exception_in_body_is_not_swallowed():
    limiter, _ = make(2, 1.0)

    async def main():
        async with limiter:
            raise KeyError("boom")

    with pytest.raises(KeyError):
        asyncio.run(main())


def test_as_value_returns_something_usable():
    limiter, _ = make(2, 1.0)

    async def main():
        async with limiter as entered:
            return entered

    assert asyncio.run(main()) is limiter, "__aenter__ should return self (the limiter)."


def test_bad_arguments():
    with pytest.raises(ValueError):
        RateLimiter(0, 1.0)
    with pytest.raises(ValueError):
        RateLimiter(3, 0)
    # A limiter that can never let anything start would make every caller wait forever.


def test_real_clock_sanity():
    limiter = RateLimiter(2, 0.2)          # default clock and sleep

    async def main():
        start = time.monotonic()
        for _ in range(5):                 # starts at about 0, 0, 0.2, 0.2, 0.4
            async with limiter:
                pass
        return time.monotonic() - start

    elapsed = asyncio.run(main())
    assert 0.35 <= elapsed < 1.5, (
        f"5 starts at 2 per 0.2 s took {elapsed:.2f}s; expected about 0.4 s. Too fast means the "
        "limiter does not wait; too slow means it waits more than needed."
    )
