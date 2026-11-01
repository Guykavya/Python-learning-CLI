import threading
import time

from solution import pipeline


class Tracker:
    def __init__(self, delay):
        self.delay = delay
        self.running = 0
        self.peak = 0
        self.threads = set()
        self.calls = 0
        self.lock = threading.Lock()

    def __call__(self, item):
        with self.lock:
            self.running += 1
            self.calls += 1
            self.peak = max(self.peak, self.running)
            self.threads.add(threading.current_thread())
        time.sleep(self.delay)
        with self.lock:
            self.running -= 1
        return item * 10


def call_with_deadline(*args, timeout=5):
    box = []
    t = threading.Thread(target=lambda: box.append(pipeline(*args)), daemon=True)
    t.start()
    t.join(timeout=timeout)
    assert not t.is_alive(), (
        "pipeline did not return. Did every worker get a sentinel? A worker blocked in "
        "queue.get() waits forever: put one sentinel PER worker after the real items."
    )
    return box[0]


def test_results_in_input_order():
    tr = Tracker(0.01)
    result = call_with_deadline(list(range(10)), tr, 3)
    assert result == [i * 10 for i in range(10)], (
        f"Got {result}. Put (index, item) on the queue and store results[index]."
    )
    assert tr.calls == 10, f"work should run once per item, ran {tr.calls} times."


def test_uses_exactly_n_worker_threads():
    tr = Tracker(0.1)
    start = time.perf_counter()
    result = call_with_deadline(list(range(8)), tr, 4)
    elapsed = time.perf_counter() - start
    assert result == [i * 10 for i in range(8)], f"Wrong results {result}."
    assert tr.peak == 4, (
        f"Peak in-flight jobs was {tr.peak}, expected 4 with n_workers=4. Start n_workers "
        "threads that all take jobs from the same queue."
    )
    assert len(tr.threads) <= 4, (
        f"work ran in {len(tr.threads)} different threads. Use exactly n_workers worker "
        "threads, not one thread per item."
    )
    assert threading.main_thread() not in tr.threads, "work must run in worker threads, not main."
    assert elapsed < 0.5, f"8 jobs of 0.1 s with 4 workers took {elapsed:.2f} s; expected ~0.2 s."


def test_all_workers_finished_on_return():
    before = threading.active_count()
    call_with_deadline(list(range(6)), Tracker(0.02), 3)
    time.sleep(0.05)
    assert threading.active_count() == before, (
        f"{threading.active_count() - before} extra thread(s) still running after pipeline "
        "returned. Join every worker before returning."
    )


def test_more_workers_than_items():
    tr = Tracker(0.01)
    result = call_with_deadline([1, 2], tr, 5)
    assert result == [10, 20], f"Got {result}. Extra workers just get a sentinel and stop."


def test_empty_items():
    result = call_with_deadline([], Tracker(0), 3)
    assert result == [], "No items: return [] (and still stop the workers)."


def test_falsy_items_are_not_sentinels():
    result = call_with_deadline([0, None, "", 3], lambda x: repr(x), 2)
    assert result == ["0", "None", "''", "3"], (
        f"Got {result}. An item equal to 0, '' or None must still be processed. Put "
        "(index, item) tuples on the queue so a real job can never look like the sentinel, "
        "and test the sentinel with 'is'."
    )
