import random
import statistics

import pytest

from solution import describe_spread


def test_hand_checked_example():
    got = describe_spread([2, 4, 4, 4, 5, 5, 7, 9])
    assert got["range"] == 7, "range is max - min = 9 - 2."
    assert got["sd"] == pytest.approx(statistics.stdev([2, 4, 4, 4, 5, 5, 7, 9]), rel=1e-9), "sd is the SAMPLE standard deviation (n - 1)."
    assert got["iqr"] == pytest.approx(1.5, rel=1e-9), "Inclusive quartiles (0-based positions (n-1)*p/100 = 1.75 and 5.25) are 4.0 and 5.5, so the IQR is 1.5."
    assert got["mad"] == pytest.approx(0.5, rel=1e-9), "The median is 4.5; the absolute deviations are 2.5, .5, .5, .5, .5, .5, 2.5, 4.5 and their median is 0.5."
    assert got["cv"] == pytest.approx(got["sd"] / 5.0, rel=1e-9), "cv = sd / mean, the mean here is 5."


def test_keys():
    got = describe_spread([1, 2, 3])
    assert set(got) == {"range", "sd", "iqr", "mad", "cv"}, "Return exactly the five keys range, sd, iqr, mad, cv."


def test_zero_mean_gives_none_cv():
    assert describe_spread([-1, 0, 1])["cv"] is None, "A mean of 0 makes cv undefined: return None."


def test_too_few_values():
    with pytest.raises(ValueError):
        describe_spread([5])


def test_no_mutation():
    data = [5, 3, 9, 1]
    describe_spread(data)
    assert data == [5, 3, 9, 1], "Do not sort the caller's list in place."


@pytest.mark.parametrize("seed", range(10))
def test_against_statistics(seed):
    rng = random.Random(seed)
    data = [rng.gauss(100, 15) for _ in range(rng.randint(5, 60))]
    got = describe_spread(data)
    q1, _, q3 = statistics.quantiles(data, n=4, method="inclusive")
    med = statistics.median(data)
    assert got["iqr"] == pytest.approx(q3 - q1, rel=1e-9), "iqr must use the inclusive quartile method."
    assert got["mad"] == pytest.approx(statistics.median([abs(x - med) for x in data]), rel=1e-9), "mad is the median of |x - median|."
    assert got["sd"] == pytest.approx(statistics.stdev(data), rel=1e-9), "sd is the sample sd."


@pytest.mark.parametrize("seed", range(5))
def test_one_huge_value_moves_sd_but_not_iqr_or_mad(seed):
    rng = random.Random(seed)
    data = [rng.gauss(100, 5) for _ in range(41)]
    before = describe_spread(data)
    after = describe_spread(data + [10_000])
    assert after["sd"] > 10 * before["sd"], "sd should explode when one huge value arrives (it uses every value)."
    assert after["range"] > 100 * before["range"], "range should explode too."
    assert after["iqr"] < 1.15 * before["iqr"] + 1e-9, "iqr should barely move: it is built from the middle of the sorted data."
    assert after["mad"] < 1.15 * before["mad"] + 1e-9, "mad should barely move: it is a median."
