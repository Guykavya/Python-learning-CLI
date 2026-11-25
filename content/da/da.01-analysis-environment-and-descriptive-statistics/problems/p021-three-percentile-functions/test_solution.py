import random
import statistics

import pytest

from solution import percentile_exclusive, percentile_inclusive, percentile_nearest_rank

DATA = [15, 20, 35, 40, 50]


def test_the_chapter_example():
    assert percentile_nearest_rank(DATA, 25) == 20, "Nearest rank: ceil(0.25 * 5) = 2, the 2nd value is 20."
    assert percentile_inclusive(DATA, 25) == pytest.approx(20.0, rel=1e-9), "Inclusive: position (5 - 1) * 0.25 = 1 (0-based) is 20."
    assert percentile_exclusive(DATA, 25) == pytest.approx(17.5, rel=1e-9), "Exclusive: position (5 + 1) * 0.25 = 1.5 (1-based): halfway between 15 and 20."
    assert percentile_inclusive(DATA, 90) == pytest.approx(46.0, rel=1e-9), "Inclusive p90: position 3.6, 40 + 0.6 * 10."


def test_extremes_of_the_inclusive_method():
    assert percentile_inclusive(DATA, 0) == 15 and percentile_inclusive(DATA, 100) == 50, "Inclusive: p=0 is the minimum and p=100 the maximum."


def test_nearest_rank_returns_a_data_value():
    rng = random.Random(1)
    data = [rng.randint(0, 1000) for _ in range(23)]
    for p in range(0, 101, 5):
        assert percentile_nearest_rank(data, p) in data, "Nearest-rank never interpolates: the answer is one of the data values."


@pytest.mark.parametrize("n", [2, 3, 5, 8, 11, 20, 37])
def test_inclusive_and_exclusive_against_the_library(n):
    rng = random.Random(n)
    data = [rng.gauss(50, 12) for _ in range(n)]
    inc = statistics.quantiles(data, n=100, method="inclusive")
    exc = statistics.quantiles(data, n=100, method="exclusive")
    for p in range(1, 100):
        assert percentile_inclusive(data, p) == pytest.approx(inc[p - 1], rel=1e-9), f"inclusive p={p}, n={n} differs from the library"
        pos = (n + 1) * p / 100
        if 1 <= pos <= n:
            assert percentile_exclusive(data, p) == pytest.approx(exc[p - 1], rel=1e-9), f"exclusive p={p}, n={n} differs from the library"
        else:
            with pytest.raises(ValueError):
                percentile_exclusive(data, p)


@pytest.mark.parametrize("n", [1, 2, 7, 10, 19, 30])
def test_nearest_rank_against_a_slow_definition(n):
    rng = random.Random(100 + n)
    data = [rng.randint(0, 50) for _ in range(n)]
    for p in range(1, 101):
        slow = min(v for v in data if 100 * sum(1 for x in data if x <= v) >= p * n)
        assert percentile_nearest_rank(data, p) == slow, f"nearest-rank p={p}, n={n}: smallest value with at least p% of data at or below it. (Use p * n / 100, not p / 100 * n.)"


def test_sanity_properties():
    rng = random.Random(7)
    data = [rng.uniform(-5, 5) for _ in range(15)]
    for fn in (percentile_nearest_rank, percentile_inclusive, percentile_exclusive):
        values = []
        for p in range(10, 91, 10):
            values.append(fn(data, p))
        assert values == sorted(values), f"{fn.__name__} must not decrease when p increases."
        assert all(min(data) <= v <= max(data) for v in values), f"{fn.__name__} must stay between the minimum and the maximum."
    assert percentile_inclusive(data, 50) == pytest.approx(statistics.median(data), rel=1e-9), "The inclusive 50th percentile is the median."


def test_errors_and_no_mutation():
    for fn in (percentile_nearest_rank, percentile_inclusive, percentile_exclusive):
        with pytest.raises(ValueError):
            fn([], 50)
        with pytest.raises(ValueError):
            fn([1, 2, 3], 101)
        with pytest.raises(ValueError):
            fn([1, 2, 3], -1)
    with pytest.raises(ValueError):
        percentile_exclusive([1, 2, 3], 10)
    data = [3, 1, 2]
    percentile_inclusive(data, 50)
    assert data == [3, 1, 2], "Do not sort the caller's list in place."
