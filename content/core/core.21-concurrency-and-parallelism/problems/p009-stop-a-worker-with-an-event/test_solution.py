import threading
import time

from solution import worker


def start_worker(stop, tick, interval):
    box = []
    t = threading.Thread(target=lambda: box.append(worker(stop, tick, interval)), daemon=True)
    t.start()
    return t, box


def test_already_stopped_returns_zero():
    stop = threading.Event()
    stop.set()
    calls = []
    assert worker(stop, lambda: calls.append(1), 0.01) == 0, "stop was already set: return 0."
    assert calls == [], "tick must not be called when stop is already set."


def test_stops_promptly_during_a_long_wait():
    stop = threading.Event()
    calls = []
    t, box = start_worker(stop, lambda: calls.append(1), 1.0)
    time.sleep(0.15)                       # first tick done, now waiting 1.0 s
    stop.set()
    start = time.perf_counter()
    t.join(timeout=2)
    waited = time.perf_counter() - start
    assert not t.is_alive(), "The worker did not stop within 2 s of stop.set()."
    assert waited < 0.3, (
        f"The worker needed {waited:.2f} s to notice stop.set(). time.sleep(interval) cannot be "
        "interrupted; wait with stop.wait(interval), which returns as soon as the event is set."
    )
    assert box == [1] and len(calls) == 1, (
        f"One tick should have happened before stop (returned {box}, ticks {len(calls)})."
    )


def test_ticks_repeat_at_the_interval():
    stop = threading.Event()
    calls = []
    t, box = start_worker(stop, lambda: calls.append(time.perf_counter()), 0.05)
    time.sleep(0.32)
    stop.set()
    t.join(timeout=2)
    assert not t.is_alive(), "The worker did not stop after stop.set()."
    assert 4 <= len(calls) <= 8, (
        f"About 0.32 s with a 0.05 s interval should give around 7 ticks, got {len(calls)}. "
        "Call tick() once per interval: tick, wait, tick, wait..."
    )
    assert box == [len(calls)], (
        f"Return the number of tick() calls ({len(calls)}), got {box}."
    )
    gaps = [b - a for a, b in zip(calls, calls[1:])]
    assert min(gaps) >= 0.04, (
        f"Two ticks came only {min(gaps):.3f} s apart. Wait the full interval between ticks."
    )


def test_does_not_tick_after_stop():
    stop = threading.Event()
    calls = []
    t, box = start_worker(stop, lambda: calls.append(1), 0.05)
    time.sleep(0.12)
    stop.set()
    t.join(timeout=2)
    n = len(calls)
    time.sleep(0.12)
    assert len(calls) == n, "tick() was called after stop was set and the worker returned."
    assert box == [n], f"Return value {box} does not match the {n} ticks."
