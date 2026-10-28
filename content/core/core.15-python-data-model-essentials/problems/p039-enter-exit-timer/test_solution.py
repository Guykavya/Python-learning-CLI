import pytest

from solution import Timer


class FakeClock:
    def __init__(self, *times):
        self.times = list(times)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.times.pop(0)


def test_with_statement_measures_elapsed():
    clock = FakeClock(10.0, 12.5)
    with Timer(clock) as t:
        pass
    assert t.elapsed == 2.5, "elapsed = clock() at exit minus clock() at enter. __enter__ reads the clock once, __exit__ reads it once."
    assert clock.calls == 2, "Read the clock exactly twice for a finished block (once in __enter__, once in __exit__)."


def test_enter_returns_the_timer_itself():
    t = Timer(FakeClock(0, 1))
    with t as same:
        assert same is t, "__enter__ must `return self` so that `with Timer() as t:` binds t."


def test_running_flag_and_live_elapsed():
    clock = FakeClock(100.0, 103.0, 104.0)
    t = Timer(clock)
    assert t.running is False and t.elapsed == 0.0, "Before the block: not running and elapsed is 0.0 (do not read the clock yet)."
    with t:
        assert t.running is True, "Inside the block running is True."
        assert t.elapsed == 3.0, "Inside the block, elapsed is the time since __enter__ (one extra clock() read)."
    assert t.running is False, "After the block running is False."
    assert t.elapsed == 4.0, "After the block, elapsed is the frozen value clock()-start (4.0), no more clock reads."
    assert t.elapsed == 4.0, "Reading elapsed again must give the same value: it is frozen."


def test_exit_runs_when_the_block_raises_and_does_not_swallow():
    clock = FakeClock(0.0, 5.0)
    t = Timer(clock)
    with pytest.raises(ZeroDivisionError):
        with t:
            1 / 0
    assert t.elapsed == 5.0 and t.running is False, "__exit__ runs even if the block raises, so the time is still recorded."


def test_exit_returns_falsy():
    t = Timer(FakeClock(0, 1))
    t.__enter__()
    result = t.__exit__(ValueError, ValueError("x"), None)
    assert not result, "__exit__ must return a false value (False or None) so the exception is NOT suppressed."


def test_timer_can_be_reused():
    clock = FakeClock(0.0, 1.0, 10.0, 14.0)
    t = Timer(clock)
    with t:
        pass
    assert t.elapsed == 1.0, "First run: 1.0."
    with t:
        pass
    assert t.elapsed == 4.0, "A second `with t:` measures again: elapsed is replaced by 14.0 - 10.0."


def test_default_clock_is_real_time():
    with Timer() as t:
        sum(range(1000))
    assert isinstance(t.elapsed, float) and t.elapsed >= 0.0, "The default clock is time.perf_counter; elapsed is a non-negative float."
