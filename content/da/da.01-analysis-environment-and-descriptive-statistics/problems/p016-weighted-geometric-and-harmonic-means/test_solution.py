import random
import statistics

import pytest

from solution import geometric_mean, harmonic_mean, weighted_mean


def test_examples():
    assert weighted_mean([80, 60], [3, 1]) == pytest.approx(75.0, rel=1e-9), "(80*3 + 60*1) / (3 + 1) = 75."
    assert geometric_mean([1.10, 0.90]) == pytest.approx(0.99 ** 0.5, rel=1e-9), "sqrt(1.10 * 0.90) = sqrt(0.99)."
    assert harmonic_mean([60, 40]) == pytest.approx(48.0, rel=1e-9), "2 / (1/60 + 1/40) = 48."


def test_growth_is_below_one():
    assert geometric_mean([1.10, 0.90]) < 1, "+10% then -10% is a 1% loss overall: the average factor is below 1."


def test_average_speed_is_below_the_arithmetic_mean():
    assert harmonic_mean([60, 40]) < 50, "You spend more time at 40 km/h, so the average speed is below 50."


def test_equal_weights_give_the_plain_mean():
    data = [3, 5, 10]
    assert weighted_mean(data, [1, 1, 1]) == pytest.approx(6.0, rel=1e-9), "Equal weights: the ordinary mean."


@pytest.mark.parametrize("seed", range(15))
def test_against_statistics(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 12)
    data = [rng.uniform(0.5, 20) for _ in range(n)]
    weights = [rng.randint(1, 9) for _ in range(n)]
    assert weighted_mean(data, weights) == pytest.approx(statistics.fmean(data, weights), rel=1e-9), "weighted_mean differs from statistics.fmean(data, weights)."
    assert geometric_mean(data) == pytest.approx(statistics.geometric_mean(data), rel=1e-9), "geometric_mean differs from the library."
    assert harmonic_mean(data) == pytest.approx(statistics.harmonic_mean(data), rel=1e-9), "harmonic_mean differs from the library."


def test_weighted_errors():
    for values, weights in [([], []), ([1, 2], [1]), ([1, 2], [1, -1]), ([1, 2], [0, 0])]:
        with pytest.raises(ValueError):
            weighted_mean(values, weights)


@pytest.mark.parametrize("fn", [geometric_mean, harmonic_mean])
@pytest.mark.parametrize("bad", [[], [0, 1], [-1, 2], [1.5, 0.0]])
def test_non_positive_and_empty(fn, bad):
    with pytest.raises(ValueError):
        fn(bad)
