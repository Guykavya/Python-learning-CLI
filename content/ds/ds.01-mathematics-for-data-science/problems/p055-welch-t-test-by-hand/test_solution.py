import math

import numpy as np
import pytest

from scipy import stats

from solution import welch_t

SF = lambda x, df: float(stats.t.sf(x, df))


def test_against_scipy_on_random_groups():
    rng = np.random.default_rng(50)
    for na, nb, sa, sb in [(10, 12, 1.0, 1.0), (8, 30, 1.0, 4.0), (40, 25, 2.0, 0.5)]:
        a, b = rng.normal(5, sa, na), rng.normal(5.7, sb, nb)
        ref = stats.ttest_ind(a, b, equal_var=False)
        t, df, p = welch_t(a, b, SF)
        assert t == pytest.approx(ref.statistic, abs=1e-9), "t = difference of means / sqrt(va/na + vb/nb), variances with ddof=1."
        assert p == pytest.approx(ref.pvalue, abs=1e-9), "two-sided p: 2 * P(T > |t|) with the Welch degrees of freedom."
        assert df == pytest.approx(ref.df, abs=1e-9), "Welch-Satterthwaite degrees of freedom (not na + nb - 2)."


def test_sign_and_symmetry():
    a, b = [5.1, 4.9, 5.3, 5.0], [4.2, 4.4, 4.0, 4.5]
    t, df, p = welch_t(a, b, SF)
    t2, df2, p2 = welch_t(b, a, SF)
    assert t > 0 and t2 == pytest.approx(-t), "swapping the groups flips the sign of t."
    assert p == pytest.approx(p2) and df == pytest.approx(df2), "the two-sided p-value and the df do not depend on the order."
    assert p < 0.01, "the groups are clearly different."


def test_identical_groups_have_p_one():
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    t, df, p = welch_t(x, list(x), SF)
    assert t == pytest.approx(0.0) and p == pytest.approx(1.0), "identical groups: t = 0 and p = 1."


def test_the_survival_function_is_used_with_abs_t():
    calls = []

    def spy(x, df):
        calls.append(x)
        return 0.25

    t, df, p = welch_t([1.0, 2.0, 3.0], [10.0, 11.0, 12.0], spy)
    assert calls and calls[0] > 0, "call t_sf with the absolute value of t (the tail beyond |t|)."
    assert p == pytest.approx(0.5), "p = 2 * t_sf(|t|, df): both tails."
