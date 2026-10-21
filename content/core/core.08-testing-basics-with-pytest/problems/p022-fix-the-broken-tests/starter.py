import pytest

from target import median


def test_median_odd():
    assert median([3, 1, 2]) == 2


def test_median_even():
    assert median([1, 2, 3, 4]) == 2


def test_median_odd():
    assert median([9, 7, 8, 10, 6]) == 8


def test_single():
    assert (median([5]) == 5, "one number is its own median")


def test_unsorted():
    median([5, 1, 4])


def test_empty():
    with pytest.raises(ValueError):
        median([1])
        median([])


def tset_negative():
    assert median([-5, -1, -3]) == -3
