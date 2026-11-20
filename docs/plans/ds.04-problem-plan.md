# Problem plan: ds.04 Evaluation done right (45 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.04.p001` … `p045`, folder `pNNN-slug`. Requires ds.03. Libraries: NumPy, pandas,
scikit-learn.

**Mix:** 15 drill, 15 applied, 11 deep, 4 challenge. **Kinds:** 31 code, 9 trace, 5 explain.
**assessment:** explain = p005, trace = p024, fix = p012, build = p045.
**★ core set (write first, 18):** 1, 3, 5, 7, 9, 12, 14, 17, 19, 21, 24, 26, 28, 30, 33, 37, 41, 45. Covers the three outcomes:
find the leak (p7–p17), beat a baseline with the right split (p19–p26), threshold from a business cost (p28–p31).

**Testing notes — making leaks detectable** (the heart of this module)
- **Spy transformers.** `conftest.py` has `RecordingScaler` (a `StandardScaler` subclass that stores the row index / a hash of every
  row it was fitted on). The learner's function receives a model factory or a pipeline step from the test; the test then asserts
  that **no test-row id appears in what was fitted**. Message: "your scaler (or selector, or encoder) saw the test rows during fit".
- **Sentinel rows.** The test set contains extreme sentinel values (e.g. 1e6). If the learner fits preprocessing on all data,
  the fitted `mean_` / category list / target encoding changes; the test compares with a fit on train only.
- **Too-good scores.** For problems that "find the leak", the data generator (`make_churn(leaks=True)`, `make_loans`, chapter §1/§15)
  plants a leak whose honest AUC is ≈ 0.70 and leaky AUC ≈ 0.99; tests check that the learner's honest pipeline lands in a band
  (e.g. 0.62–0.80) and that the named leaky column is the planted one. Bands are checked on 3 seeds by the author.
- Split problems check properties (no group on both sides, all test times after all train times), never fixed index lists.
- Data generators from the chapter (`make_churn`, `make_patients`, `make_sales`, `make_fraud`, `make_churn_regional`, `make_loans`)
  live in `conftest.py`, called with small `n` (≤ 5,000 rows; `make_fraud` with n = 20,000 only where rarity matters) so each file
  stays ≤ ~15 s. Models: `LogisticRegression`, `HistGradientBoostingClassifier(max_iter=50)`, never `n_jobs=-1`.
- Costs, thresholds and calibration use inline small arrays when the answer must be exact (hand-worked), generators otherwise.

## A. What leakage is (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Too good to be true | drill | explain | a colleague reports AUC 0.99 on churn; explain why that is an alarm, not good news, and the first three checks you would run (single-feature scores, shuffled labels, timeline); checklist
| 2 | Name the leak family | drill | trace | `⚠ HAND-TRACE` given code that maps 8 leak stories to the four families (preprocessing, target, duplicates/groups, time) by keyword, print its labels |
| 3 | Two evaluations of one model | deep | code | `two_evaluations(X, y, model, seed)` returns `(cv_auc_on_all, holdout_auc)` using `cv_auc` (§1); on `make_churn(leaks=True)` the gap is > 0.15 |
| 4 | The golden rule | drill | trace | `⚠ HAND-TRACE` six code snippets (fit scaler, select features, impute, split …) in order; print `ok` / `leak` for each according to the golden rule (§2.3) as the given checker applies it |
| 5 | Explain leakage to a colleague | deep | explain | `assessment = "explain"`; explain, with the churn story of §1, what leakage is, why the score lied, and the golden rule; checklist in `answer.md` |

## B. Preprocessing and target leaks (Ch. 3–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Scale on train only | drill | code | `scale_split(X_train, X_test)` returns both scaled; spy/sentinel test: fitted mean equals the train mean |
| 7 | Feature selection inside the pipeline | applied | code | `honest_selection_score(X, y, k)` with `SelectKBest` inside a `Pipeline` in CV; on pure noise with 2,000 features the score is ≈ 0.5 (band 0.4–0.6), while `leaky_selection_score` (§3.1) is > 0.7 |
| 8 | Target encoding without leaking | deep | code | `target_encode(train_col, train_y, test_col, n_folds, seed)` out-of-fold for train, full-train means for test; test checks no row's own target is used (a row's encoding unchanged when its own y flips) |
| 9 | Single-feature scores | drill | code | `single_feature_auc(X, y, cv)` returns a sorted Series; the planted leaky feature is first and > 0.95 |
| 10 | Shuffled-label sanity check | applied | code | `shuffled_label_check(model, X, y, repeats, seed)`; honest pipeline → mean AUC ≈ 0.5; a pipeline with a selection leak → clearly > 0.5 |
| 11 | Which column is from the future? | applied | trace | `⚠ HAND-TRACE` a feature table with timestamps (`created_at`, `cancelled_at`, `last_login`) relative to a prediction date; print which features are usable at prediction time |
| 12 | Fix the leaky churn pipeline | applied | code | `assessment = "fix"`; given code that scales and selects before splitting and keeps a post-outcome column; tests: spy scaler sees only train rows, the leaky column is gone, holdout AUC in the honest band |
| 13 | Rebuild a feature as of the date | deep | code | `as_of_feature(events, customers, cutoff)` counts events strictly before each customer's prediction date; test plants events on and after the date |

## C. Duplicates and groups (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Find exact and near duplicates | deep | code | `duplicate_groups(df, cols, round_to)` assigns a group id to rows equal after rounding; planted near-copies found |
| 15 | Duplicates across the split | applied | code | `cross_split_duplicates(train, test, cols)` returns the count and ids; split must then be redone by group |
| 16 | Group split by patient | drill | code | `group_split(df, group_col, test_frac, seed)` with `GroupShuffleSplit`; no patient on both sides; sizes approximately right |
| 17 | How much did the row split lie? | applied | code | `row_vs_group_cv(X, y, groups)` on `make_patients`: row-wise CV score higher than `GroupKFold` score by a clear margin |
| 18 | Choose the group | deep | explain | for three datasets (patients' visits, shop receipts, sensor readings per machine), name the grouping column and why; checklist |

## D. Time-based splits (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Time split by a cutoff date | drill | code | `time_split(df, date_col, cutoff)`; all train dates < all test dates; rows on the cutoff go to test |
| 20 | `TimeSeriesSplit` by hand | drill | trace | `⚠ HAND-TRACE` print the train/test index ranges of `TimeSeriesSplit(n_splits=3)` on 12 rows (exact, documented algorithm) |
| 21 | Detect look-ahead in feature code | applied | code | `uses_future(feature_fn, series, t)` (§7.4): perturb the series after t and check the feature at t changes; catches a centred rolling mean, passes a trailing one |
| 22 | Seasonal-naive baseline | drill | code | `seasonal_naive(train, horizon, season)`; MAE on `make_sales`; equals the hand formula |
| 23 | Does the model beat seasonal naive? | applied | code | `beats_seasonal_naive(model_fn, series, folds)` with rolling origins; returns both MAEs and the verdict |

## E. Baselines and proving "better" (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Read the baseline table | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given fold AUCs (inline) of a rule baseline and a model, the given code prints the mean difference, its standard error and the verdict; the learner predicts all three |
| 25 | A business-rule baseline | drill | code | `rule_score(X)` (§8.3: e.g. "months since last order") as a score; its AUC is computed with `roc_auc_score`; the model must beat it |
| 26 | Better is a difference with an error bar | challenge | code | `paired_difference(y, p_model, p_base, reps, seed)` bootstraps the AUC difference on the same rows; returns mean and 95% CI; CI excludes 0 for a real gain, includes it for a fake one |
| 27 | Top-decile lift | drill | trace | `⚠ HAND-TRACE` given `top_decile_lift` and 20 inline (y, score) rows, print the base rate, the top-decile rate and the lift

## F. Imbalance, thresholds, cost (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | Cost of a threshold | drill | trace | `⚠ HAND-TRACE` given `total_cost(y_true, y_pred, cost)` with `{FP: 5, FN: 100}` and 10 inline rows, print the cost at thresholds 0.3, 0.5 and 0.7 and the cheapest one
| 29 | Best threshold from a cost curve | applied | code | `best_threshold(y_val, p_val, cost, grid)` minimises total cost on **validation**; test checks the test set is not passed in (signature) and the chosen threshold is near the theoretical `FP/(FP+FN)` for calibrated probabilities |
| 30 | ROC-AUC against average precision | applied | trace | `⚠ HAND-TRACE` 10 inline scores and labels; print ROC-AUC (pair counting) and AP (step formula) to 3 decimals |
| 31 | How stable is the threshold? | deep | code | `threshold_stability(y, p, cost, reps, seed)` bootstraps the best threshold; returns its 5–95% range |
| 32 | The oversampling leak | challenge | code | `oversample_then_cv` vs `cv_then_oversample` (oversample inside each training fold only); the leaky one is optimistic on `make_fraud`; spy check: duplicated minority rows never appear in a validation fold |
| 33 | Budget as a count: precision at k | drill | code | `at_k(y, score, k)` returns precision and recall at the top k; ties broken by original order |
| 34 | Why accuracy lies on fraud | drill | explain | with 0.2% fraud, why 99.8% accuracy is worthless and which numbers to report; checklist |

## G. Calibration (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Reliability table | drill | code | `reliability(y, p, bins)` returns per bin: mean predicted, observed rate, count; empty bins dropped |
| 36 | Expected calibration error | applied | code | `ece(y, p, bins)`; perfectly calibrated simulation → < 0.02; squashed probabilities → > 0.1 |
| 37 | Calibrate on held-out data | applied | code | `calibrate(model, X_train, y_train, X_cal, y_cal)` with `CalibratedClassifierCV(FrozenEstimator(...))` (sklearn 1.9); ECE improves on test; the calibrator never sees test |
| 38 | Calibration moves the best threshold | deep | trace | `⚠ HAND-TRACE` given costs and four probability bins before/after calibration (inline), print the threshold the cost rule picks each time |

## H. Segments, reproducibility, training-serving (Ch. 12–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | Slice table | deep | code | `slice_table(frame, y, p, col)` returns rows, base rate, AUC per value; slices with one class get `NaN` AUC, not a crash |
| 40 | Worst slices scan | applied | code | `worst_slices(frame, y, p, cols, min_rows, top)` on `make_churn_regional`; the planted weak region is first |
| 41 | Seed noise: report the spread | applied | code | `seed_spread(run, seeds)` returns mean, std, min, max of a score across seeds; `run` is passed in (fast fake) |
| 42 | A reproducibility record | deep | code | `run_experiment(cfg, df)` (§13.6) returns a record with config, `data_fingerprint`, scores; same config twice → identical record (except time) |
| 43 | Same features in training and serving | deep | code | `build_features(raw)` used by both paths; equivalence test: batch features of 50 rows == single-row features for each row (column order, one-hot of an unseen category) |
| 44 | Population stability index | challenge | explain | explain what PSI = 0.05, 0.15, 0.4 mean for a model in production and what to do at each; uses `psi` output printed in `problem.md`; checklist |

## I. Project (Ch. 15)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 45 | Audit and fix the leaky loan project | challenge | code | `assessment = "build"`; `audit(df)` on `make_loans` returns the found problems (leaky column name, duplicate count, group column, preprocessing-before-split flag) and an honest `evaluate(...)` result; tests: each planted problem found, honest AUC in the band, leaky AUC above it |

## Counts check

Tiers: drill 15 (1, 2, 4, 6, 9, 16, 19, 20, 22, 25, 27, 28, 33, 34, 35), applied 15 (7, 10, 11, 12, 15, 17, 21, 23, 24, 29, 30, 36, 37, 40, 41),
deep 11 (3, 5, 8, 13, 14, 18, 31, 38, 39, 42, 43), challenge 4 (26, 32, 44, 45).
Kinds: trace 9 (2, 4, 11, 20, 24, 27, 28, 30, 38), explain 5 (1, 5, 18, 34, 44), code 31.
Assessment: explain p005, trace p024, fix p012, build p045 — exactly one each.

## Risks and open questions

- The installed scikit-learn is **1.9.1**, where `CalibratedClassifierCV(cv="prefit")` no longer exists: p037 uses
  `CalibratedClassifierCV(FrozenEstimator(model))` (`from sklearn.frozen import FrozenEstimator`), checked to import on 2026-11-18.
  form for the installed version and the test should accept both.
- Score bands (honest AUC 0.62–0.80 etc.) must be measured by the author on 3 seeds with the reference; widen rather than tighten.
- `make_fraud(40000)` from the chapter may be too slow under the 60 s cap with gradient boosting; use n = 20,000 and logistic regression.
