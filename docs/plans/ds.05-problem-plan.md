# Problem plan: ds.05 scikit-learn in depth (45 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.05.p001` … `p045`, folder `pNNN-slug`. Requires ds.04. Libraries: NumPy, pandas,
SciPy, scikit-learn **1.9** (installed version; `FrozenEstimator`, `TunedThresholdClassifierCV`, halving search all available).

**Mix:** 15 drill, 15 applied, 11 deep, 4 challenge. **Kinds:** 31 code, 9 trace, 5 explain.
**assessment:** explain = p010, trace = p004, fix = p036, build = p045.
**★ core set (write first, 18):** 1, 4, 6, 8, 10, 12, 14, 16, 18, 21, 24, 27, 30, 33, 36, 38, 41, 45. The learning outcome
(one pipeline object from raw data to predictions) is p012–p017 and p045.

**Testing notes**
- Data: the chapter's used-car table `make_listings(n, seed)` (§2) in `conftest.py`, called with n ≤ 2,000; the solution receives
  DataFrames. Raw columns include text, categories with rare levels, dates and missing values, as in the chapter.
- "Leak-free" is checked with the spy/sentinel tools of ds.04 (`RecordingScaler`, sentinel test rows), so a learner who fits a
  transformer outside the pipeline fails with a clear message.
- Custom estimators are checked with `sklearn.utils.estimator_checks.check_estimator` **only for the specific checks that matter**
  (`clone` round-trip, `get_params` contract, `fit` returns self, no learned attributes in `__init__`) — the full suite is slow and
  version-sensitive. Each check named in the assert message.
- Results compare with a hand-built equivalent (e.g. the pipeline equals manual fit/transform on train then predict on test,
  `rtol=1e-10`) rather than hard-coded scores (R3).
- Searches: ≤ 12 candidates × 3 folds, `n_jobs=None`. HistGradientBoosting with `max_iter ≤ 50`. Each file ≤ ~15 s.
- Saving/loading: `joblib.dump` to `tmp_path`; the "fresh process" test loads it with `subprocess.run([sys.executable, "-c", ...])`;
  works because the runner puts the test folder on `PYTHONPATH`, so `solution.CarAge` can be unpickled (the §12.2 lesson).

## A. The estimator API (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Fit, transform, predict | drill | code | `fit_and_predict(model, X_train, y_train, X_test)`; returns predictions; does not refit on test (spy model counts `fit` calls) |
| 2 | `fit_transform` equals `fit` then `transform` | drill | trace | `⚠ HAND-TRACE` `MinMaxScaler` on 4 inline rows: print `fit_transform` and `fit(...).transform(...)` (identical) and then `transform` of a new row outside the range (value > 1)
| 3 | Double-underscore parameters | deep | code | `set_alpha(pipe, value)` sets `ridge__alpha` with `set_params`; `get_params()` shows it; the original pipeline object is changed in place, a `clone` is not |
| 4 | Which object is it? | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given 8 objects (scaler, ridge, pipeline, column transformer, KMeans …) print for each whether it has `transform`, `predict`, `fit_transform`, using the given `hasattr` loop |
| 5 | `clone` gives an unfitted copy | drill | trace | `⚠ HAND-TRACE` print `hasattr(m, "coef_")` before fit, after fit, and for `clone(m)`; and the cloned `alpha` |

## B. Transformers (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Pick a scaler | drill | code | `scale(X_train, X_test, kind)` with `"standard"`, `"minmax"`, `"robust"`; train-only fit (sentinel test) |
| 7 | Impute with an indicator | applied | code | `impute(X_train, X_test)` with `SimpleImputer(strategy="median", add_indicator=True)`; indicator columns present; medians from train only |
| 8 | One-hot with unknown categories | drill | code | `encode(train_col, test_col)` with `handle_unknown="ignore"`; an unseen test category becomes all zeros, no error |
| 9 | Ordinal versus one-hot | applied | trace | `⚠ HAND-TRACE` the output arrays of `OrdinalEncoder` (with an explicit `categories=`) and `OneHotEncoder(sparse_output=False)` on 4 inline rows |
| 10 | When does encoding order matter? | deep | explain | `assessment = "explain"`; why ordinal encoding suits trees but misleads linear models, and why target encoding needs cross-fitting; checklist |

## C. Pipelines and ColumnTransformer (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | A two-step pipeline | drill | code | `make_ridge_pipeline(alpha)` = scaler + ridge; equals the manual version on the test rows |
| 12 | Different columns, different treatment | applied | code | `make_preprocessor(num_cols, cat_cols)` with a `ColumnTransformer`; output width = numeric + one-hot widths; no column lost |
| 13 | Select columns by type | applied | code | `make_preprocessor_auto()` with `make_column_selector(dtype_include=...)`; a new numeric column added later is picked up automatically |
| 14 | Raw data to predictions | applied | code | `full_pipeline()` from raw `make_listings` columns to price; `fit(raw_train).predict(raw_test)` works with missing values and unseen categories; CV MAE beats `DummyRegressor` |
| 15 | Slicing and inspecting a pipeline | drill | code | `feature_names(pipe)` returns `get_feature_names_out()` of the fitted preprocessor; names include `cat__fuel_diesel` style prefixes |
| 16 | Remainder and dropped columns | applied | trace | `⚠ HAND-TRACE` given a `ColumnTransformer` with `remainder="drop"` and then `"passthrough"`, print the output column names in order |
| 17 | Log target inside the model | applied | code | `log_target_model(base)` with `TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)`; predictions are in price units; equals manual log/exp |

## D. Custom estimators (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | A stateless transformer: car age | drill | code | `CarAge` (§6.2) computing age from `year` and a reference year parameter; `get_feature_names_out`; works in a pipeline |
| 19 | A transformer that learns: rare categories | applied | code | `RareGrouper(min_count, other)` learns frequent levels in `fit`; unseen and rare levels → `"other"`; learned attribute ends with `_` |
| 20 | Obey the estimator contract | deep | code | `QuantileClipper(lower, upper)`; passes the selected `check_estimator` checks (clone, params, fit returns self, no work in `__init__`) |
| 21 | Spot the contract violation | deep | trace | `⚠ HAND-TRACE` given 4 tiny custom transformers, the given checker prints which rule each breaks (`__init__` modifies a param, fit does not return self, learned attr without `_`, transform refits) |

## E. Feature engineering (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | A configurable preprocessor | applied | code | `make_prep(*, age, text, poly, target_encode)` (§7.2) returns a ColumnTransformer; each switch adds the expected columns |
| 23 | Cyclical month features | drill | trace | `⚠ HAND-TRACE` print sin/cos (3 decimals) for months 12, 1 and 6, then the distance Dec–Jan and Dec–Jun; shows why a plain month number puts December far from January
| 24 | Measure one idea at a time | challenge | code | `ablation(df, switches)` returns CV MAE per switch turned on alone, with the same folds; folds passed in |
| 25 | Selection inside the pipeline | applied | code | `selected_pipeline(k)` with `SelectKBest` as a step; spy test: selection fit only on training folds |
| 26 | Leakage in an engineered feature | deep | explain | the "price per brand mean" feature computed on the whole table: why it leaks, how to compute it inside the pipeline (`TargetEncoder` cross-fitting); checklist |

## F. Model selection and tuning (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Same folds for every model | drill | code | `compare_models(models, X, y, cv)` returns a DataFrame of fold scores with identical fold assignment; folds passed in |
| 28 | A custom scorer | drill | code | `within_10pct_scorer()` via `make_scorer(within_10pct)` (§8.2); higher is better; equals manual computation |
| 29 | Paired comparison of two models | deep | code | `paired_fold_diff(a_scores, b_scores)` returns mean difference, std and a t-statistic over folds; matches `scipy.stats.ttest_rel` |
| 30 | Grid search over alpha and a preprocessing choice | applied | code | `tune_ridge(X, y)` with a grid that includes `prep__num__scaler` options; best params returned; refit model predicts |
| 31 | Randomized search with a seed | applied | explain | why random search with 20 trials usually beats a 20-point grid when only one or two of five hyperparameters matter, and why the seed must be fixed for a reproducible result; checklist: "distinct values per important parameter", "budget", "random_state"
| 32 | Successive halving | deep | trace | `⚠ HAND-TRACE` given `n_candidates=12, factor=3, min_resources=100`, print the candidates and resources per round (documented formula) |
| 33 | Nested CV: the honest score of a search | challenge | code | `nested_cv_score(search, X, y, outer)`; lower than `search.best_score_` on noisy data (the §9.6 optimism) |

## G. Classification inside the API (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 34 | Stratified by default | drill | trace | `⚠ HAND-TRACE` print the CV splitter class that `cross_val_score(..., cv=5)` uses for a classifier and for a regressor (`check_cv(5, y, classifier=...)`) |
| 35 | Tune the decision threshold | applied | code | `tuned_threshold(model, X, y, scorer)` with `TunedThresholdClassifierCV`; the threshold differs from 0.5 on an imbalanced "will it sell" task |
| 36 | Fix the broken calibration | applied | code | `assessment = "fix"`; given code that calibrates on the training data (and uses removed `cv="prefit"`); fix with `CalibratedClassifierCV(FrozenEstimator(model))` on a calibration split; ECE on test improves |
| 37 | Sample weights through a pipeline | deep | code | `fit_weighted(pipe, X, y, w)` passes `ridge__sample_weight=w`; zero weights equal dropping those rows |

## H. Inspecting, saving, debugging (Ch. 11–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 38 | Coefficients with real names | drill | code | `named_coefficients(pipe)` → Series indexed by feature names, sorted by absolute size |
| 39 | Permutation importance on raw columns | challenge | code | `raw_importance(pipe, X_test, y_test, seed)` with `permutation_importance` on the whole pipeline; the planted strong column is first, a pure-noise column ≈ 0 |
| 40 | Partial dependence as numbers | deep | code | `pd_curve(pipe, X, feature, grid)` manual (set column, predict, average); equals `partial_dependence(..., kind="average")` |
| 41 | Save, load, predict one | applied | code | `save(pipe, path)` and `predict_one(path, record)`; loading in a fresh subprocess gives the same prediction |
| 42 | Why must custom classes live in a module? | drill | explain | why `pickle` stores the class by import path, so a class defined in a notebook cannot be loaded by the service; checklist |
| 43 | Audit the inputs | deep | code | `audit_inputs(model, raw_columns)` (§13.1) reports missing and unexpected columns and dtype mismatches before predicting |
| 44 | Silent errors | deep | explain | three silent pipeline errors (column order, unknown category ignored, wrong unit) and the check that catches each; checklist |

## I. Project (Ch. 14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 45 | `tabml`: a reusable tabular pipeline | challenge | code | `assessment = "build"`; `Config`, `build_pipeline(cfg)`, `train(cfg, df)` (returns model + report with CV and test scores + data fingerprint), `save`, and `Predictor(folder).predict/predict_one`; tests run it on the listings regression task and a classification variant; save→load in a subprocess gives identical predictions |

## Counts check

Tiers: drill 15 (1, 2, 4, 5, 6, 8, 11, 15, 18, 23, 27, 28, 34, 38, 42), applied 15 (7, 9, 12, 13, 14, 16, 17, 19, 22, 25, 30, 31, 35, 36, 41),
deep 11 (3, 10, 20, 21, 26, 29, 32, 37, 40, 43, 44), challenge 4 (24, 33, 39, 45).
Kinds: trace 9 (2, 4, 5, 9, 16, 21, 23, 32, 34), explain 5 (10, 26, 31, 42, 44), code 31.
Assessment: explain p010, trace p004, fix p036, build p045 — exactly one each.

## Risks and open questions

- `check_estimator` check names change between versions: the test calls the individual check functions it needs through
  `sklearn.utils.estimator_checks` and skips none silently; if a name is missing the test fails with "update the check name".
- `TargetEncoder` exists since 1.3 (installed 1.9): fine.
- Successive-halving schedule (p032): confirm the printed schedule by running `HalvingGridSearchCV(..., verbose=1)` once while writing.
