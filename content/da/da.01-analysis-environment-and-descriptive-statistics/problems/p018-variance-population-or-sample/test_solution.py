import random
import statistics

import pytest

from solution import stdev, variance


def test_examples():
    data = [2, 4, 4, 4, 5, 5, 7, 9]
    assert variance(data, 0) == pytest.approx(4.0, rel=1e-9), "Population variance: squared deviations sum to 32, divided by n = 8."
    assert stdev(data, 0) == pytest.approx(2.0, rel=1e-9), "stdev is the square root of the variance."
    assert variance([1, 2, 3, 4], 1) == pytest.approx(5 / 3, rel=1e-9), "Sample variance divides 5 by n - 1 = 3."


def test_sample_is_larger_than_population():
    data = [1, 5, 9, 2]
    assert variance(data, 1) > variance(data, 0), "Dividing by n - 1 gives a bigger number than dividing by n."


def test_one_value():
    assert variance([7], 0) == 0.0, "One value has population variance 0."
    with pytest.raises(ValueError):
        variance([7], 1)
    with pytest.raises(ValueError):
        stdev([7], 1)


def test_empty_and_bad_ddof():
    with pytest.raises(ValueError):
        variance([], 0)
    with pytest.raises(ValueError):
        variance([1, 2, 3], 2)


def test_large_values_close_together():
    data = [1_000_000_004, 1_000_000_007, 1_000_000_013, 1_000_000_016]
    assert variance(data, 0) == pytest.approx(22.5, rel=1e-9), "Use the mean first, then squared deviations; mean(x**2) - mean(x)**2 loses all the digits here."


@pytest.mark.parametrize("seed", range(20))
def test_against_statistics(seed):
    rng = random.Random(seed)
    data = [rng.gauss(10, 4) for _ in range(rng.randint(2, 50))]
    assert variance(data, 0) == pytest.approx(statistics.pvariance(data), rel=1e-9), "population variance differs from statistics.pvariance"
    assert variance(data, 1) == pytest.approx(statistics.variance(data), rel=1e-9), "sample variance differs from statistics.variance"
    assert stdev(data, 1) == pytest.approx(statistics.stdev(data), rel=1e-9), "sample stdev differs from statistics.stdev"
    assert stdev(data, 0) == pytest.approx(statistics.pstdev(data), rel=1e-9), "population stdev differs from statistics.pstdev"
