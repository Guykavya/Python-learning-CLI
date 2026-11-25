import pytest
from solution import diff_prop_ci


def test_hand_example():
    d, (lo, hi) = diff_prop_ci(130, 1000, 100, 1000)
    assert d == pytest.approx(0.03), "p1 - p2 = 0.13 - 0.10."
    assert lo == pytest.approx(0.0021, abs=1e-4) and hi == pytest.approx(0.0579, abs=1e-4), \
        "SE = sqrt(0.13*0.87/1000 + 0.10*0.90/1000) = 0.01425; interval 0.03 +- 1.96 * SE."


def test_order_flips_the_sign():
    d1, (l1, h1) = diff_prop_ci(130, 1000, 100, 1000)
    d2, (l2, h2) = diff_prop_ci(100, 1000, 130, 1000)
    assert d2 == pytest.approx(-d1) and l2 == pytest.approx(-h1) and h2 == pytest.approx(-l1), "Swapping the groups negates the difference and mirrors the interval."


def test_different_group_sizes_and_z():
    d, (lo, hi) = diff_prop_ci(30, 200, 90, 600, z=2.576)
    assert d == pytest.approx(0.0), "30/200 = 90/600 = 0.15."
    se = (0.15 * 0.85 / 200 + 0.15 * 0.85 / 600) ** 0.5
    assert hi == pytest.approx(2.576 * se) and lo == pytest.approx(-2.576 * se), "Use the z argument."
