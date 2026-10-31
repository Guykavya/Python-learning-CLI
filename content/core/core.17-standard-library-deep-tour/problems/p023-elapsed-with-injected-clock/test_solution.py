import time

import pytest

from solution import Deadline, Stopwatch, timed


class FakeClock:
    """A clock you move by hand: no real waiting, the same result every run."""

    def __init__(self, start=1000.0):
        self.now = start
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.now

    def advance(self, seconds):
        self.now += seconds


# ------------------------------------------------------------------ defaults
def test_default_clocks():
    assert Stopwatch().clock is time.perf_counter, (
        "Measure durations with time.perf_counter by default. time.time() is wall-clock time: it can jump "
        "when the computer's clock is corrected, and it has a coarser resolution."
    )
    assert Deadline(5).clock is time.monotonic, (
        "Use time.monotonic by default for deadlines: it never goes backwards."
    )


def test_real_clock_smoke():
    sw = Stopwatch()
    sw.start()
    total = sw.stop()
    assert isinstance(total, float) and 0.0 <= total < 5.0, "With the real clock a start/stop gives a small, non-negative float."


# ------------------------------------------------------------------ Stopwatch
def test_stopwatch_uses_the_injected_clock():
    clock = FakeClock()
    sw = Stopwatch(clock)
    sw.start()
    clock.advance(2.5)
    assert sw.stop() == 2.5, "stop() returns clock() at stop minus clock() at start. Call self.clock(), not time.*."


def test_stopwatch_ignores_the_starting_value():
    clock = FakeClock(start=987654.0)
    sw = Stopwatch(clock)
    sw.start()
    clock.advance(1.0)
    assert sw.stop() == 1.0, (
        "perf_counter() and monotonic() have no meaning on their own (their zero is arbitrary); only the "
        "DIFFERENCE between two readings means something."
    )


def test_laps():
    clock = FakeClock()
    sw = Stopwatch(clock)
    sw.start()
    clock.advance(1.0)
    assert sw.lap() == 1.0, "The first lap is the time since start()."
    clock.advance(3.0)
    assert sw.lap() == 3.0, "Each lap is the time since the PREVIOUS lap, not since start()."
    clock.advance(0.5)
    assert sw.stop() == 4.5, "stop() returns the TOTAL time since start(), laps included."
    assert sw.laps == [1.0, 3.0], "laps lists every lap split, in order."


def test_laps_returns_a_copy():
    clock = FakeClock()
    sw = Stopwatch(clock)
    sw.start()
    clock.advance(1.0)
    sw.lap()
    sw.laps.append(99.0)
    assert sw.laps == [1.0], "The laps property should return a copy, so callers cannot change the stopwatch's data."


def test_restart_clears_laps():
    clock = FakeClock()
    sw = Stopwatch(clock)
    sw.start()
    clock.advance(1.0)
    sw.lap()
    sw.stop()
    sw.start()
    clock.advance(2.0)
    assert sw.stop() == 2.0, "A new start() begins a new measurement from the current clock reading."
    assert sw.laps == [], "A new start() clears the old laps."


def test_stopwatch_errors():
    sw = Stopwatch(FakeClock())
    with pytest.raises(RuntimeError):
        sw.stop()
    with pytest.raises(RuntimeError):
        sw.lap()
    sw.start()
    with pytest.raises(RuntimeError):
        sw.start()
    sw.stop()
    with pytest.raises(RuntimeError):
        sw.stop()


# ------------------------------------------------------------------ Deadline
def test_deadline():
    clock = FakeClock()
    d = Deadline(10.0, clock)
    assert d.remaining() == 10.0 and d.expired() is False, "A fresh 10-second deadline has 10 seconds left."
    clock.advance(4.0)
    assert d.remaining() == 6.0, "remaining() is end - clock(): read the clock each time it is called."
    clock.advance(6.0)
    assert d.expired() is True, "At exactly the end time the deadline has expired (use >=)."
    clock.advance(5.0)
    assert d.remaining() == 0.0, "remaining() never goes below 0.0."


def test_deadline_zero_and_negative():
    clock = FakeClock()
    assert Deadline(0, clock).expired() is True, "A deadline of 0 seconds is already expired."
    with pytest.raises(ValueError):
        Deadline(-1, clock)


def test_deadline_end_is_fixed_at_creation():
    clock = FakeClock()
    clock.advance(100.0)
    d = Deadline(5.0, clock)
    clock.advance(3.0)
    assert d.remaining() == 2.0, "The end time is clock() when the Deadline is CREATED plus seconds."


# ------------------------------------------------------------------ timed
def test_timed():
    clock = FakeClock()

    def work():
        clock.advance(0.25)
        return "done"

    result, seconds = timed(work, clock)
    assert result == "done", "timed returns the function's own result first."
    assert seconds == 0.25, "and then the time it took, read from the injected clock."
    assert clock.calls == 2, "Read the clock exactly twice: once before calling func and once after."


def test_timed_real_clock():
    result, seconds = timed(lambda: sum(range(100)))
    assert result == 4950 and isinstance(seconds, float) and seconds >= 0.0, "With the default clock it still works."
