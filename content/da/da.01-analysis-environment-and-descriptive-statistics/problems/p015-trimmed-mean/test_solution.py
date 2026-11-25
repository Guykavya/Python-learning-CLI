import random
import statistics

import pytest

from solution import trimmed_mean


def test_example():
    assert trimmed_mean([1, 2, 3, 4, 100], 0.2) == pytest.approx(3.0, rel=1e-9), "n = 5, k = floor(5 * 0.2) = 1: drop 1 and 100, mean of [2, 3, 4] is 3."


def test_zero_proportion_is_the_mean():
    assert trimmed_mean([1, 2, 3, 4, 100], 0) == pytest.approx(22.0, rel=1e-9), "proportion=0 cuts nothing: with s[k:-k] and k=0 you would get an empty slice; use len(s) - k."


def test_default_proportion_cuts_floor_of_ten_percent():
    data = list(range(1, 21)) + [1000]
    got = trimmed_mean(data)
    k = 2
    s = sorted(data)[k:-k]
    assert got == pytest.approx(statistics.fmean(s), rel=1e-9), "Default 0.1 with n=21: k = floor(2.1) = 2 from each end."


def test_floor_not_round():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    assert trimmed_mean(data, 0.19) == pytest.approx(statistics.fmean(data[2:-2]), rel=1e-9), "15 * 0.19 = 2.85: floor is 2 (rounding would give 3)."


def test_unsorted_input_and_no_mutation():
    data = [100, 3, 1, 4, 2]
    copy = list(data)
    assert trimmed_mean(data, 0.2) == pytest.approx(3.0, rel=1e-9), "Sort a copy before trimming; the extremes are the smallest and largest values, not the first and last entries."
    assert data == copy, "You sorted the caller's list in place: use sorted(values)."


@pytest.mark.parametrize("bad", [0.5, 0.7, -0.1])
def test_bad_proportion(bad):
    with pytest.raises(ValueError):
        trimmed_mean([1, 2, 3], bad)


def test_empty():
    with pytest.raises(ValueError):
        trimmed_mean([])


def test_random_against_statistics():
    for seed in range(15):
        rng = random.Random(seed)
        data = [rng.gauss(50, 10) for _ in range(rng.randint(10, 60))]
        k = int(len(data) * 0.1)
        want = statistics.fmean(sorted(data)[k:len(data) - k])
        assert trimmed_mean(data, 0.1) == pytest.approx(want, rel=1e-9), "Wrong trimmed mean on random data."
