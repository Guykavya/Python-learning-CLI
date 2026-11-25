import pytest
import statsmodels.formula.api as smf
from solution import adjusted_effect


def test_matches_a_direct_fit(world_factory):
    w = world_factory(n=3000, tau=150, seed=11)
    fit = smf.ols("spend ~ app_i + engagement + income", data=w.assign(app_i=w["app"].astype(int))).fit()
    lo, hi = fit.conf_int().loc["app_i"]
    coef, a, b = adjusted_effect(w)
    assert coef == pytest.approx(fit.params["app_i"]) and a == pytest.approx(lo) and b == pytest.approx(hi), \
        "Return the coefficient of app and its 95% CI from spend ~ app_i + engagement + income."


def test_ci_contains_the_truth_and_naive_does_not(world_factory):
    hits = 0
    for seed in range(5):
        w = world_factory(n=4000, tau=150, seed=60 + seed)
        coef, lo, hi = adjusted_effect(w)
        hits += lo <= 150 <= hi
        naive = w.loc[w.app, "spend"].mean() - w.loc[~w.app, "spend"].mean()
        assert not (lo <= naive <= hi), "The naive difference is far outside the adjusted interval."
        assert abs(coef - 150) < 80, "The adjusted coefficient should be near the true effect 150."
    assert hits >= 4, f"The 95% interval should contain the true effect 150 in about 95% of worlds (got {hits} of 5): did you include both engagement and income?"


def test_returns_three_floats(world_factory):
    r = adjusted_effect(world_factory(n=500, seed=1))
    assert len(r) == 3 and all(isinstance(v, float) for v in r) and r[1] < r[0] < r[2]
