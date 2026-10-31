import pytest

from solution import best_time


class FakeClock:
    """Returns the given times one by one and counts how often it was read."""

    def __init__(self, times):
        self.times = list(times)
        self.reads = 0

    def __call__(self):
        value = self.times[self.reads]
        self.reads += 1
        return value


def test_example_from_problem():
    clock = FakeClock([0.0, 2.0, 10.0, 11.0, 20.0, 23.0])
    calls = []
    got = best_time(lambda: calls.append(1), number=4, repeat=3, timer=clock)
    assert got == pytest.approx(0.25), (
        f"Got {got}. Batches took 2.0, 1.0 and 3.0 s for 4 calls each; the fastest per call is 1.0 / 4 = 0.25. "
        "Did you take the mean, forget to divide by number, or return the total?"
    )
    assert len(calls) == 12, f"fn must run number * repeat = 12 times, it ran {len(calls)} times."


def test_minimum_not_mean():
    clock = FakeClock([0.0, 5.0, 5.0, 6.0, 6.0, 7.0])
    got = best_time(lambda: None, number=1, repeat=3, timer=clock)
    assert got == pytest.approx(1.0), (
        f"Got {got}. The batches took 5, 1 and 1 s. Report the MINIMUM (1.0): noise only makes runs slower, "
        "so the mean (2.33) is pulled up by the one disturbed batch."
    )


def test_divides_by_number():
    clock = FakeClock([0.0, 10.0])
    got = best_time(lambda: None, number=100, repeat=1, timer=clock)
    assert got == pytest.approx(0.1), f"Got {got}. 10 s for 100 calls is 0.1 s PER CALL: divide the batch time by number."


def test_timer_read_only_around_batches():
    clock = FakeClock([float(i) for i in range(100)])
    best_time(lambda: None, number=7, repeat=3, timer=clock)
    assert clock.reads == 6, (
        f"The timer was read {clock.reads} times. Read it once before and once after each batch "
        "(2 * repeat = 6), not around every single call: that adds the clock's own cost to every call."
    )


def test_calls_happen_between_reads():
    events = []
    times = iter([0.0, 1.0, 1.0, 3.0])

    def timer():
        events.append("t")
        return next(times)

    best_time(lambda: events.append("f"), number=2, repeat=2, timer=timer)
    assert events == ["t", "f", "f", "t", "t", "f", "f", "t"], (
        f"Order was {''.join(events)}. Each batch must be: read clock, call fn number times, read clock."
    )


def test_returns_float_with_int_clock():
    ticks = iter([0, 3, 10, 12])
    got = best_time(lambda: None, number=2, repeat=2, timer=lambda: next(ticks))
    assert got == 1.0 and isinstance(got, float), f"Got {got!r}. 2 s / 2 calls = 1.0; use true division / so the answer is a float."


@pytest.mark.parametrize("number, repeat", [(0, 3), (3, 0), (-1, 1), (1, -5)])
def test_bad_arguments(number, repeat):
    try:
        best_time(lambda: None, number=number, repeat=repeat)
    except ValueError:
        return
    raise AssertionError(
        f"number={number}, repeat={repeat} must raise ValueError. Check number < 1 or repeat < 1 before timing anything."
    )


def test_real_clock_default():
    got = best_time(lambda: sum(range(200)), number=200, repeat=3)
    assert 0 < got < 0.01, (
        f"Got {got}. With the default time.perf_counter the per-call time of sum(range(200)) is a small positive "
        "number of seconds (microseconds). 0 means the clock was not read; a big number means you did not divide."
    )
