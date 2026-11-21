import math

import pytest

from solution import quantile, summary

INF = float("inf")
SKEWED = [(0.05, 80), (0.1, 90), (0.25, 95), (0.5, 97), (1.0, 99), (5.0, 100), (INF, 100)]


def test_median_is_interpolated_inside_the_first_bucket():
    assert quantile(0.5, SKEWED) == pytest.approx(0.03125), \
        "rank 50 falls in the first bucket (0 to 0.05, 80 requests): 0 + 0.05 * 50 / 80 = 0.03125. The lower bound of the first bucket is 0."


def test_p95():
    assert quantile(0.95, SKEWED) == pytest.approx(0.25), \
        "rank 95: the first bucket with count >= 95 is (0.25, 95); interpolate from the previous bucket (0.1, 90): 0.1 + 0.15 * 5/5 = 0.25."


def test_p99():
    assert quantile(0.99, SKEWED) == pytest.approx(1.0), "rank 99 lands exactly on the (1.0, 99) bucket: 0.5 + 0.5 * 2/2 = 1.0."


def test_interpolation_between_bounds():
    assert quantile(0.999, SKEWED) == pytest.approx(4.6), "rank 99.9 is in (5.0, 100): 1.0 + 4.0 * (99.9 - 99) / (100 - 99) = 4.6."
    assert quantile(0.92, SKEWED) == pytest.approx(0.1 + 0.15 * (92 - 90) / (95 - 90)), "Linear interpolation inside the bucket (0.1, 0.25]."


def test_q_one():
    assert quantile(1.0, SKEWED) == pytest.approx(5.0), "q=1 is the upper bound of the bucket that holds the last request."


def test_the_inf_bucket_returns_the_highest_finite_bound():
    buckets = [(0.1, 50), (1.0, 90), (INF, 100)]
    assert quantile(0.95, buckets) == 1.0, "rank 95 is beyond the last finite bucket: the histogram cannot say more than 'above 1.0'; return 1.0."
    assert quantile(0.5, buckets) == pytest.approx(0.1), "rank 50 is exactly the first bucket's count: 0 + 0.1 * 50/50 = 0.1."


def test_empty_histogram():
    assert math.isnan(quantile(0.9, [(1.0, 0), (INF, 0)])), "No observations: nan."


def test_empty_buckets_in_the_middle_are_skipped_correctly():
    buckets = [(0.1, 10), (0.5, 10), (1.0, 20), (INF, 20)]
    assert quantile(0.75, buckets) == pytest.approx(0.5 + 0.5 * (15 - 10) / (20 - 10)), \
        "rank 15: the first bucket with count >= 15 is (1.0, 20), whose lower bound is the previous le 0.5 with 10 before it."


def test_single_bucket_histogram():
    assert quantile(0.5, [(1.0, 10), (INF, 10)]) == pytest.approx(0.5), "One finite bucket from 0: rank 5 of 10 = halfway = 0.5."


@pytest.mark.parametrize("q", [0, -0.1, 1.01, 2])
def test_bad_q(q):
    with pytest.raises(ValueError):
        quantile(q, SKEWED)


@pytest.mark.parametrize("buckets", [
    [(0.1, 5), (1.0, 3), (INF, 5)],
    [(1.0, 5), (0.1, 6), (INF, 6)],
    [(0.1, 5), (0.1, 6), (INF, 6)],
    [(0.1, 5), (1.0, 6)],
    [],
])
def test_bad_buckets(buckets):
    with pytest.raises(ValueError):
        quantile(0.5, buckets)


def test_summary_shows_why_the_mean_hides_the_tail():
    s = summary(SKEWED, 8.0)
    assert s["mean"] == pytest.approx(0.08), "mean = 8.0 seconds / 100 requests = 0.08."
    assert (s["p50"], s["p95"], s["p99"]) == pytest.approx((0.03125, 0.25, 1.0))
    assert s["p99"] > 10 * s["mean"], "The average (80 ms) looks healthy while one request in a hundred takes a second: the tail needs percentiles."


def test_summary_of_nothing():
    s = summary([(1.0, 0), (INF, 0)], 0.0)
    assert s["mean"] == 0.0 and math.isnan(s["p99"]), "No requests: mean 0.0 (not a ZeroDivisionError) and nan percentiles."
