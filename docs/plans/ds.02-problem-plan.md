# Problem plan: ds.02 Statistical modelling (35 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.02.p001` … `p035`, folder `pNNN-slug`. Requires ds.01 and da.04
(NumPy, pandas, statsmodels, SciPy are all available).

**Mix:** 12 drill, 12 applied, 8 deep, 3 challenge. **Kinds:** 24 code, 7 trace, 4 explain.
**assessment:** explain = p012, trace = p009, fix = p022, build = p035.
**★ core set (write first, 14):** 1, 3, 5, 7, 9, 12, 13, 16, 19, 22, 25, 28, 31, 35 (fit → check assumptions → interpret: the learning outcome).

**Testing notes**
- Data come from the chapter's generators with a **known true model**: `make_wages(n, seed)` (§6.1) and `make_houses(n, seed)`
  (§19.2), copied into `conftest.py` as fixtures; the solution receives a DataFrame. Because the truth is known, tests check
  "the fit recovers the true slope within its 95% CI" instead of hard-coding a fitted number (R3).
- Hand-computed results (normal equations, R², standard errors) are compared with `statsmodels` (`sm.OLS(...).fit()`,
  `smf.ols`) with `rtol=1e-8`; that is the chapter's own §4.2 check.
- Functions that return a fitted model return the statsmodels results object; tests read `params`, `bse`, `conf_int()`,
  `model.exog_names` (so the forgotten constant is detectable: no `"const"`/`"Intercept"` in the names).
- statsmodels import ≈ 3 s, each fit on ≤ 1,200 rows takes milliseconds; keep coverage simulations ≤ 300 reps.
- No plots are checked; if a function makes a plot it saves to a `tmp_path` the test passes (Agg backend).
- Silence the expected `ConvergenceWarning`/`PerfectSeparationWarning` only in the separation problem, and check for it there.

## A. Regression from first principles (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Slope and intercept by formula | drill | code | `simple_fit(x, y)` with `cov/var`; matches `np.polyfit(x, y, 1)`; constant x raises `ValueError` |
| 2 | Residual sum of squares surface | drill | trace | `⚠ HAND-TRACE` `rss(b0, b1)` on 4 inline points for three candidate lines; print each RSS and which line is best |
| 3 | The normal equations | drill | code | `ols_coefs(X, y)` with an intercept column, solved with `np.linalg.solve(XᵀX, Xᵀy)`; equals `sm.OLS` params |
| 4 | Standard errors by hand | applied | code | `ols_se(X, y)` = `sqrt(diag(σ² (XᵀX)⁻¹))` with `σ² = RSS/(n−p)`; equals `result.bse`; message names `n−p`, not `n` |
| 5 | R² and adjusted R² by hand | drill | code | `r_squared(y, fitted, p)` returns both; equals `rsquared`, `rsquared_adj`; adding a junk column never lowers R² but can lower adjusted R² |

## B. statsmodels and its report (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | The forgotten constant | drill | code | `fit_ols(df, y, xs)` must include an intercept (`sm.add_constant`); test checks `"const"` in `exog_names` and the slope is unbiased on data with a big intercept |
| 7 | Read the coefficient table | drill | code | `coef_report(result, exponentiate=False)` (chapter §17.3): columns `estimate, ci_low, ci_high, p`; compare with `params`/`conf_int()` |
| 8 | What does each summary line mean? | drill | explain | label 8 numbers from a printed `summary()` (R², F p-value, coef, std err, t, P>|t|, Durbin-Watson, Jarque-Bera) with one sentence each; checklist in `answer.md` |
| 9 | Predict the summary numbers | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` for 5 inline points with an exact line, print slope, intercept, R² and residual df (exact values, worked on paper) |

## C. Formulas, categories, interactions, transforms (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Dummy coding by hand | drill | trace | `⚠ HAND-TRACE` given `dummies(series, baseline)` code, print the 0/1 columns for 5 inline rows with baseline `"school"` (column order is the sorted non-baseline levels)
| 11 | The formula interface | applied | code | `fit_wages(df)` = `log(wage) ~ experience + C(education) + C(city)` with `Treatment("school")`; recovers the true education effects (0.18, 0.40) within the CIs |
| 12 | Explain a coefficient in words | deep | explain | `assessment = "explain"`; the master phrase (§7.1) for four coefficients: level-level, log-level (≈ % change, exact `100(e^b − 1)`), log-log (elasticity), a dummy (difference from baseline); checklist in `answer.md` |
| 13 | Percent effect from a log model | deep | trace | `⚠ HAND-TRACE` print `b`, the approximation `100b` and the exact `100(e^b − 1)` to 2 decimals for b = 0.02, 0.10, 0.40, −0.40; shows where the shortcut breaks
| 14 | An interaction term | applied | code | `experience_slope_by_education(df)` fits `experience * C(education)` and returns the slope for each level; masters ≈ 0.035, others ≈ 0.025 (within CI) |
| 15 | Trace dummy coefficients | drill | trace | `⚠ HAND-TRACE` given fitted coefficients for `C(city)` (inline numbers), print the predicted log-wage for each city at experience 10 |
| 16 | Standardised coefficients | applied | code | `standardised_coefs(df, y, xs)` (z-score all variables, refit); equals `b · sd(x)/sd(y)` |

## D. Assumptions and diagnostics (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Coverage when an assumption breaks | challenge | code | `slope_ci_coverage(world, n, reps, seed)` for `"ok"`, `"hetero"`, `"dependent"` worlds; ok ≈ 0.95, hetero clearly lower (< 0.90) with ordinary SEs |
| 18 | Residuals versus fitted, as numbers | deep | code | `funnel_ratio(result)` = spread of residuals in the top third of fitted values / bottom third; > 2 on heteroscedastic data, ≈ 1 otherwise |
| 19 | Leverage and Cook's distance | applied | code | `influential_points(result, threshold=4/n)` returns row indices; the planted bad point is found; equals `get_influence().cooks_distance[0]` ranking |
| 20 | Variance inflation factors | drill | code | `vif_table(df, predictors)` by regressing each predictor on the others (`1/(1−R²)`); equals `variance_inflation_factor`; near-duplicate column → VIF > 10 |
| 21 | Breusch-Pagan and robust errors | deep | code | `hetero_check(result)` returns the BP p-value and the HC3 standard errors (`get_robustcov_results("HC3")` or `fit(cov_type="HC3")`); p < 0.01 on hetero data; robust SE larger than ordinary |
| 22 | Fix the diagnostics report | applied | code | `assessment = "fix"`; given a `diagnose(result)` (§18) with three bugs: Cook's threshold uses `p/n`, VIF loop includes the constant, Durbin-Watson read from the wrong attribute; tests compare each field with statsmodels |
| 23 | Which assumption is broken? | deep | trace | `⚠ HAND-TRACE` four small diagnostic summaries (funnel ratio, DW, max Cook's, JB p) printed by given code; the learner writes the label the given rule prints for each |

## E. Intervals, overfitting, omitted variables (Ch. 10–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Confidence versus prediction interval | applied | explain | which interval to quote for one new house versus the average house of that size, and why the prediction interval never shrinks to zero with more data; checklist: "mean response", "plus residual variance", "σ does not shrink with n" (uses `get_prediction().summary_frame()` output printed in `problem.md`)
| 25 | A held-out check | applied | code | `holdout_rmse(df, formula, test_frac, seed)` with `train_test_split_idx` (§10/§11); RMSE on test ≥ on train for a model with 20 junk predictors (the `overfit_demo` lesson) |
| 26 | Omitted-variable bias | deep | code | `omitted_bias(seed)` simulates a confounder; the short regression's slope moves by `β_z · cov(x,z)/var(x)` (formula vs fit within 10%) |
| 27 | Correlation is not causation | deep | explain | the §12.3 case (ice-cream and drownings style synthetic data): why controlling for the confounder changes the slope, and when adding a variable is harmful (a collider/mediator); checklist |

## F. Logistic, GLMs, counts, comparing models (Ch. 13–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | Logistic regression by maximum likelihood | applied | code | `fit_logit(X, y)` with Newton or `scipy.optimize.minimize` on `neg_loglik`; equals `sm.Logit(...).fit(disp=0).params` within 1e-4 |
| 29 | Odds ratios with intervals | applied | code | `odds_ratios(result)` = `coef_report(..., exponentiate=True)`; CI excludes 1 for a true effect |
| 30 | Odds, log-odds and probability | drill | trace | `⚠ HAND-TRACE` convert p = 0.2, 0.5, 0.8 to odds and log-odds and back; print to 3 decimals |
| 31 | Confusion matrix at a threshold | drill | code | `confusion_at(y, p, threshold)` returns TP, FP, FN, TN; threshold 0 and 1 edge cases |
| 32 | The separation trap | deep | code | `safe_logit(X, y)` detects perfect separation (statsmodels warning/exception or huge coefficients) and returns `None` with a reason string; tested on a separable and a normal dataset |
| 33 | Poisson regression with exposure | applied | code | `rate_model(df)` with `offset=np.log(df.exposure)`; recovers the true rate ratio; without the offset the estimate is biased (test checks both) |
| 34 | Overdispersion and AIC | challenge | code | `choose_count_model(df)` fits Poisson and NegativeBinomial GLMs, returns the dispersion ratio (Pearson χ²/df) and the name with the lower AIC; NB wins on overdispersed data, Poisson on Poisson data. Also `lr_test(big, small)` (§16.1) matches `scipy.stats.chi2.sf` |

## G. Project (Ch. 17–19)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | House-price study | challenge | code | `assessment = "build"`; `house_study(df)` returns a dict: the main log-price model (`np.log(price) ~ np.log(area/1000) + bedrooms + bathrooms + age + C(locality) + parking`), its max VIF, the area elasticity with CI (contains the true 0.85), Breusch-Pagan p, and held-out RMSE; tests use `make_houses(1200, 2025)` and two other seeds |

## Counts check

Tiers: drill 12 (1, 2, 3, 5, 6, 7, 8, 10, 15, 20, 30, 31), applied 12 (4, 9, 11, 14, 16, 19, 22, 24, 25, 28, 29, 33),
deep 8 (12, 13, 18, 21, 23, 26, 27, 32), challenge 3 (17, 34, 35).
Kinds: trace 7 (2, 9, 10, 13, 15, 23, 30), explain 4 (8, 12, 24, 27), code 24.
Assessment: explain p012, trace p009, fix p022, build p035 — exactly one each.

## Risks and open questions

- statsmodels output names (`Intercept` vs `const`) differ between the formula and array interfaces; tests accept both and the
  message says which interface was expected.
- NegativeBinomial GLM needs an `alpha`; use `smf.negativebinomial` (estimates alpha) or fix alpha = 1 and say so in `problem.md`.
- Separation behaviour changed across statsmodels versions (warning vs `PerfectSeparationError`); p032 must accept either.
