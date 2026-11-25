import math

import statsmodels.formula.api as smf


def sig_round(value, ref):
    if ref == 0 or not math.isfinite(ref):
        return f"{value:,.0f}"
    decimals = max(0, 1 - math.floor(math.log10(abs(ref))))
    return f"{round(value, decimals):,.{decimals}f}"


def redo(study_df, mei):
    d = study_df.assign(app_i=study_df["app"].astype(int))
    naive = d.loc[d.app_i == 1, "spend"].mean() - d.loc[d.app_i == 0, "spend"].mean()
    fit = smf.ols("spend ~ app_i + engagement + age + C(city)", data=d).fit(cov_type="HC3")
    est, se = float(fit.params["app_i"]), float(fit.bse["app_i"])
    lo, hi = (float(v) for v in fit.conf_int().loc["app_i"])
    if lo > mei:
        verdict = "worth it: the whole interval is above the minimum effect"
    elif hi < mei:
        verdict = "not worth it: the whole interval is below the minimum effect"
    else:
        verdict = "inconclusive: the interval contains the minimum effect"
    report = (f"Adjusted for engagement, age and city, app users spend {sig_round(est, se)} rupees more "
              f"(95% CI {sig_round(lo, se)} to {sig_round(hi, se)}). This is an observational comparison: "
              f"an unmeasured confounder could still bias it.")
    return {"naive_diff": float(naive), "adjusted_diff": est, "ci": (lo, hi), "verdict": verdict, "report": report}
