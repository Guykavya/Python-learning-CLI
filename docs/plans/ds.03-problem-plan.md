# Problem plan: ds.03 Machine learning fundamentals (40 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.03.p001` … `p040`, folder `pNNN-slug`. Requires ds.02. Libraries: NumPy, pandas,
scikit-learn (no plotting: the chapter prints text tables).

**Mix:** 13 drill, 14 applied, 9 deep, 4 challenge. **Kinds:** 28 code, 8 trace, 4 explain.
**assessment:** explain = p020, trace = p006, fix = p027, build = p040.
**★ core set (write first, 16):** 1, 3, 4, 6, 9, 12, 16, 18, 20, 22, 25, 27, 30, 32, 36, 40. The learning outcome (explain overfitting
with a learning curve) is p016–p020.

**Testing notes**
- Names follow the chapter: `three_way_split`, `make_curve`, `poly_model`, `bias_variance`, `learning_curve_table`, `ridge_fit`,
  `kfold_indices`, `cross_val_manual`, `reg_metrics`, `cls_metrics`, `auc_by_pairs`, `log_loss`, `kmeans`, `Evaluation`,
  `TestSetAlreadyOpened`.
- Data: synthetic from a known rule (`make_curve(n, noise, seed)` in `conftest.py`) or the datasets **bundled with scikit-learn**
  (`load_diabetes`, `load_breast_cancer`: no download). Never `fetch_*` (those download).
- Hand-written metrics and splits are compared with `sklearn.metrics` / `sklearn.model_selection` (`rtol=1e-10`) on random inputs.
- Split problems check **properties**: disjoint, cover all rows, sizes, stratified class shares within one row, same seed → same split,
  different seed → different split. Never a hard-coded index list from a NumPy generator (R3).
- Overfitting/learning-curve problems check **shapes of behaviour** (train error falls with degree; validation error is U-shaped;
  gap shrinks as n grows), with margins the reference meets on 3 seeds.
- Every test file ≤ ~10 s: bias–variance simulations ≤ 200 reps, CV ≤ 5 folds × ≤ 10 candidates on ≤ 500 rows.

## A. The supervised problem and baselines (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Supervised or unsupervised? ✅ | drill | trace | `⚠ HAND-TRACE` given code that labels 8 task descriptions with a keyword rule; the learner predicts its output (and the solution.md explains the two the rule gets wrong) |
| 2 | Features and target from a table ✅ | drill | code | `split_xy(df, target)` returns `X` (DataFrame without target) and `y`; target missing → `KeyError` with a clear message; does not modify `df` |
| 3 | Mean and majority baselines ✅ | drill | code | `baseline_predict(y_train, n, task)` → mean for regression, most frequent class for classification; equals `DummyRegressor/DummyClassifier` |
| 4 | Beat the baseline? ✅ | applied | code | `beats_baseline(model, X_tr, y_tr, X_te, y_te, task)` returns `(model_score, baseline_score, bool)`; a useless model on noise does **not** beat it |

## B. Splits (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Train, validation and test ✅ | drill | code | `three_way_split(X, y, val, test, seed)`; sizes, disjointness, reproducibility |
| 6 | One split is one draw ✅ | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given a tiny deterministic "split" function (rotation by seed, no randomness) and 6 labelled rows, print the test rows and the test accuracy of a fixed rule for seeds 0–2; shows the score moves with the split |
| 7 | Stratified split by hand ✅ | applied | code | `stratified_split(y, test_frac, seed)` returns index arrays; each class's share in test within one row of the overall share; works with a class of 3 rows |
| 8 | Why we keep a test set locked ✅ | drill | explain | why tuning on the test set makes its score optimistic; checklist: "selection uses the data", "best of many", "fresh data only once" |

## C. Overfitting, bias and variance (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Polynomial models of growing degree ✅ | drill | code | `fit_errors(degree, X_tr, y_tr, X_val, y_val)` with `poly_model(degree)`; train RMSE never rises with degree |
| 10 | Find the sweet spot ✅ | applied | code | `best_degree(...)` chooses the degree with the lowest validation RMSE among 1–12 on `make_curve`; answer in 3–6 on 3 seeds |
| 11 | Trace train and validation error ✅ | drill | trace | `⚠ HAND-TRACE` given a printed table of errors (inline numbers) and code that labels each degree "underfit"/"good"/"overfit" by a stated rule, print the labels |
| 12 | Bias and variance by simulation ✅ | deep | code | `bias_variance(degree, n_train, reps, noise, seed)` returns `(bias², variance)` at fixed points; degree 1 has high bias, degree 10 high variance; `bias²+variance+noise² ≈` expected test MSE within 10% |
| 13 | More data: cure or not? ✅ | deep | explain | why more data reduces overfitting of a degree-10 model but does nothing for a degree-1 model on a curve; checklist: "variance falls with n", "bias does not", "learning curve plateaus" |

## D. Learning curves (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | A learning-curve table ✅ | applied | code | `learning_curve_table(make_model, X, y, sizes, val_X, val_y, repeats, seed)` returns rows `(n, train, validation)`; train error rises, validation error falls with n |
| 15 | Learning curve with scikit-learn ✅ | drill | code | `real_curve(est, X, y)` wraps `sklearn.model_selection.learning_curve`; returns a DataFrame with `size, train, validation, gap`; signs flipped for `neg_` scorers |
| 16 | Diagnose from the curve ✅ | applied | code | `diagnose(lc, task)` → `"high variance"`, `"high bias"` or `"fine"` using the chapter's rule (§7.2 / `Evaluation.diagnose`); three synthetic curves |
| 17 | Read four learning curves ✅ | drill | trace | `⚠ HAND-TRACE` four printed curve tables, run through the given `diagnose`; print the four labels |
| 18 | Overfitting, measured ✅ | challenge | code | `overfit_report(X, y, model, seed)` returns the gap at the largest size and whether adding data is expected to help (gap > threshold and still shrinking); deep tree vs linear model on diabetes |
| 19 | Fix with regularisation or data? ✅ | deep | trace | `⚠ HAND-TRACE` given three learning-curve summaries and the chapter's decision table, print the recommended action for each |
| 20 | Explain overfitting with a learning curve ✅ | deep | explain | `assessment = "explain"`; the module's learning outcome: using a printed curve (in `problem.md`), explain what the gap and the plateau say, and what you would try next; checklist in `answer.md` |

## E. Regularisation (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | Ridge in closed form ✅ | drill | code | `ridge_fit(X, y, alpha)` = `(XᵀX + αI)⁻¹Xᵀy` with an **unpenalised** intercept; equals `sklearn.linear_model.Ridge` within 1e-8 |
| 22 | Scale before you penalise ✅ | applied | code | `ridge_pipeline(alpha)` = `make_pipeline(StandardScaler(), Ridge(alpha))`; test shows the unscaled ridge penalises the large-unit feature unequally (coefficient comparison) |
| 23 | The shrinkage path ✅ | deep | explain | why ridge shrinks every coefficient but never to exactly zero, while lasso sets some to zero; uses the printed `ridge_path`/lasso path tables in `problem.md`; checklist: "squared penalty is smooth at 0", "absolute penalty has a corner", "scale first"
| 24 | Lasso zeros out junk ✅ | applied | code | `lasso_selected(X, y, alpha)` returns the names of non-zero coefficients; with 3 true and 7 junk features at the right alpha only the 3 remain (alpha chosen by `LassoCV` with fixed folds) |

## F. Cross-validation and tuning (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | K-fold indices by hand ✅ | drill | code | `kfold_indices(n, k, seed)` returns k test-index arrays; disjoint, cover 0..n−1, sizes differ by ≤ 1 |
| 26 | Cross-validation by hand ✅ | applied | code | `cross_val_manual(make_model, X, y, k, seed, scorer)`; equals `cross_val_score` with the same `KFold(shuffle=True, random_state=seed)` folds (the test passes the folds in to avoid generator differences) |
| 27 | Fix the leaky tuning loop ✅ | applied | code | `assessment = "fix"`; given code that picks alpha by the **test** score and reports that same score; fix: tune with CV on train, score test once; test checks the test set is touched once (a wrapper counts `.score` calls on test data) |
| 28 | Grid search with CV ✅ | applied | code | `tune(model, grid, X, y)` with `GridSearchCV(cv=5)`; returns best params and the CV score; best alpha in the expected range |
| 29 | The optimism of the best of many ✅ | deep | code | `best_of_many_optimism(n_models, seed)` on pure-noise data: the best CV score among many random models is above chance; the fresh test score is not; test checks both |
| 30 | Grouped and time-ordered folds ✅ | applied | code | `choose_cv(kind)` returns `GroupKFold`, `TimeSeriesSplit` or `StratifiedKFold`; test checks no group appears on both sides and time folds never train on the future |

## G. Metrics (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 31 | Regression metrics ✅ | drill | code | `reg_metrics(y, p)` → MAE, RMSE, R², MAPE (raises on zero targets); equals sklearn |
| 32 | Classification metrics from counts ✅ | drill | code | `cls_metrics(TP, FP, FN, TN)`; zero-division cases return 0.0 with no warning |
| 33 | The accuracy trap ✅ | applied | trace | `⚠ HAND-TRACE` 1,000 rows with 20 positives and a model that always says "no": print accuracy, precision, recall, F1 |
| 34 | AUC by counting pairs ✅ | deep | code | `auc_by_pairs(y, score)`; ties count 0.5; equals `roc_auc_score`; O(n log n) version passes n = 20,000 in < 2 s |
| 35 | Log-loss ✅ | applied | trace | `⚠ HAND-TRACE` the log-loss contribution of four predictions (y=1, p=0.9 / 0.5 / 0.1 / 0.0 with eps=1e-15), printed to 3 decimals, and the mean; shows why clipping is needed
| 36 | Pick a metric from the cost ✅ | deep | trace | `⚠ HAND-TRACE` given three business stories and the chapter's decision rule coded as a function, print the chosen metric for each |
| 37 | Macro, micro and weighted ✅ | challenge | code | `multiclass_f1(y, p)` returns the three averages; equals `f1_score(average=...)`; test with an imbalanced 3-class case where they differ |

## H. Unsupervised learning (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 38 | k-means by hand ✅ | deep | code | `kmeans(X, k, iters, seed)` returns centres and labels; inertia never rises across iterations; final inertia within 1% of sklearn `KMeans(n_init=1)` started from the same centres |
| 39 | Choosing k ✅ | challenge | code | `elbow_and_silhouette(X, ks, seed)` returns inertia and silhouette per k; on 4 well-separated blobs silhouette picks 4 |
| 40 | The evaluation framework ✅ | challenge | code | `assessment = "build"`; the §14 `Evaluation` class: `baseline()`, `compare(models)`, `learning_curve(model)`, `diagnose`, `tune(model, grid)`, `final_test(model)`; a second `final_test` call raises `TestSetAlreadyOpened`; tests on diabetes (regression) and breast cancer (classification) |

## Counts check

Tiers: drill 13 (1, 2, 3, 5, 8, 9, 11, 15, 17, 21, 25, 31, 32), applied 14 (4, 6, 7, 10, 14, 16, 22, 24, 26, 27, 28, 30, 33, 35),
deep 9 (12, 13, 19, 20, 23, 29, 34, 36, 38), challenge 4 (18, 37, 39, 40).
Kinds: trace 8 (1, 6, 11, 17, 19, 33, 35, 36), explain 4 (8, 13, 20, 23), code 28.
Assessment: explain p020, trace p006, fix p027, build p040 — exactly one each.

## Risks and open questions

- `learning_curve`/`GridSearchCV` with `n_jobs=None` only: parallel jobs spawn processes that may break the 1 GiB cap.
- `KMeans` default `n_init` changed between sklearn versions: always pass `n_init` explicitly.
- p026 passes folds in so the learner's result does not depend on how sklearn shuffles.
