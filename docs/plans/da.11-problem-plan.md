# Problem plan: da.11 Applied business analytics (30 problems)

Rules: [README.md](README.md) (shared, especially R1–R4) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `da.11.p001`…`p030`, folder `pNNN-slug`.

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 21 code, 5 trace, 4 explain.
**assessment:** explain = p012, trace = p004, fix = p016, build = p030.
**★ core set (12):** p001, p003, p005, p006, p012, p013, p016, p019, p021, p023, p024, p030.

**Testing notes**
- Libraries: numpy, pandas, scipy.stats, statsmodels (power), scikit-learn (`KMeans`, `StandardScaler`,
  `adjusted_rand_score`, §5.5). All import under the runner's limits (sklearn 2.7 s measured by the parent; the
  scipy/statsmodels stack 2.7 s, 219 MB in the da.08 spike). No new spike needed.
- Data: small copies of the chapter generators (`make_shop`, `make_experiment`, `make_sessions`, §1.2, §2.3, §3.2) in
  `conftest.py` with `n` cut to ≤ 5,000 rows, passed in as DataFrames. Hand-checkable problems use inline tables
  of 6–15 rows.
- Simulations (`peeking_simulation`, power checks) take `rng`/`seed` and are tested by **properties with wide
  margins** (R3): e.g. false-positive rate with peeking > 0.10 across 400 sims, without peeking in [0.02, 0.09].
  Keep sims ≤ 500 so each test stays under ~3 s.
- Chapter functions used as fixed specs (quote in `problem.md`): `n_per_group` (§2.2, `ceil`), `srm_check`
  (§2.4, chi-square; mismatch when p < 0.001), `two_prop` (§2.5), `mean_diff_ci` (§2.6), `cuped` (§2.7, returns
  adjusted values, theta, r²), `funnel_table` (§3.3, exact columns), `wilson`, `step_rates` (§3.4), `rfm_table`
  (§5.1, grain one row per customer with an order by `asof`), `score_quantile` (§5.2, `rank(method="first")` +
  `qcut`), `segment(r, f)` (§5.3, exact six labels), `Finding`/`lint_finding` (§6.4, max 450 words).
- KMeans: `n_init=10, random_state=0` passed explicitly; tests compare clusterings with `adjusted_rand_score`
  or sorted centres, never raw label numbers (labels are permuted between versions).

## A. A/B testing (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | How many visitors per group? | drill | code | `n_per_group(p0, mde, alpha, power)` (§2.2): the four chapter MDEs; always rounds up; within 2% of statsmodels `NormalIndPower` with `proportion_effectsize` |
| 2 | What an underpowered test does | drill | explain | §2.12: the same small test repeated 400 times. Explain why the runs that come out "significant" overstate the lift and sometimes have the wrong sign. Checklist: low power, most runs miss the effect, the significant ones are the lucky large ones (exaggeration), sign errors, plan n with `n_per_group` before starting |
| 3 | Check the randomisation first | drill | code | `srm_check(counts, expected_share)` (§2.4) → `(chi2, p)` equal to `scipy.stats.chisquare`; `[12_000, 11_100]` flags a mismatch; uneven planned split (0.6, 0.4) handled |
| 4 | Read an experiment by hand | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given code computes conversion A and B, absolute and relative lift and the SRM verdict for an inline 2×2 count table; predict the printed lines (`:.2f`, `:.1%`) |
| 5 | The primary metric | applied | code | `two_prop(kA, nA, kB, nB, level)` (§2.5) → lift in points, CI, p; equals statsmodels `proportions_ztest` p within 1e-9; B worse → negative lift |
| 6 | Revenue per visitor with a bootstrap | applied | code | `mean_diff_ci(a, b, n_boot, seed)` (§2.6); same seed → same CI; CI contains the observed difference; zero-heavy data (most visitors spend 0) handled |
| 7 | CUPED | deep | code | `cuped(df, y, x)` (§2.7): adjusted mean difference equals the raw one within its SE; adjusted variance smaller by about `1 - r²` (± 5%); x uncorrelated with y → theta ≈ 0, nothing changes |
| 8 | Peeking inflates false alarms | deep | code | `peeking_simulation(n_sims, n_per_group, looks, p, seed)` (§2.8) → false-positive rate; properties: looks = 1 → in [0.02, 0.09]; looks = 14 → > 0.10 (message: "every extra look is another chance to stop on noise") |
| 9 | Segments: look, do not decide | drill | explain | why a segment that "won" in a test with 8 segments is not a result (§2.10); checklist: multiple comparisons, small n per segment, pre-registration, follow-up test |
| 10 | The decision | applied | code | `decide(primary_ci, guardrail_cis, mei)` → `"ship"`, `"do not ship"`, `"extend the test"` with the reason string; rules from §2.11 written in `problem.md`; a guardrail CI entirely below its limit blocks shipping |

## B. Funnel analysis (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | The funnel table | drill | code | `funnel_table(df, steps)` (§3.3): exact columns; first row NaN for "% of previous step"; `dropped` column; hand 10-session table |
| 12 | Why a funnel can mislead | applied | explain | `assessment = "explain"`; device mix shifts from desktop to mobile and the overall checkout rate falls although each device improved (§3.4, §3.7). Checklist: mix vs rate, compare within segments, Simpson's paradox, step definitions, sessions vs users |
| 13 | Step rates by segment with Wilson intervals | applied | code | `step_rates(df, by)` (§3.4) with `wilson` CIs; a segment with 0 sessions at a step → NaN rate, not a crash; sorted by segment |
| 14 | Size the opportunity | deep | code | `opportunity(df, target_rate, n_boot, seed)` (§3.5): extra purchases if one step reached the target rate, with a bootstrap range; target below the current rate → 0, not negative |
| 15 | Funnel by hand | drill | trace | `⚠ HAND-TRACE` 12 sessions, 4 steps; predict `% of previous step` and `% of all sessions` (`:.1f`) |
| 16 | Fix the non-monotone funnel | deep | code | `assessment = "fix"`; given `funnel_table` that counts each step flag independently, so sessions that "purchased" without "add to cart" (a logging bug) make a step exceed the previous one (> 100%). Fix: a session counts at a step only if it passed every earlier step; also return the number of inconsistent sessions. Tests: no step above 100% of previous; count of inconsistent rows correct |

## C. Cohorts, retention and customer value (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | The retention matrix | applied | code | `retention_matrix(orders, customers)` (§4.2): rows = signup month, columns = months since signup, values = share active; month 0 = 1.0; immature cells (not yet observable at the as-of date) are NaN, **not 0** (message names the trap) |
| 18 | Pooled retention curve | applied | code | `pooled_retention(matrix_counts, ks)` weighted by cohort size and using only cohorts that reached month k (§4.3); hand matrix where the simple average of rates gives a different (wrong) answer |
| 19 | 90-day repeat rate | drill | code | `repeat_rate_90d(orders, customers, asof)`: only customers whose first order is ≥ 90 days before `asof` enter the denominator; second order within 90 days of the first; hand data with a boundary customer at exactly 90 days (included, stated) |
| 20 | Cohort retention by hand | drill | trace | `⚠ HAND-TRACE` 6 customers, signup months and order months given; predict the printed retention rows as lists (`:.2f`, `nan` printed as `-`) |
| 21 | The LTV curve | deep | code | `ltv_curve(orders, customers, months)` → cumulative revenue per customer by months since signup, only mature cohorts at each point (§4.5); non-decreasing; the curve at month 0 equals first-order revenue per customer |
| 22 | Time to the second order | applied | code | `days_to_second(orders)` → Series per customer; one-order customers excluded and counted separately; median days; customers whose first two orders are on the same day → 0 days (stated rule) |

## D. RFM segmentation (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | The RFM table | drill | code | `rfm_table(orders, customers, asof)` (§5.1): orders after `asof` ignored; R in days; customers with no order by `asof` absent; hand data |
| 24 | Scores and segments | applied | code | `score_quantile(s, higher_is_better, n)` (§5.2) with `rank(method="first")` so heavy ties do not break `qcut`; `segment(r, f)` six labels; test: a small recency gives score 5; every customer gets exactly one label |
| 25 | Which segment? | drill | trace | `⚠ HAND-TRACE` the chapter's `segment(r, f)` for 8 `(r, f)` pairs including the order-dependent ones (`(4, 4)` is Champions before Loyal; `(3, 2)` is Needs attention); predict the labels |
| 26 | Do the segments mean anything? | deep | code | `future_value_by_segment(rfm, orders_after)` (§5.4): revenue per customer in the next 90 days by segment; test: Champions > Hibernating on the conftest data; customers with no future orders count as 0, not dropped |
| 27 | k-means as an alternative | challenge | code | `kmeans_segments(rfm, k, seed)` with log-transform + `StandardScaler` + `KMeans(n_init=10, random_state=seed)` → labels and silhouette; compared to the RFM segments with `adjusted_rand_score` only as a reported number; test checks scaling was used (an unscaled version puts almost everything in one cluster on the given data) |
| 28 | When RFM misleads | deep | explain | three cases (a seasonal business, a subscription product, a single huge B2B order) and what goes wrong with RFM scores in each (§5.7) |

## E. From analyses to a recommendation; the project (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Lint the recommendation page by hand | challenge | trace | `⚠ HAND-TRACE` the chapter's `lint_finding(f, max_words=450)` (§6.4) on a draft `Finding` with four planted faults (impact as a point, recommendation without a date, one evidence item without a number, a vague phrase); predict the exact printed issue list in order |
| 30 | Customer analytics case study | challenge | code | `assessment = "build"`; `build_case_study(data)` returns a `Finding` (§6.4) + the markdown page: A/B decision, funnel opportunity, 90-day retention by channel, RFM segment sizes, each number computed from `data`; `lint_finding` clean (≤ 450 words); `check_case_study(page, finding)` (§7.2) finds no number in the page that is not in the results; a second dataset changes the numbers (no hard-coding) |

## Counts check

Tiers: drill 10 (1, 2, 3, 9, 11, 15, 19, 20, 23, 25) · applied 10 (4, 5, 6, 10, 12, 13, 17, 18, 22, 24) ·
deep 7 (7, 8, 14, 16, 21, 26, 28) · challenge 3 (27, 29, 30) = 30.
Traces 5: 4, 15, 20, 25, 29. Explain 4: 2, 9, 12, 28. Code 21.
One assessment of each kind: explain 12, trace 4, fix 16, build 30.

## Risks and open questions

- §6.2 says prioritisation is **an argument, not a formula** (impact, confidence, effort weighed in words). Do not add a scoring problem; p29 traces the linter instead. Copy `lint_finding` and the `VAGUE` list exactly from §6.4.
- p17/p21 depend on the "mature cohort" rule; write the as-of rule into `problem.md` with a worked example, as this
  is where most learners (and test authors) go wrong.
- p27 silhouette values differ slightly between sklearn versions; never assert them, only that they are in (−1, 1].
- p8 and p6 are the slowest (simulation, bootstrap): keep n_sims ≤ 400, n_boot ≤ 2,000; measure the reference.
