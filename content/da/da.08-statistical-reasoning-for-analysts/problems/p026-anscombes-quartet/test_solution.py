import pytest
from solution import looks_linear, pair_summary

X = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
Y1 = [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]
Y2 = [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]
Y3 = [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]
X4 = [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8]
Y4 = [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]
SETS = [(X, Y1), (X, Y2), (X, Y3), (X4, Y4)]


@pytest.mark.parametrize("x,y", SETS)
def test_identical_summaries(x, y):
    mx, my, vx, r, slope, icpt = pair_summary(x, y)
    assert mx == pytest.approx(9.0) and my == pytest.approx(7.50, abs=0.01), "Means 9.0 and 7.50."
    assert vx == pytest.approx(11.0), "Sample variance of x (ddof=1) is 11.0."
    assert r == pytest.approx(0.816, abs=0.002), "r = 0.816 for all four sets: the summary cannot tell them apart."
    assert slope == pytest.approx(0.5, abs=0.005) and icpt == pytest.approx(3.0, abs=0.01)


def test_only_set_one_looks_linear():
    got = [looks_linear(x, y) for x, y in SETS]
    assert got == [True, False, False, False], f"Set 1 is a line; set 2 curves, set 3 has an outlier, set 4 hangs on one point. You returned {got}."


def test_perfect_line_is_linear():
    assert looks_linear([1, 2, 3, 4, 5, 6], [2, 4, 6, 8, 10, 12.0]) in (True,), "A perfect line is linear (zero residuals must not crash)."


def test_bad_input():
    with pytest.raises(ValueError):
        pair_summary([1, 1, 1], [1, 2, 3])
    with pytest.raises(ValueError):
        looks_linear([1, 2], [3, 4])
