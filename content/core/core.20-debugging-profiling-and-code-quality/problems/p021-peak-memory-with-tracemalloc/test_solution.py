import tracemalloc

import pytest

from solution import peak_bytes


@pytest.fixture(autouse=True)
def tracing_off_after_each_test():
    was = tracemalloc.is_tracing()
    yield
    if tracemalloc.is_tracing() and not was:
        tracemalloc.stop()  # clean up if a wrong solution left it running


def with_list(n):
    return sum([i * i for i in range(n)])


def with_generator(n):
    return sum(i * i for i in range(n))


def build_and_drop(n):
    data = [str(i) * 3 for i in range(n)]
    del data
    return None


def explode():
    big = [0] * 100_000
    raise RuntimeError(len(big))


def test_list_needs_a_lot():
    got = peak_bytes(with_list, 100_000)
    assert isinstance(got, int), f"Return an int number of bytes, got {type(got).__name__}."
    assert got > 1_000_000, (
        f"Got {got}. A list of 100,000 squares needs megabytes at its peak. Did you use the PEAK "
        "(second item of get_traced_memory), and start tracing BEFORE calling fn?"
    )


def test_generator_needs_little():
    got = peak_bytes(with_generator, 100_000)
    assert 0 <= got < 50_000, (
        f"Got {got}. A generator holds one value at a time, so its peak is tiny. A big number means you counted "
        "memory that was already in use before the call: subtract the starting current value."
    )


def test_ratio_list_vs_generator():
    big = peak_bytes(with_list, 100_000)
    small = peak_bytes(with_generator, 100_000)
    assert big > 50 * max(small, 1), f"list peak {big}, generator peak {small}: the list version must need far more memory."


def test_peak_not_current():
    got = peak_bytes(build_and_drop, 50_000)
    assert got > 1_000_000, (
        f"Got {got}. The list is freed before the function returns, so the CURRENT memory at the end is "
        "small, but the PEAK is megabytes. Use the peak value."
    )


def test_stops_tracing_it_started():
    assert not tracemalloc.is_tracing(), "Tracing is already on at the start of this test: an earlier call of peak_bytes did not stop it."
    peak_bytes(with_generator, 10)
    assert not tracemalloc.is_tracing(), "Tracing was not running before, so peak_bytes must stop it afterwards (tracing slows everything down)."


def test_leaves_existing_tracing_running():
    tracemalloc.start()
    try:
        _ = [bytes(1000) for _ in range(2000)]  # an earlier, bigger peak of about 2 MB
        del _
        got = peak_bytes(with_generator, 1000)
        still = tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()
    assert still, "Tracing was already running (someone else started it), so peak_bytes must NOT stop it."
    assert got < 50_000, (
        f"Got {got}. The old 2 MB peak from before the call must not count: call tracemalloc.reset_peak() "
        "and measure from the current value at the start."
    )


def test_exception_stops_tracing_and_propagates():
    with pytest.raises(RuntimeError):
        peak_bytes(explode)
    assert not tracemalloc.is_tracing(), "When fn raises, still stop the tracing you started: use try/finally."


def test_kwargs():
    got = peak_bytes(with_list, n=50_000)
    assert got > 500_000, f"Got {got}. Pass **kwargs on to fn."
