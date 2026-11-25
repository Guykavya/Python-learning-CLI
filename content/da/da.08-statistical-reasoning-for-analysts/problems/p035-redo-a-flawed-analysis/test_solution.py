import math

import pytest
import statsmodels.formula.api as smf
from solution import redo

TRUE = 120
WORTH = "worth it: the whole interval is above the minimum effect"
NOT = "not worth it: the whole interval is below the minimum effect"
INC = "inconclusive: the interval contains the minimum effect"


def sig(value, ref):
    d = max(0, 1 - math.floor(math.log10(abs(ref))))
    return f"{round(value, d):,.{d}f}"


def direct(df):
    d = df.assign(app_i=df["app"].astype(int))
    fit = smf.ols("spend ~ app_i + engagement + age + C(city)", data=d).fit(cov_type="HC3")
    return fit, d


def test_numbers_match_a_direct_fit(study_factory):
    df = study_factory(seed=3)
    fit, d = direct(df)
    r = redo(df, 50)
    lo, hi = fit.conf_int().loc["app_i"]
    assert set(r) == {"naive_diff", "adjusted_diff", "ci", "verdict", "report"}, "Keys: naive_diff, adjusted_diff, ci, verdict, report."
    assert r["adjusted_diff"] == pytest.approx(fit.params["app_i"]) and tuple(r["ci"]) == pytest.approx((lo, hi)), \
        "Adjusted effect and CI: OLS spend ~ app_i + engagement + age + C(city), cov_type='HC3'."
    assert r["naive_diff"] == pytest.approx(d.loc[d.app_i == 1, "spend"].mean() - d.loc[d.app_i == 0, "spend"].mean())


def test_adjusted_interval_catches_the_truth_naive_does_not(study_factory):
    hits = 0
    for seed in range(5):
        r = redo(study_factory(seed=100 + seed), 50)
        lo, hi = r["ci"]
        hits += lo <= TRUE <= hi
        assert r["naive_diff"] > 2 * TRUE, "The naive difference is badly inflated by confounding (engagement)."
        assert not (lo <= r["naive_diff"] <= hi), "The naive number lies far outside the adjusted interval."
    assert hits >= 4, f"The adjusted 95% interval should contain the true effect (120) in about 95% of studies; got {hits} of 5."


@pytest.mark.parametrize("mei,label", [(50, WORTH), (500, NOT), (120, INC)])
def test_verdict_is_consistent_with_the_interval(study_factory, mei, label):
    r = redo(study_factory(seed=7), mei)
    lo, hi = r["ci"]
    want = WORTH if lo > mei else NOT if hi < mei else INC
    assert r["verdict"] == want, f"With CI ({lo:.0f}, {hi:.0f}) and mei {mei} the label is: {want}"
    assert want == label, "Test self-check: pick an interval that gives the intended label."


def test_report_contains_numbers_and_caveats(study_factory):
    df = study_factory(seed=9)
    fit, _ = direct(df)
    r = redo(df, 50)
    se = fit.bse["app_i"]
    lo, hi = fit.conf_int().loc["app_i"]
    text = r["report"]
    for v in (fit.params["app_i"], lo, hi):
        assert sig(v, se) in text, f"The report must contain {sig(v, se)} (value rounded with sig_round(value, SE))."
    assert "observational" in text and "confounder" in text, "Say that the comparison is observational and mention the confounder."
