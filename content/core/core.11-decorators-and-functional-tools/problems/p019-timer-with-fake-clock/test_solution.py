import pytest

from solution import report, timed


def fake_clock_from(values):
    ticks = iter(values)

    def clock():
        return next(ticks)

    return clock


def test_records_durations():
    @timed(clock=fake_clock_from([10.0, 10.25, 20.0, 20.5]))
    def work(x):
        return x * 2

    assert work.durations == [], "wrapper.durations must exist and be empty right after decoration."
    assert work(1) == 2, "Return the function's result."
    assert work(2) == 4, "Return the function's result on every call."
    assert work.durations == [0.25, 0.5], "Append end - start for each call, using the clock you were given (not time.perf_counter)."


def test_clock_read_twice_per_call():
    reads = []

    def clock():
        reads.append(1)
        return float(len(reads))

    @timed(clock=clock)
    def f():
        return "ok"

    assert reads == [], "Decorating must not read the clock."
    f()
    assert len(reads) == 2, "Read the clock exactly twice per call: once before, once after."


def test_duration_recorded_on_error():
    @timed(clock=fake_clock_from([1.0, 4.0]))
    def boom():
        raise KeyError("x")

    with pytest.raises(KeyError):
        boom()
    assert boom.durations == [3.0], "Record the duration in a `finally:` block, so a call that raises is timed too, and re-raise the error."


def test_report():
    @timed(clock=fake_clock_from([10.0, 10.25, 20.0, 20.5]))
    def work():
        return None

    assert report(work) == "work: no calls", "Before any call, report says 'name: no calls'."
    work()
    work()
    assert report(work) == "work: 2 calls, total 0.750s, slowest 0.500s", "Use len, sum and max of durations, each number with :.3f."


def test_separate_lists_and_metadata():
    clock = fake_clock_from([0.0, 1.0, 0.0, 2.0])

    @timed(clock=clock)
    def a():
        """Doc a."""

    @timed(clock=clock)
    def b():
        pass

    a()
    b()
    assert (a.durations, b.durations) == ([1.0], [2.0]), "Each decorated function needs its own durations list. Create it in decorate, not at module level."
    assert a.__name__ == "a" and a.__doc__ == "Doc a.", "Use @wraps(func) on the wrapper."


def test_default_real_clock():
    @timed()
    def quick():
        return 7

    assert quick() == 7, "With @timed() the real clock is used and the result still comes back."
    assert len(quick.durations) == 1 and quick.durations[0] >= 0, "The default clock is time.perf_counter, which never goes backwards."
