import random
import statistics

import pytest

from solution import skewness


def slow(values):
    m = statistics.fmean(values)
    sd = statistics.pstdev(values)
    return statistics.fmean(((x - m) / sd) ** 3 for x in values)


def test_symmetric_is_about_zero():
    assert skewness([1, 2, 3, 4, 5]) == pytest.approx(0.0, abs=1e-12), "Symmetric data: the cubes cancel, skewness is 0."


def test_hand_checked_value():
    assert skewness([1, 1, 4]) == pytest.approx(1 / 2 ** 0.5, rel=1e-9), "mean 2, population sd sqrt(2): z = -0.707, -0.707, 1.414; the mean of the cubes is 0.7071."


def test_right_tail_positive_left_tail_negative():
    assert skewness([1, 2, 2, 3, 10]) > 0.5, "A long tail to the right gives a clearly positive skewness."
    assert skewness([-1, -2, -2, -3, -10]) < -0.5, "A long tail to the left gives a negative skewness."


def test_mirror_gives_the_exact_negative():
    rng = random.Random(8)
    data = [rng.expovariate(1.0) for _ in range(60)]
    assert skewness([-x for x in data]) == pytest.approx(-skewness(data), rel=1e-9), "Mirroring the data must flip the sign exactly."


def test_scale_and_shift_do_not_matter():
    rng = random.Random(9)
    data = [rng.expovariate(0.5) for _ in range(40)]
    assert skewness([3 * x + 100 for x in data]) == pytest.approx(skewness(data), rel=1e-9), "Skewness is unit-free: z-scores do not change under x -> 3x + 100."


def test_too_few_values_or_no_spread():
    with pytest.raises(ValueError):
        skewness([1, 2])
    with pytest.raises(ValueError):
        skewness([])
    with pytest.raises(ValueError):
        skewness([4, 4, 4, 4])


@pytest.mark.parametrize("seed", range(10))
def test_against_a_slow_version(seed):
    rng = random.Random(seed)
    data = [rng.gauss(0, 3) ** 2 for _ in range(rng.randint(3, 50))]
    copy = list(data)
    assert skewness(data) == pytest.approx(slow(data), rel=1e-9), "Use the POPULATION sd (divide by n) inside the z-scores."
    assert data == copy, "Do not change the caller's list."
