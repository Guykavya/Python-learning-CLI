import random
import statistics

import pytest

from solution import flag_iqr, flag_z


def ordinary_with_one_outlier():
    rng = random.Random(3)
    data = [rng.gauss(50, 2) for _ in range(30)]
    data.insert(17, 100.0)
    return data


def test_an_ordinary_outlier_is_caught_by_both():
    data = ordinary_with_one_outlier()
    assert flag_iqr(data) == [17], "The value 100 among 30 values near 50 lies far outside the IQR fences."
    assert flag_z(data) == [17], "With 31 values, one far value has a z-score above 3."


def test_two_huge_values_mask_each_other_in_the_z_score():
    data = [10, 12, 11, 13, 12, 11, 10, 12, 13, 11, 1000, 1100]
    sd = statistics.stdev(data)
    mean = statistics.fmean(data)
    assert max(abs(x - mean) / sd for x in data) < 3, "Self-check of the test data: both outliers have |z| below 3."
    assert flag_z(data) == [], "Masking: two huge values inflate the mean and the sd, so neither gets a z above 3. The z-score rule must miss them here."
    assert flag_iqr(data) == [10, 11], "The quartiles ignore the top quarter, so the IQR fences still catch both huge values."


def test_a_short_list_cannot_trigger_the_three_sigma_rule():
    data = [10, 11, 12, 11, 10, 12, 11, 500]
    assert flag_z(data) == [], "With n = 8 a sample z-score can never exceed 2.47, so nothing is flagged."
    assert flag_iqr(data) == [7], "The IQR rule does not have this blind spot."


def test_constant_list_has_no_flags_and_no_division_by_zero():
    assert flag_iqr([5] * 10) == [], "A constant list has no outliers."
    assert flag_z([5] * 10) == [], "sd = 0: return [] instead of dividing by zero."


def test_tiny_lists():
    assert flag_z([]) == [] and flag_iqr([]) == [], "An empty list has no outliers."
    assert flag_z([7]) == [] and flag_iqr([7]) == [], "One value has no outliers."


def test_fence_is_strict():
    data = [0, 4, 4, 4, 4, 4, 4, 8]
    q1, _, q3 = statistics.quantiles(data, n=4, method="inclusive")
    assert flag_iqr(data, k=0) == [i for i, x in enumerate(data) if x < q1 or x > q3], "A value exactly on a fence is not flagged (strict < and >)."


def test_low_outliers_and_k():
    data = [100, 101, 99, 100, 102, 98, 100, 101, 99, 100, 40]
    assert flag_iqr(data) == [10], "A low outlier is flagged too."
    assert flag_iqr(data, k=100) == [], "A huge k widens the fences until nothing is flagged."


@pytest.mark.parametrize("seed", range(10))
def test_random_against_a_slow_version(seed):
    rng = random.Random(seed)
    data = [rng.gauss(0, 1) for _ in range(rng.randint(5, 40))] + [rng.choice([-9, 9, 15])]
    q1, _, q3 = statistics.quantiles(sorted(data), n=4, method="inclusive")
    want_iqr = [i for i, x in enumerate(data) if x < q1 - 1.5 * (q3 - q1) or x > q3 + 1.5 * (q3 - q1)]
    m, s = statistics.fmean(data), statistics.stdev(data)
    want_z = [i for i, x in enumerate(data) if abs(x - m) / s > 3]
    assert flag_iqr(data) == want_iqr, "flag_iqr differs from the definition (inclusive quartiles, strict fences)."
    assert flag_z(data) == want_z, "flag_z differs from the definition (sample sd, strictly greater than t)."
