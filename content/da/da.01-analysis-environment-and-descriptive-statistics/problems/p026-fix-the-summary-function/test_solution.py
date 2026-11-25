import copy
import random
import statistics

import pytest

from solution import summarise


def test_bug1_the_callers_list_is_not_changed():
    marks = [40, 10, 30, 20]
    before = copy.deepcopy(marks)
    summarise(marks)
    assert marks == before, "Bug 1: values.sort() sorts the caller's list in place. Use sorted(values) and work on the copy."


def test_bug2_sample_standard_deviation():
    data = [2, 4, 4, 4, 5, 5, 7, 9]
    got = summarise(data)["sd"]
    assert got == pytest.approx(statistics.stdev(data), rel=1e-9), "Bug 2: the sample sd divides the squared deviations by n - 1, not by n."


def test_bug2_single_value_has_no_sample_sd():
    assert summarise([5])["sd"] is None, "One value: the sample sd is undefined, return None."


def test_bug3_even_median():
    assert summarise([1, 2])["median"] == 1.5, "Bug 3: for [1, 2] the middle values are at indexes 0 and 1 (n // 2 - 1 and n // 2)."
    assert summarise([1, 2, 3, 4])["median"] == 2.5, "Bug 3: the median of [1, 2, 3, 4] is (2 + 3) / 2."


def test_odd_median_still_right():
    assert summarise([9, 1, 5])["median"] == 5, "The odd branch was fine: sort, take the middle."


def test_whole_result_and_keys():
    got = summarise([4, 1, 3, 2])
    assert set(got) == {"n", "mean", "median", "sd", "min", "max"}, "Keep exactly the keys n, mean, median, sd, min, max."
    assert got["n"] == 4 and got["min"] == 1 and got["max"] == 4 and got["mean"] == 2.5, "n, min, max and mean were already right: do not break them."


def test_empty():
    with pytest.raises(ValueError):
        summarise([])


@pytest.mark.parametrize("seed", range(10))
def test_random_lists_against_statistics(seed):
    rng = random.Random(seed)
    data = [rng.randint(-50, 50) for _ in range(rng.randint(2, 30))]
    original = list(data)
    got = summarise(data)
    assert got["median"] == pytest.approx(statistics.median(original), rel=1e-9), f"median wrong for {original}"
    assert got["sd"] == pytest.approx(statistics.stdev(original), rel=1e-9), f"sd wrong for {original}"
    assert got["mean"] == pytest.approx(statistics.fmean(original), rel=1e-9), "mean wrong"
    assert data == original, "the input list was changed"
