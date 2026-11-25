import numpy as np
import pytest
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

from conftest import make_houses
from solution import house_study

FORMULA = ("np.log(price_lakh) ~ np.log(area_sqft / 1000) + bedrooms + bathrooms"
           " + age_years + C(locality) + parking")
AREA = "np.log(area_sqft / 1000)"
SEEDS = [2025, 1, 2]


@pytest.fixture(scope="module", params=SEEDS)
def case(request):
    df = make_houses(1200, request.param)
    return df, house_study(df)


def test_keys(case):
    _, out = case
    assert set(out) == {"n_dropped", "n_used", "elasticity", "elasticity_ci", "max_vif", "bp_p", "holdout_rmse", "outliers"}, f"keys must be exactly the eight documented ones, got {sorted(out)}."


def test_cleaning_removes_only_the_impossible_row(case):
    df, out = case
    assert out["n_dropped"] == 1 and out["n_used"] == 1199, "exactly one row has area_sqft > 4000 (the extra zero); do not drop anything else."
    assert 940 in out["outliers"], "the luxury flat (row 940) is genuine: keep it in the fit, and report it as an outlier."


def test_elasticity_matches_a_direct_fit_and_contains_the_truth(case):
    df, out = case
    res = smf.ols(FORMULA, data=df[df.area_sqft <= 4000]).fit()
    assert out["elasticity"] == pytest.approx(res.params[AREA], rel=1e-8), "elasticity = coefficient of np.log(area_sqft / 1000) in the cleaned fit."
    lo, hi = out["elasticity_ci"]
    assert (lo, hi) == pytest.approx(tuple(res.conf_int().loc[AREA]), rel=1e-8), "elasticity_ci = the 95% interval of that coefficient."
    assert lo < 0.85 < hi, f"({lo:.3f}, {hi:.3f}) should contain the true elasticity 0.85 once the impossible row is gone."


def test_diagnostics_match_statsmodels(case):
    df, out = case
    res = smf.ols(FORMULA, data=df[df.area_sqft <= 4000]).fit()
    exog = res.model.exog
    names = list(res.model.exog_names)
    expected_vif = max(variance_inflation_factor(exog, i) for i, n in enumerate(names) if n != "Intercept")
    assert out["max_vif"] == pytest.approx(expected_vif, rel=1e-8), "max_vif: leave the intercept column out."
    assert out["bp_p"] == pytest.approx(het_breuschpagan(res.resid, exog)[1], rel=1e-8), "bp_p: Breusch-Pagan LM p-value of the cleaned fit."
    assert out["max_vif"] < 10, "the house model has no serious collinearity."


def test_holdout_error_is_near_the_noise_level(case):
    df, out = case
    clean = df[df.area_sqft <= 4000]
    n = len(clean)
    idx = np.random.default_rng(0).permutation(n)
    cut = int(n * 0.75)
    train, test = clean.iloc[idx[:cut]], clean.iloc[idx[cut:]]
    fit = smf.ols(FORMULA, data=train).fit()
    expected = float(np.sqrt(np.mean((np.log(test["price_lakh"]) - fit.predict(test)) ** 2)))
    assert out["holdout_rmse"] == pytest.approx(expected, rel=1e-8), "holdout: permutation(n) with seed 0, first 75% fit, last 25% evaluate, error on the log scale."
    assert 0.15 < out["holdout_rmse"] < 0.30, "the true noise sd is 0.18 on the log scale."


def test_outliers_are_sorted_labels(case):
    _, out = case
    assert out["outliers"] == sorted(out["outliers"]), "sorted ascending."
    assert all(isinstance(i, int) for i in out["outliers"]), "plain ints."
