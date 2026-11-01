import asyncio
import time

from solution import produce_consume


class Tracker:
    def __init__(self, delay=0.02):
        self.delay = delay
        self.pulled = 0
        self.started = 0
        self.active = 0
        self.peak_active = 0
        self.max_ahead = 0
        self.consumed = []

    def source(self, n):
        for i in range(n):
            # i items already pulled before this one; how far ahead of the consumers are we?
            self.max_ahead = max(self.max_ahead, self.pulled - self.started)
            self.pulled += 1
            yield i

    async def consume(self, item):
        self.started += 1
        self.active += 1
        self.peak_active = max(self.peak_active, self.active)
        await asyncio.sleep(self.delay)
        self.active -= 1
        self.consumed.append(item)
        return item * item


def run(n, maxsize, n_consumers, delay=0.02):
    tracker = Tracker(delay)

    async def main():
        async with asyncio.timeout(10):
            result = await produce_consume(tracker.source(n), tracker.consume, maxsize, n_consumers)
        others = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        return result, others

    result, others = asyncio.run(main())
    return result, others, tracker


def test_results_in_item_order():
    result, _, _ = run(12, maxsize=2, n_consumers=3)
    assert result == [i * i for i in range(12)], (
        f"Got {result}. Keep each item's index with it through the queue and put the results "
        "back in item order."
    )


def test_every_item_consumed_once():
    _, _, tracker = run(15, maxsize=3, n_consumers=4)
    assert sorted(tracker.consumed) == list(range(15)), (
        f"Consumed {sorted(tracker.consumed)}. Every item exactly once: no item lost, none twice."
    )


def test_producer_is_held_back():
    _, _, tracker = run(20, maxsize=2, n_consumers=2)
    assert tracker.max_ahead <= 2 + 1, (
        f"The producer got {tracker.max_ahead} items ahead of the consumers; with maxsize=2 it "
        "may be at most 3 ahead (2 in the queue + 1 waiting to be put). Did you build a list "
        "of all items first, or use an unbounded queue / put_nowait?"
    )


def test_items_are_pulled_lazily():
    tracker = Tracker()
    pulled_at_first_consume = []
    original = tracker.consume

    async def consume(item):
        if not pulled_at_first_consume:
            pulled_at_first_consume.append(tracker.pulled)
        return await original(item)

    async def main():
        async with asyncio.timeout(10):
            return await produce_consume(tracker.source(1000), consume, 2, 1)

    tracker.delay = 0.0
    asyncio.run(main())
    assert pulled_at_first_consume[0] <= 4, (
        f"{pulled_at_first_consume[0]} of 1000 items had been read before the first one was "
        "consumed. Iterate over `items` in the producer, one put at a time; never list(items)."
    )


def test_consumers_run_concurrently():
    start = time.perf_counter()
    _, _, tracker = run(12, maxsize=4, n_consumers=4, delay=0.05)
    elapsed = time.perf_counter() - start
    assert tracker.peak_active == 4, (
        f"At most {tracker.peak_active} consume() calls overlapped; with 4 consumers it should "
        "be 4. Start all consumer tasks before waiting for anything."
    )
    assert elapsed < 0.45, (
        f"Took {elapsed:.2f}s; 12 items x 0.05s over 4 consumers is about 0.15s (serial 0.6s)."
    )


def test_consumers_finish_cleanly():
    _, others, _ = run(6, maxsize=2, n_consumers=3)
    assert others == [], (
        f"{len(others)} task(s) were still alive after produce_consume returned. Stop each "
        "consumer: one sentinel per consumer, or queue.join() then cancel and await them."
    )


def test_one_consumer_maxsize_one():
    result, others, tracker = run(5, maxsize=1, n_consumers=1)
    assert result == [0, 1, 4, 9, 16], "Must also work with a single consumer and maxsize=1."
    assert tracker.max_ahead <= 2
    assert others == []


def test_empty_items():
    result, others, _ = run(0, maxsize=2, n_consumers=3)
    assert result == [], "No items: return [] (and still stop the consumers)."
    assert others == [], "Consumers must stop even when there was nothing to do."


def test_works_with_a_plain_list():
    async def double(x):
        await asyncio.sleep(0)
        return 2 * x

    async def main():
        async with asyncio.timeout(5):
            return await produce_consume([3, 1, 2], double, 1, 2)

    assert asyncio.run(main()) == [6, 2, 4], "items can be any iterable, a list too."
