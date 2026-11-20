# Problem plan: da.08 Statistical reasoning for analysts (35 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.08.p001`…`p035`, folder `pNNN-slug`.

**Mix:** 11 drill, 13 applied, 8 deep, 3 challenge. **Kinds:** 25 code, 6 trace, 4 explain.
**assessment:** explain = p017, trace = p020, fix = p009, build = p035.
**★ core set (14):** p001, p002, p005, p007, p009, p010, p011, p012, p017, p018, p025, p029, p030, p035.

**Testing notes**
- Libraries: numpy, pandas, scipy.stats, statsmodels (the chapter imports all four). Spiked 2026-11-18 under the
  runner's limits: numpy+pandas+scipy+statsmodels.formula import, 5 × 1,000 t-intervals, a 5,000-resample bootstrap
  and an OLS on 20,000 rows took **2.7 s, 219 MB** in total.
- **`OMP_NUM_THREADS=2` matters:** importing matplotlib+seaborn+pandas+plotly+scipy+statsmodels under the 1 GiB cap
  without it raised `MemoryError` (OpenBLAS threads); with it, fine. The runner sets it; if you run pytest by hand
  under `ulimit -v`, set it too.
- **Randomness goes in as an argument:** every function that samples takes `rng` (`np.random.default_rng(seed)`).
  Tests check *properties* (R3), never a hard-coded number from a random draw. Measured spread to size thresholds:
  t-interval coverage on exponential data, n = 40, 1,000 reps, seeds 0–4: 0.923–0.944. So coverage tests accept
  **[0.90, 0.975]** on normal data and use the wrong version (sd instead of SE) to show the failure (~1.0).
- Subtle formula errors (z instead of t, ddof=0) do not show in a simulation; catch them with a **direct comparison
  at small n** against `scipy.stats.t.interval`, `statsmodels.stats.proportion.proportion_confint` etc.
- Chapter functions reused as fixed specs (quote them in `problem.md`): `ci_mean` (§4.2), `bootstrap_ci` (§4.5),
  `diff_prop_ci` (§4.6), `power` (§5.5), `cohens_d`, `verdict` (§6.2, exact three label strings), `sig_round`,
  `report_mean` (§9.1, exact string format, e.g. `Mean monthly spend: 2,578 rupees (95% CI 2,453 to 2,702; n = 500)`),
  `make_app_world` (§8.3), `make_study` (§10.1). Tests that need a world generator carry a **small** copy of it
  (n ≤ 5,000) in `conftest.py`; the learner receives the DataFrame as an argument.

## A. Populations, samples, sampling variation (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Standard error of a mean | drill | code | `standard_error(x)` = s/√n with `ddof=1`; equals `scipy.stats.sem`; n = 2; constant data → 0; n = 1 → `ValueError` ("one value has no spread") |
| 2 | Draw many samples | applied | code | `sample_means(pop, n, reps, rng)` → array of means; same seed → same result (no global `np.random`); mean of means within 2% of the population mean; their sd within 15% of σ/√n |
| 3 | How fast does the SE shrink? | drill | trace | `⚠ HAND-TRACE` prints SE for sd = 20 and n = 25, 100, 400, 1600 with `:.2f` (4.00, 2.00, 1.00, 0.50) and the line "to halve the SE, multiply n by 4" |
| 4 | Law of large numbers or CLT? | drill | explain | separate the two ideas; answer.md checklist: "the average settles near the true mean" / "the *shape* of the sampling distribution becomes normal" / "n is the sample size, not the population size" / "skewed data needs a larger n" |

## B. Sampling bias (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Precision is not accuracy | applied | code | `bias_spread_rmse(estimates, truth)` → `(bias, sd, rmse)` with `ddof=0`; test checks `rmse**2 == bias**2 + sd**2` (approx) and a hand example; message for using ddof=1 |
| 6 | Survivorship bias with numbers | applied | trace | `⚠ HAND-TRACE` 10 shops in an inline list, 4 closed; code prints mean growth of survivors and of all shops (`:.1f`) and the gap |
| 7 | Post-stratification weights | applied | code | `weighted_mean(sample_df, value, by, pop_shares)`; hand-computed inline example; a stratum in `pop_shares` missing from the sample → `ValueError` naming it; shares not summing to 1 → `ValueError` |
| 8 | Name the bias | drill | explain | six short scenarios → selection, non-response, survivorship, voluntary response, measurement, convenience; answer.md lists the label and the one-line reason for each |
| 9 | Fix the biased sampler | deep | code | `assessment = "fix"`; given `draw(pop, n, rng)` that takes the first n rows of a table sorted by signup date (the §3.1 trap) plus an off-by-one that repeats a row; fix to `rng.choice(len(pop), n, replace=False)`. Tests: no duplicate rows; over 200 seeds the mean estimate is within 1% of the truth (the buggy one is ~8% off, message says "your sample is not random: it depends on row order") |

## C. Confidence intervals (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | t interval for a mean | drill | code | `ci_mean(x, level=0.95)` equals `scipy.stats.t.interval` at n = 5 and 30 (catches z instead of t: message "with n = 5 the t quantile is 2.78, not 1.96"); level 0.90 |
| 11 | What "95 percent" means: coverage | applied | code | `coverage(ci_fn, sampler, truth, reps, rng)` → share of intervals containing `truth`; test: reference `ci_mean` on normal data → in [0.90, 0.975]; a deliberately wrong ci (sd instead of SE) → > 0.99. Never a hard-coded share |
| 12 | Wilson interval for a proportion | applied | code | `wilson(k, n, level)` equals `proportion_confint(k, n, method="wilson")`; k = 0 and k = n stay inside [0, 1] (message: "the Wald interval goes below 0 here; that is why we use Wilson") |
| 13 | Bootstrap percentile interval | deep | code | `bootstrap_ci(x, stat, B, level, rng)`; same seed → same interval; the interval contains `stat(x)`; with 4× the data the width shrinks by 30–70% (property, not a number); B = 2,000 keeps it under 1 s |
| 14 | Interval for a difference in proportions | drill | code | `diff_prop_ci(k1, n1, k2, n2, z=1.96)` (§4.6); hand-computed example to 4 decimals in the test; order of groups changes the sign |
| 15 | Read an interval against a threshold | drill | trace | `⚠ HAND-TRACE` the chapter's `verdict()` printed for 5 intervals (edges exactly on the MEI included: `lo == mei` is *inconclusive*) |
| 16 | How many observations do I need? | applied | code | `n_for_margin(sd, margin, level=0.95)` and `n_for_proportion(margin, p=0.5)`; always rounds **up** (`math.ceil`); hand values; message "rounding down gives a margin slightly too wide" |
| 17 | A narrow interval around the wrong value | deep | explain | `assessment = "explain"`; a 200,000-row opt-in survey vs a 400-row random sample (§4.7): which to trust and why. Checklist: "the interval only measures sampling error" / "bias does not shrink with n" / "more data makes a biased estimate *more confidently* wrong" / "fix the sampling, not the size" |

## D. p-values and significance (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Two-proportion z-test | applied | code | `two_prop_test(kA, nA, kB, nB)` → `(z, p)` two-sided, pooled SE; equals `statsmodels.stats.proportion.proportions_ztest`; identical groups → z = 0, p = 1 |
| 19 | p-value by permutation | deep | code | `permutation_p(a, b, reps, rng)` for the difference in means, with the +1 correction; same seed → same p; agrees with `scipy.stats.permutation_test` within ±0.03 at reps = 5,000; p is never exactly 0 |
| 20 | Many tests, many false alarms | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` prints `1 - 0.95**k` for k = 1, 5, 20, 100 (`:.3f`) and the Bonferroni threshold `0.05/k` (`:.4f`) |
| 21 | Power by simulation | challenge | code | `power(p0, p1, n, sims, rng)` (§5.5); properties: p1 = p0 → power in [0.02, 0.09] (≈ α); increases with n (3 sizes); within 0.06 of `statsmodels` `NormalIndPower` with `proportion_effectsize` |
| 22 | Cohen's d | drill | code | pooled sd with ddof=1; hand example; equal groups → 0; swapping groups flips the sign |
| 23 | Practical against statistical | applied | code | `classify(lo, hi, mei, alpha_ci_excludes_zero)` → one of the three `verdict` labels plus `significant: bool`; the chapter's three table rows (§6.2) as tests: "significant and not worth it" exists |
| 24 | Big sample, tiny effect | deep | explain | n = 2,000,000 per group, p < 0.001, lift 0.02 points: what to tell the manager. Checklist: effect size first, interval, minimum effect of interest, cost of the change, "significant ≠ important" |

## E. Correlation (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Pearson and Spearman by hand | drill | code | `pearson(x, y)`, `spearman(x, y)` (ranks with ties averaged) equal `scipy.stats.pearsonr/spearmanr`; a constant column → `ValueError` ("r is undefined when one variable does not vary") |
| 26 | Anscombe's quartet | applied | code | `pair_summary(x, y)` → mean x, mean y, var x, r, slope, intercept; the four quartet sets inline: all give 9.0, 7.50, 11.0, 0.816, 0.500, 3.00 (rounded), so the summary alone cannot tell them apart; second function `looks_linear(x, y)` (residual check) separates set 1 from 2 and 4 |
| 27 | Where r fails | deep | trace | `⚠ HAND-TRACE` r for y = x² on x = −3…3 (0.000), for a line plus one outlier, and for a perfect monotone curve vs its Spearman (`:.3f`); the code is given and deterministic |
| 28 | Spurious correlation of trends | deep | code | `diff_corr(a, b)` = Pearson of first differences; test: 30 seeded pairs of independent random walks; mean `|raw r|` > 0.3 but mean `|diff r|` < 0.15 (properties, wide margins) |

## F. Causation and confounders (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | A confounder in action | applied | code | `naive_and_true(df)` on a small `make_app_world`-style table (built in `conftest.py`, n = 4,000, true effect 150): naive difference ≥ 1.5× the effect; returns both numbers |
| 30 | Stratified (adjusted) difference | deep | code | `adjusted_diff(df, treat, outcome, by)` = within-stratum differences weighted by stratum size; a hand-made Simpson's paradox table of 8 rows: naive says +, adjusted says −; empty treated/control in a stratum → skip it and report it |
| 31 | Regression adjustment | challenge | code | `adjusted_effect(df)` with `smf.ols("spend ~ app + engaged")` → `(coef, ci_low, ci_high)`; compared with fitting smf directly in the test; on the conftest world the CI contains the true 150 and the naive diff does not |
| 32 | Which comparison is fair? | drill | trace | `⚠ HAND-TRACE` 8-row table; code prints the naive difference, then the difference inside each group, then the weighted one (`:.1f`) |

## G. Reporting uncertainty (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 33 | Round to the uncertainty | drill | code | `sig_round(value, ref)` (§9.1): ref 0.4 → 1 decimal, 37 → 0 decimals with thousands comma, ref 0 or `nan` → whole number; message for rounding to a fixed 2 decimals |
| 34 | Report a mean with its interval | applied | code | `report_mean(x, label, unit, level)` exact format of §9.1; NaNs dropped and n counts only real values; level 0.9 prints `90% CI` |

## H. Project: critique and redo a flawed analysis (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Redo a flawed analysis | challenge | code | `assessment = "build"`; `redo(study_df, mei)` → dict `naive_diff`, `adjusted_diff`, `ci` (95%), `verdict` (chapter labels), `report` (string from `report_mean`-style rounding, mentions "observational" and "confounder"). Data: a small `make_study` copy in conftest (n = 5,000, known effect). Tests: adjusted CI contains the true effect on 3 seeds; naive does not; verdict consistent with the CI; report contains the interval numbers |

## Counts check

Tiers: drill 11 (1, 3, 4, 8, 10, 14, 15, 22, 25, 32, 33) · applied 13 (2, 5, 6, 7, 11, 12, 16, 18, 20, 23, 26, 29, 34) ·
deep 8 (9, 13, 17, 19, 24, 27, 28, 30) · challenge 3 (21, 31, 35) = 35.
Traces 6: 3, 6, 15, 20, 27, 32. Explain 4: 4, 8, 17, 24. Code 25. One assessment of each kind: explain 17, trace 20, fix 9, build 35.

## Risks and open questions

- p26 uses the published Anscombe numbers; they are exact data, not random, so hard-coding is fine (R3).
- p21 and p11 are the slowest tests (simulations): keep sims ≤ 2,000 and reps ≤ 1,000; measured ~0.2 s per 1,000 intervals.
- `statsmodels` prints `FutureWarning`s on some versions; tests should not fail on warnings (no `-W error`).
- p31 requires the learner to know formula syntax from §8.3; the hint should show `smf.ols("y ~ a + b", data=df).fit()`.
