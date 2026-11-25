import random
import statistics

import pytest

from solution import mean, median, modes


def test_examples():
    assert mean([2, 4, 9]) == 5.0, "mean([2, 4, 9]) is 15 / 3 = 5.0."
    assert median([5, 1, 3]) == 3, "Sort first: [1, 3, 5], the middle is 3."
    assert median([4, 1, 3, 2]) == 2.5, "Even count: the mean of the two middle values (2 and 3) is 2.5."
    assert modes([1, 2, 2, 3, 3, 4]) == [2, 3], "Return every value tied for most frequent, sorted."
    assert modes([7, 7, 1]) == [7], "One mode: a list with one value."


def test_all_unique_means_all_tied():
    assert modes([3, 1, 2]) == [1, 2, 3], "If every value occurs once, they are all modes (sorted)."


def test_single_value():
    assert mean([4]) == 4 and median([4]) == 4 and modes([4]) == [4], "One value is its own mean, median and mode."


@pytest.mark.parametrize("fn", [mean, median, modes])
def test_empty_raises_a_clear_error(fn):
    with pytest.raises(ValueError, match="empty"):
        fn([])


@pytest.mark.parametrize("seed", range(50))
def test_against_statistics(seed):
    rng = random.Random(seed)
    data = [rng.randint(-20, 20) for _ in range(rng.randint(1, 40))]
    copy = list(data)
    assert mean(data) == pytest.approx(statistics.fmean(data), rel=1e-9), f"mean wrong for {data}"
    assert median(data) == pytest.approx(statistics.median(data), rel=1e-9), f"median wrong for {data}: sort first and handle even lengths"
    assert modes(data) == sorted(statistics.multimode(data)), f"modes wrong for {data}: return all tied values, sorted"
    assert data == copy, "You reordered the caller's list: use sorted(values), not values.sort()."
