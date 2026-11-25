import numpy as np
import pytest
from solution import cohens_d


def test_hand_example():
    assert cohens_d([4, 6, 8], [1, 3, 5]) == pytest.approx(1.5), "Means 6 and 3, both variances 4 (ddof=1), pooled sd 2: d = 1.5."


def test_unequal_sizes_weighted():
    a = np.array([10.0, 12, 14, 16, 18, 20])
    b = np.array([8.0, 12])
    sp = (((5 * a.var(ddof=1)) + (1 * b.var(ddof=1))) / 6) ** 0.5
    assert cohens_d(a, b) == pytest.approx((a.mean() - b.mean()) / sp), "Pool the variances with weights n - 1."


def test_equal_groups_and_sign():
    x = [3.0, 5.0, 9.0]
    assert cohens_d(x, x) == 0
    assert cohens_d([5, 6, 7], [1, 2, 3]) == pytest.approx(-cohens_d([1, 2, 3], [5, 6, 7])), "Swapping the groups flips the sign."
