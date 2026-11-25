import random

import pytest

from solution import histogram_counts


def test_example():
    rows, outside = histogram_counts([1, 2, 2, 3, 4, 10], bins=3)
    assert rows == [(1.0, 4.0, 4), (4.0, 7.0, 1), (7.0, 10.0, 1)], f"Got {rows}. 4 belongs to [4, 7) and the maximum 10 to the last bin."
    assert outside == 0, "Without a given range nothing is outside."


def test_the_maximum_lands_in_the_last_bin():
    rows, _ = histogram_counts([0, 5, 10], bins=2)
    assert [r[2] for r in rows] == [1, 2], "Half-open bins drop the max: the largest value must be counted in the last bin (5 is in [5, 10], so is 10)."


def test_counts_sum_to_n_without_a_range():
    rng = random.Random(4)
    data = [rng.randint(0, 100) for _ in range(200)]
    rows, outside = histogram_counts(data, bins=10)
    assert sum(r[2] for r in rows) == 200, "Every value must be counted when the range is the data range."
    assert outside == 0


def test_values_outside_a_given_range():
    rows, outside = histogram_counts([-5, 0, 3, 9, 10, 11, 100], bins=2, low=0, high=10)
    assert outside == 3, "-5, 11 and 100 are outside [0, 10]; they are counted, not binned."
    assert [r[2] for r in rows] == [2, 2], "0 and 3 in [0, 5); 9 and 10 in [5, 10]."
    assert rows[0][:2] == (0.0, 5.0) and rows[-1][:2] == (5.0, 10.0), "Edges are low + i * width; the last right edge is high."


def test_all_equal_values():
    rows, outside = histogram_counts([4, 4, 4], bins=3)
    assert sum(r[2] for r in rows) == 3 and rows[0][2] == 3, "Width 0: put everything in the first bin instead of dividing by zero."


def test_errors():
    with pytest.raises(ValueError):
        histogram_counts([1, 2], bins=0)
    with pytest.raises(ValueError):
        histogram_counts([], bins=3)


def test_empty_with_a_range_gives_empty_bins():
    rows, outside = histogram_counts([], bins=2, low=0, high=4)
    assert rows == [(0.0, 2.0, 0), (2.0, 4.0, 0)] and outside == 0, "An empty list with an explicit range gives bins with count 0."


@pytest.mark.parametrize("seed", range(10))
def test_against_a_slow_version(seed):
    rng = random.Random(seed)
    bins = rng.choice([2, 4, 5, 10])
    data = [rng.randint(-5, 25) for _ in range(rng.randint(1, 80))]
    low, high = 0, 20
    rows, outside = histogram_counts(data, bins, low, high)
    for i, (left, right, count) in enumerate(rows):
        last = i == bins - 1
        slow = sum(1 for x in data if left <= x < right or (last and x == right))
        assert count == slow, f"Bin {i} [{left}, {right}): expected {slow}, got {count}."
    assert outside == sum(1 for x in data if x < low or x > high), "Wrong outside count."
