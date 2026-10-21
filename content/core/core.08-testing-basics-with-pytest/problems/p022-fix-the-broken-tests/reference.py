import pytest

from target import median


def test_median_odd():
    assert median([3, 1, 2]) == 2, "The middle of 1, 2, 3 is 2."


def test_median_odd_longer():
    assert median([9, 7, 8, 10, 6]) == 8, "Sorted: 6 7 8 9 10, the middle is 8."


def test_median_even():
    assert median([1, 2, 3, 4]) == 2.5, "Even count: the mean of the two middle values, (2 + 3) / 2."


def test_single():
    assert median([5]) == 5, "One number is its own median."


def test_unsorted():
    assert median([5, 1, 4]) == 4, "The input is not sorted: sort first. Sorted it is 1 4 5."


def test_empty():
    with pytest.raises(ValueError):
        median([])


def test_negative():
    assert median([-5, -1, -3]) == -3, "Sorted: -5 -3 -1, the middle is -3."
