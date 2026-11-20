# Problem plan: ds.09 Experimentation and causal inference (30 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.09.p001` … `p030`, folder `pNNN-slug`. Requires ds.02. Libraries: NumPy, pandas,
SciPy, statsmodels (scikit-learn allowed for the propensity model only).

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 21 code, 6 trace, 3 explain.
**assessment:** explain = p019, trace = p011, fix = p015, build = p030.
**★ core set (write first, 12):** 1, 3, 4, 6, 8, 11, 13, 15, 17, 19, 24, 30. Outcome (size an experiment and analyse it without
peeking errors): p6–p9, p17–p20, p30.

**Testing notes**
- Names follow the chapter's §12 library: `bucket`, `arm`, `two_prop_test`, `welch`, `n_per_arm_prop`, `n_per_arm_mean`, `mde_prop`,
  `srm_check`, `smd`, `dedupe`, `cuped`, `holm`, `benjamini_hochberg`, `obf_boundaries`, `decide`.
- **Exact checkers:** `statsmodels.stats.proportion.proportions_ztest`, `statsmodels.stats.power.NormalIndPower` /
  `zt_ind_solve_power` (sample size within 1% — the chapter's own test), `scipy.stats.ttest_ind(equal_var=False)`,
  `statsmodels.stats.multitest.multipletests(method="holm"/"fdr_bh")`, `scipy.stats.chisquare` for SRM.
- **Simulations are expensive in the chapter** (`sims=400_000` for boundaries, 20,000 for peeking). Tests use ≤ 4,000 simulations,
  vectorised with NumPy (no Python loop per simulated user), and tolerances that the reference meets on 5 seeds (e.g. false-positive
  rate of 5 peeks in 0.11–0.18; a single look in 0.035–0.065). The learner's function takes `sims` and `seed` arguments.
- Data: `sim_experiment(n, seed)` (§10) and the observational dataset of §11.3 with a **known true effect**, in `conftest.py`
  with n ≤ 60,000 rows (vectorised; fast).
- Bayesian A/B: Beta posteriors by `rng.beta` with ≤ 100,000 draws, or exactly with `scipy.stats.beta` where possible.

## A. Why randomise, and the anatomy of a test (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Stable assignment by hashing | drill | code | `bucket(user_id, salt, n_buckets)` with `hashlib.sha256` (never `hash()`, which changes per process); `arm(user_id, salt, share)`; same user → same arm across calls and processes (subprocess check); shares within 1% on 100,000 ids; a different salt reshuffles |
| 2 | The naive comparison lies | drill | trace | `⚠ HAND-TRACE` the §1.2 example with 8 inline users (potential outcomes known): print the true average effect and the naive treated-minus-untreated difference when heavy users opt in |
| 3 | Test of two proportions | drill | code | `two_prop_test(x_c, n_c, x_t, n_t, alpha)` → lift, z, p, CI of the difference (unpooled CI, pooled z); equals `proportions_ztest` |
| 4 | Welch test for means | drill | code | `welch(y_c, y_t, alpha)` → difference, CI, p; equals `ttest_ind(equal_var=False)`; Welch–Satterthwaite df |
| 5 | Significant but not important | drill | trace | `⚠ HAND-TRACE` four (lift, CI) results and a business threshold of +1 pp: print the decision the given `decide`-style rule prints for each (ship / don't ship / inconclusive) |

## B. Power and sample size (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Sample size by formula | drill | code | `n_per_arm_prop(p1, delta, alpha, power)` and `n_per_arm_mean(sigma, delta, ...)`; within 1% of statsmodels `NormalIndPower().solve_power` (effect size from `proportion_effectsize`) |
| 7 | Verify power by simulation | applied | code | `simulate_power(p1, delta, n, sims, alpha, seed)` vectorised; at the formula's n the simulated power is 0.8 ± 0.03 |
| 8 | Minimum detectable effect | applied | code | `mde_prop(p1, n, alpha, power)` by inverting the formula (bisection); `n_per_arm_prop(p1, mde_prop(p1, n)) ≈ n` (the chapter's test) |
| 9 | Duration from traffic | applied | trace | `⚠ HAND-TRACE` given `duration_days(n_per_arm, arms, daily_users, eligible_share)` (rounds up to whole weeks, minimum 7), print the duration for 4 inline scenarios

## C. Variance reduction and awkward metrics (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | CUPED | applied | code | `cuped(y, x, treated, max_z)` with θ = cov(y, x)/var(x) from **pooled** data; the effect estimate stays unbiased (mean over seeds within the CI of the truth) and its standard error drops by ≈ `sqrt(1 − ρ²)` |
| 11 | Trace CUPED by hand | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` 6 users with pre-period x and outcome y (inline): print θ, each adjusted value and the adjusted means of the two arms, to 2 decimals |
| 12 | Ratio metrics and the unit of analysis | deep | code | `ratio_metric_se(clicks, views)` per user with the delta method; naive per-pageview SE is too small (test checks the delta SE against a bootstrap over users within 15%) |
| 13 | Heavy-tailed revenue | deep | code | `winsorised_welch(y_c, y_t, q)` caps at the pooled q-quantile; on `revenue(n, lift)` the CI is narrower than plain Welch; cap computed on pooled data, not per arm |

## D. Trust checks (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Sample ratio mismatch | drill | code | `srm_check(n_control, n_treatment, share)` → chi-square p; equals `scipy.stats.chisquare`; 50,000 vs 50,800 at 50/50 → p < 0.01 |
| 15 | Fix the analysis that skipped its trust checks | applied | code | `assessment = "fix"`; given an analysis that counts duplicated users twice, ignores an SRM and reports the lift; fix: `dedupe` then `srm_check` first and refuse to report a lift (return a reason) when SRM p < 0.001; tests on three datasets |
| 16 | Covariate balance | applied | explain | after randomisation one pre-experiment covariate has SMD 0.15 and the others are < 0.05: explain what that can mean (chance with many covariates vs a broken assignment), how to tell (SRM, A/A history, assignment code), and why regression adjustment helps either way; uses `smd` output printed in `problem.md`; checklist

## E. Multiple testing and peeking (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Holm and Benjamini–Hochberg | drill | code | `holm(p, alpha)`, `benjamini_hochberg(p, q)` return reject flags in the **original order**; equal `multipletests` |
| 18 | Peeking inflates false positives | applied | code | `peeking_false_positive_rate(K, per_look, sims, crit, seed)` vectorised over simulations; K = 1 ≈ 0.05; K = 5 clearly higher (band) |
| 19 | Explain why peeking breaks a test | deep | explain | `assessment = "explain"`; a manager says "it was significant on day 9, stop the test": explain the multiple-looks problem, the cost in false positives (the simulated number from the chapter), and two honest ways to monitor (fixed horizon; group-sequential boundaries / mSPRT); checklist |
| 20 | Group-sequential boundaries | challenge | code | `obf_boundaries(K, alpha, sims, seed)` (O'Brien-Fleming shape `c·sqrt(K/k)`, calibrating c by simulation, ≤ 20,000 sims); overall false-positive rate ≈ alpha ± 0.01; the first boundary is much stricter than the last |
| 21 | Segment fishing | deep | trace | `⚠ HAND-TRACE` 10 segment p-values (inline): print which segments survive no correction, Holm and BH at 0.05 |

## F. A Bayesian view (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | Beta posterior for a conversion rate | drill | code | `posterior(x, n, a, b)` returns the Beta parameters and a 95% credible interval (`scipy.stats.beta.ppf`); flat prior with x = 0 gives a non-zero upper bound |
| 23 | Probability that B beats A | applied | code | `bayes_ab(x_c, n_c, x_t, n_t, a, b, draws, seed)` → P(t > c) and expected loss; symmetric data → ≈ 0.5; tolerance from the Monte-Carlo SE |
| 24 | Bayes does not cure peeking | deep | explain | why stopping when P(B > A) > 0.95 at any of K looks still inflates wrong decisions (§9.3 simulation, printed in `problem.md`); checklist |

## G. Causal inference without an experiment (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Regression adjustment | applied | code | `adjusted_effect(df, treatment, outcome, confounders)` with statsmodels OLS; recovers the known effect within its CI; the unadjusted difference is biased (test checks both) |
| 26 | Inverse propensity weighting | deep | code | `ipw_effect(df, ...)` with a logistic propensity model, clipped weights; weighted SMDs (`wsmd`) all < 0.1 after weighting; estimate within 15% of the truth |
| 27 | Doubly robust estimation | challenge | code | `aipw_effect(df, ...)`; still close to the truth when **either** the outcome model or the propensity model is deliberately misspecified (two tests) |
| 28 | Confounder, mediator or collider? | deep | trace | `⚠ HAND-TRACE` 6 variables described by arrows (inline DAG as edge list); the given rule prints adjust / do not adjust; the learner predicts the output |
| 29 | Difference in differences | applied | code | `did(df)` on a two-group, two-period table; recovers the planted effect; the simple post-period difference is biased by the group gap |

## H. Project (Ch. 10, 12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Analyse a simulated product experiment | challenge | code | `assessment = "build"`; `analyse(df, plan)` returns a decision memo dict in the §10 order: trust checks (dedupe, SRM, balance), primary metric with CUPED, guardrail non-inferiority, Holm-corrected pre-registered segments, decision via `decide`; tests on `sim_experiment` with (a) a real effect, (b) no effect, (c) an SRM — each gives the right decision |

## Counts check

Tiers: drill 10 (1, 2, 3, 4, 5, 6, 11, 14, 17, 22), applied 10 (7, 8, 9, 10, 15, 16, 18, 23, 25, 29),
deep 7 (12, 13, 19, 21, 24, 26, 28), challenge 3 (20, 27, 30).
Kinds: trace 6 (2, 5, 9, 11, 21, 28), explain 3 (16, 19, 24), code 21.
Assessment: explain p019, trace p011, fix p015, build p030 — exactly one each.

## Risks and open questions

- The chapter's `sequential_boundaries` uses 400,000 simulations; p020 must accept a looser tolerance with 20,000 and say so.
- Python's `hash()` is salted per process: p001 must forbid it explicitly (the subprocess test catches it).
- `proportions_ztest` uses the pooled variance by default; p003's statement must say which variance the z and the CI use.
