import inspect
import threading

from solution import Counter


def hammer(counter, n_threads, per_thread):
    barrier = threading.Barrier(n_threads)

    def work():
        barrier.wait()          # all threads start together
        for _ in range(per_thread):
            counter.increment()

    threads = [threading.Thread(target=work) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def test_starts_at_zero_and_counts():
    c = Counter()
    assert c.value == 0, "A new Counter must start at 0."
    c.increment()
    c.increment()
    assert c.value == 2, f"Two increments should give 2, got {c.value}."


def test_value_is_a_property():
    assert isinstance(inspect.getattr_static(Counter, "value"), property), (
        "value must be a property (use @property), so callers write c.value, not c.value()."
    )


def test_gap_is_still_there():
    source = inspect.getsource(Counter.increment)
    assert "sleep(0)" in source, (
        "Keep the time.sleep(0) between the read and the write. It forces a thread switch "
        "in the gap, which is how this test proves that your lock really works."
    )


def test_eight_threads_lose_nothing():
    c = Counter()
    hammer(c, 8, 200)
    assert c.value == 1600, (
        f"8 threads x 200 increments should give 1600, got {c.value}. Increments were lost: "
        "another thread ran between 'current = self._value' and 'self._value = current + 1'. "
        "Hold one Lock around ALL three lines: with self._lock: ..."
    )


def test_each_counter_has_its_own_count():
    a, b = Counter(), Counter()
    hammer(a, 4, 50)
    hammer(b, 2, 25)
    assert (a.value, b.value) == (200, 50), (
        f"Got {(a.value, b.value)}. Each Counter needs its own value and its own lock: create "
        "them in __init__, not as class attributes."
    )


def test_runs_again_without_hanging():
    c = Counter()
    hammer(c, 8, 100)
    hammer(c, 8, 100)
    assert c.value == 1600, (
        f"Got {c.value}. If this hangs or is wrong, check that the lock is always released "
        "(use 'with self._lock:' rather than acquire() without release())."
    )
