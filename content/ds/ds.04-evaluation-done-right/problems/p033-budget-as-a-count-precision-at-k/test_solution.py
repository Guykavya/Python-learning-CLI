import numpy as np
import pytest

from solution import at_k

Y = [1, 0, 1, 0, 0, 1]
S = [0.9, 0.8, 0.8, 0.3, 0.2, 0.1]


def test_ties_by_original_order():
    p, r = at_k(Y, S, 2)
    assert p == pytest.approx(0.5) and r == pytest.approx(1 / 3), "top 2 = rows 0 and 1 (row 1 is earlier than row 2 on the 0.8 tie)."


def test_k_three():
    p, r = at_k(Y, S, 3)
    assert p == pytest.approx(2 / 3) and r == pytest.approx(2 / 3), "top 3 = rows 0, 1, 2: two positives of three, two of the three positives."


def test_all_rows_and_no_positives():
    assert at_k(Y, S, 6) == pytest.approx((0.5, 1.0)), "k = n: precision is the base rate, recall is 1."
    assert at_k([0, 0, 0], [0.3, 0.2, 0.1], 2) == (0.0, 0.0), "no positives: precision 0, recall 0."


def test_bad_k():
    with pytest.raises(ValueError):
        at_k(Y, S, 0)
    with pytest.raises(ValueError):
        at_k(Y, S, 7)


def test_matches_a_slow_version():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 300)
    s = np.round(rng.random(300), 1)                 # many ties
    for k in (10, 50, 200):
        idx = sorted(range(300), key=lambda i: (-s[i], i))[:k]
        p, r = at_k(y, s, k)
        assert p == pytest.approx(y[idx].mean()) and r == pytest.approx(y[idx].sum() / y.sum()), f"k = {k}: top rows by score, earlier rows first on ties."
