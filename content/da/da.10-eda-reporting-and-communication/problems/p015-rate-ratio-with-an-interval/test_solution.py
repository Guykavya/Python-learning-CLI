import numpy as np
import pandas as pd
import pytest

from solution import rate_ratio


def test_hand_example():
    rr, lo, hi = rate_ratio(20, 1000, 10, 1000)
    assert rr == pytest.approx(2.0), "rr = (20/1000) / (10/1000) = 2."
    assert (round(lo, 3), round(hi, 3)) == (0.941, 4.251), f"95% CI on the log scale: 0.941 to 4.251, got {lo:.3f} to {hi:.3f}"


def test_interval_is_not_symmetric():
    rr, lo, hi = rate_ratio(20, 1000, 10, 1000)
    assert hi - rr > rr - lo, "on the log scale the interval stretches further above rr than below it."
    assert lo * hi == pytest.approx(rr * rr), "the interval is symmetric around rr on the LOG scale: lo x hi = rr squared."


def test_chapter_numbers():
    rr, lo, hi = rate_ratio(1997, 94313, 1905, 243463)
    assert rr == pytest.approx(2.706, abs=1e-3), f"the chapter's 'all weeks' row has a rate ratio of about 2.71, got {rr:.3f}"
    assert 2.5 < lo < rr < hi < 2.9


def test_returns_plain_floats():
    out = rate_ratio(5, 50, 5, 100)
    assert all(type(v) is float for v in out), "return three Python floats."


@pytest.mark.parametrize("args", [(0, 100, 5, 100), (5, 100, 0, 100)])
def test_zero_events(args):
    with pytest.raises(ValueError, match="need at least one event in each group"):
        rate_ratio(*args)


def test_impossible_counts():
    with pytest.raises(ValueError, match="events cannot exceed the group size"):
        rate_ratio(120, 100, 5, 100)
