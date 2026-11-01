import inspect
import threading
import time

import pytest

import solution
from solution import BoundedBuffer


def in_thread(target, *args):
    """Run target(*args) in a DAEMON thread so a hang cannot freeze the test run."""
    box = {}

    def runner():
        try:
            box["value"] = target(*args)
        except BaseException as error:      # report errors to the test
            box["error"] = error

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    return thread, box


def test_fifo_in_one_thread():
    buf = BoundedBuffer(3)
    for x in "abc":
        buf.put(x)
    assert len(buf) == 3, f"len is {len(buf)} after 3 puts."
    got = [buf.get(), buf.get(), buf.get()]
    assert got == ["a", "b", "c"], f"Got {got}. First in, first out: popleft(), not pop()."
    assert len(buf) == 0


def test_get_on_empty_times_out():
    buf = BoundedBuffer(2)
    start = time.perf_counter()
    with pytest.raises(TimeoutError):
        buf.get(timeout=0.1)
    elapsed = time.perf_counter() - start
    assert 0.08 <= elapsed < 1.0, (
        f"get(timeout=0.1) gave up after {elapsed:.2f}s. Pass the timeout to cond.wait_for and "
        "raise TimeoutError when it returns False."
    )


def test_put_on_full_times_out():
    buf = BoundedBuffer(1)
    buf.put("x")
    with pytest.raises(TimeoutError):
        buf.put("y", timeout=0.1)
    assert len(buf) == 1, "A put that timed out must not add its item."


def test_get_blocks_until_put():
    buf = BoundedBuffer(2)
    thread, box = in_thread(buf.get)
    time.sleep(0.1)
    assert thread.is_alive(), (
        "get() on an empty buffer returned (or crashed) instead of waiting: "
        f"{box}. It must block until an item arrives."
    )
    buf.put("hello")
    thread.join(timeout=2)
    assert not thread.is_alive(), (
        "The waiting get() never woke up after put(). Call cond.notify_all() after appending."
    )
    assert box.get("value") == "hello", f"The waiting get() returned {box}."


def test_put_blocks_while_full():
    buf = BoundedBuffer(1)
    buf.put(1)
    thread, box = in_thread(buf.put, 2)
    time.sleep(0.1)
    assert thread.is_alive(), f"put() on a full buffer did not wait ({box}). It must block."
    assert len(buf) == 1, f"The buffer holds {len(buf)} items but its capacity is 1."
    assert buf.get(timeout=1) == 1
    thread.join(timeout=2)
    assert not thread.is_alive(), (
        "The blocked put() never woke up after get() made room. Call cond.notify_all() after "
        "removing an item too."
    )
    assert buf.get(timeout=1) == 2


def test_many_producers_and_consumers():
    buf = BoundedBuffer(4)
    received = []
    overfull = []
    lock = threading.Lock()

    def producer(base):
        for i in range(100):
            buf.put(base + i, timeout=5)
            if len(buf) > 4:
                overfull.append(len(buf))

    def consumer():
        for _ in range(100):
            item = buf.get(timeout=5)
            with lock:
                received.append(item)

    threads = [threading.Thread(target=producer, args=(b,), daemon=True) for b in (0, 1000, 2000)]
    threads += [threading.Thread(target=consumer, daemon=True) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert not any(t.is_alive() for t in threads), (
        "Some threads never finished: a waiter was not woken. Use notify_all() (one Condition "
        "is shared by putters AND getters, so notify() may wake the wrong kind)."
    )
    expected = sorted(list(range(100)) + list(range(1000, 1100)) + list(range(2000, 2100)))
    assert sorted(received) == expected, (
        f"{len(received)} items received, {len(set(received))} distinct; expected 300 distinct. "
        "Do every check-and-change inside 'with self._cond'."
    )
    assert not overfull, f"The buffer grew to {max(overfull)} items with capacity 4."


def test_bad_capacity():
    with pytest.raises(ValueError):
        BoundedBuffer(0)


def test_does_not_use_the_queue_module():
    source = inspect.getsource(solution)
    assert "import queue" not in source and "from queue" not in source, (
        "Build it yourself with a deque and threading.Condition; the queue module is off limits "
        "here."
    )
