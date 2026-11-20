# Problem plan: ds.06 ML algorithms, from scratch and with libraries (60 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.06.p001` … `p060`, folder `pNNN-slug`. Requires ds.05. Libraries: NumPy, pandas,
SciPy, scikit-learn. **XGBoost, LightGBM and UMAP are not installed**: boosting problems use the from-scratch booster and
`sklearn.ensemble.GradientBoosting*` / `HistGradientBoosting*`; UMAP appears only in an explain problem.

**Mix:** 20 drill, 20 applied, 14 deep, 6 challenge. **Kinds:** 45 code, 10 trace, 5 explain.
**assessment:** explain = p054, trace = p020, fix = p016, build = p060.
**★ core set (write first, 24):** 1, 2, 4, 7, 10, 12, 16, 18, 20, 22, 25, 28, 31, 33, 37, 40, 43, 45, 48, 50, 52, 54, 57, 60.
Outcomes: three algorithms matching sklearn (p4, p10, p22, p48, p60), and why t-SNE distances mean nothing (p52–p55).

**Testing notes**
- **The match method of the chapter (§1.2):** every from-scratch model is compared with its scikit-learn twin on seeded data from
  `regression_data(seed)` / `classification_data(seed)` (§13.3, in `conftest.py`) using the chapter's `compare(name, ours, theirs, tol)`.
  Tolerances: closed forms `1e-8`; Newton/gradient descent `1e-4` on coefficients after convergence; probabilities `1e-6`.
  Settings must be aligned exactly as the chapter does (e.g. `LogisticRegression(C=..., tol=1e-10, max_iter=...)`, `penalty` on weights
  only, `GaussianNB(var_smoothing=...)` epsilon) — the `problem.md` lists them.
- **Trees:** match `DecisionTreeClassifier(random_state=0)` on data **without tied split gains** (continuous random features); compare
  predictions and the preorder of `(feature, threshold)` (`preorder` / `sk_preorder`, §6.4). A tie test is a separate trace problem.
- **Random parts** (forest bootstrap, k-means++ init, mini-batch order) are matched **statistically** (accuracy within 0.03 of sklearn
  averaged over 3 seeds) or by passing the same initial centres/indices in — never by expecting the same random stream as sklearn.
- Sizes: n ≤ 500, d ≤ 10; trees depth ≤ 6; forests ≤ 25 trees; boosting ≤ 50 stages; t-SNE on ≤ 300 points with `perplexity=30`,
  `max_iter=500`. Each file ≤ ~20 s (measure the forest and t-SNE ones).
- Data shipped with sklearn only: `load_iris`, `load_digits`, `load_breast_cancer`.

## A. The method and linear models (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A comparison helper | drill | code | `compare(name, ours, theirs, tol)` returns `(ok, max_abs_diff)` and a one-line report; shape mismatch raises `ValueError` |
| 2 | Normal equations with an intercept | drill | code | `linreg_closed(X, y)` with `add_ones`; equals `LinearRegression` `coef_` and `intercept_` within 1e-8 |
| 3 | Linear regression by gradient descent | applied | code | `linreg_gd(X, y, lr, epochs, tol)` on standardised data; within 1e-4 of the closed form |
| 4 | `LinearRegressionGD` as an estimator | applied | code | class with `fit`, `predict`, `coef_`, `intercept_`; works in `cross_val_score`; matches sklearn |
| 5 | Mini-batch descent | applied | code | `linreg_minibatch(X, y, lr, epochs, batch, seed)`; same seed → same result; final MSE within 2% of the optimum |
| 6 | Ridge in closed form | drill | code | `ridge_closed(X, y, alpha)` without penalising the intercept (centre first); equals `Ridge(alpha)` |
| 7 | Why scaling fixes the valley | drill | trace | `⚠ HAND-TRACE` given iteration counts printed by the chapter's experiment (inline numbers) and the condition numbers, print the label the given rule assigns ("slow valley" / "round bowl") |

## B. Logistic regression (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 8 | A stable sigmoid | drill | code | `sigmoid(z)` with no overflow warning for z = ±1000 (`np.errstate(over="raise")`); symmetric: `σ(−z) = 1 − σ(z)` |
| 9 | The logistic gradient | drill | code | `logreg_grad(theta, X, y, C)` = `Xᵀ(σ(Xθ) − y) + θ/C` (intercept unpenalised); checked numerically |
| 10 | Newton's method | applied | code | `logreg_newton(X, y, C, steps)`; matches `LogisticRegression(C=C)` within 1e-4; converges in < 15 steps |
| 11 | What `C` does | drill | trace | `⚠ HAND-TRACE` coefficient norms for C = 0.01, 1, 100 printed by given code on inline 2-feature data: the learner predicts the order (smallest to largest) and whether separable data blows up at C = 100 |
| 12 | Softmax regression | deep | code | `softmax_gd(X, y, lr, epochs)` for 3 classes; probabilities sum to 1; accuracy on iris ≥ sklearn multinomial − 0.03 |

## C. k-nearest neighbours and Naive Bayes (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | Pairwise squared distances, vectorised | drill | code | `pairwise_sq_dist(A, B)` via `‖a‖² + ‖b‖² − 2a·b`, clipped at 0; equals `scipy.spatial.distance.cdist(...)**2`; 1,000×1,000 in < 1 s (no Python double loop) |
| 14 | KNN classifier | applied | code | `KNN(k)` with majority vote, ties broken by the nearest neighbour; matches `KNeighborsClassifier(k, algorithm="brute")` predictions on data without distance ties |
| 15 | Choose k with CV | applied | code | `best_k(X, y, ks, cv)` returns the k with best CV accuracy; k = 1 overfits (train accuracy 1.0) |
| 16 | Fix the unscaled KNN | applied | code | `assessment = "fix"`; given a KNN pipeline on income (≈ 10⁵) and age (≈ 10¹) without scaling and with `k` chosen on the test set; fix: scaler inside the pipeline, k by CV; tests: accuracy band and spy scaler fit on train only |
| 17 | The curse of dimensionality | deep | code | `distance_contrast(d, n, seed)` = (max − min)/min distance from a random point; falls towards 0 as d grows (monotone for d = 2, 10, 100, 1000) |
| 18 | Gaussian Naive Bayes | applied | code | `GaussianNBScratch` with per-class means, variances (+ `var_smoothing · max variance`), log priors; `predict_proba` matches `GaussianNB` within 1e-6 |
| 19 | Multinomial Naive Bayes for text | applied | code | `MultinomialNBScratch(alpha)` on a count matrix; log-probabilities match `MultinomialNB(alpha)` |
| 20 | Trace a Naive Bayes decision | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` two classes, three words, counts inline, alpha = 1: print each class's log-score (3 decimals) and the predicted class for the message `"free money now"` |
| 21 | How over-confident is Naive Bayes? | deep | explain | with duplicated (correlated) features, why NB probabilities go to 0/1 while ranking stays good; checklist: "independence assumption", "evidence counted twice", "calibrate" |

## D. Decision trees (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | Gini and entropy | drill | code | `gini(counts)`, `entropy(counts)`; `[50,50]` → 0.5 / 1.0; pure → 0; empty raises |
| 23 | Best split of one feature | applied | code | `best_split(x, y)` → threshold (midpoint between sorted unique values, as sklearn) and impurity decrease; brute-force check |
| 24 | Trace the first split | drill | trace | `⚠ HAND-TRACE` 8 inline points with 2 features: print the weighted Gini of each candidate split and the chosen one |
| 25 | A classification tree from scratch | deep | code | `TreeScratch(max_depth, min_samples_leaf)`; same preorder `(feature, threshold)` as `DecisionTreeClassifier(random_state=0)` on tie-free data; same predictions |
| 26 | Ties: when structures differ | deep | trace | `⚠ HAND-TRACE` given two features with equal gain on 6 inline rows, print which feature the chapter's tree chooses (first index) — and the solution explains why sklearn may pick the other (random feature permutation) |
| 27 | Depth and overfitting | drill | code | `depth_curve(X_tr, y_tr, X_val, y_val, depths)` returns train/val accuracy per depth; train accuracy is non-decreasing |
| 28 | Cost-complexity pruning | applied | code | `best_ccp_alpha(X, y, cv)` from `cost_complexity_pruning_path`; the pruned tree is smaller and validates no worse than full depth − 0.01 |
| 29 | A regression tree | deep | code | `RegressionTreeScratch(max_depth)` with variance reduction; matches `DecisionTreeRegressor` predictions on tie-free data |

## E. Ensembles (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Bootstrap samples and out-of-bag rows | drill | trace | `⚠ HAND-TRACE` given a fixed list of bootstrap indices for n = 8 (inline, no randomness), print the in-bag counts per row and the out-of-bag rows; the solution derives the ≈ 36.8% (`(1 − 1/n)ⁿ → 1/e`) by hand
| 31 | A random forest from our tree | applied | code | `ForestScratch(n_trees, max_features, seed)`; accuracy within 0.03 of `RandomForestClassifier` (same settings) averaged over 3 seeds |
| 32 | Why averaging helps: a measurement | deep | code | `variance_of_average(n_trees, rho, sigma)` formula `ρσ² + (1−ρ)σ²/n` and a simulation agreeing within 10% |
| 33 | Gradient boosting for regression | applied | code | `BoostScratch(n_estimators, lr, max_depth)` fitting residuals with sklearn regression trees; **exact** match with `GradientBoostingRegressor(criterion="squared_error", subsample=1.0, init="mean"-equivalent)` predictions (§8.2 shows the exact match) |
| 34 | Learning rate against number of trees | drill | trace | `⚠ HAND-TRACE` boosting a constant target with lr 0.5: print the prediction after 1, 2, 3 stages (each closes half the gap) |
| 35 | Boosting for classification | deep | code | `boost_classifier(X, y, n_estimators, lr, max_depth)` with log-odds and residuals `y − p`; accuracy within 0.02 of `GradientBoostingClassifier` |
| 36 | Histogram boosting in place of LightGBM | applied | explain | LightGBM and XGBoost are not installed; explain what `HistGradientBoosting` shares with them (binned features, histogram split search, native missing values, early stopping) and what you would check when switching libraries on your own machine; checklist
| 37 | Bagging versus boosting | drill | explain | when each helps (variance vs bias), using the two measurements of §7.4 and §8.3; checklist |

## F. Support vector machines (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 38 | The hinge loss | drill | code | `hinge(w, b, X, y)` with labels in {−1, +1}; zero for points beyond the margin |
| 39 | Linear SVM by sub-gradient descent | challenge | code | `linear_svm_subgradient(X, y, C, iters)`; objective within 1% of `SVC(kernel="linear", C)`'s objective on separable-ish data; same predictions on ≥ 98% of points |
| 40 | Find the support vectors | drill | code | `support_vectors(w, b, X, y, tol)` = points with margin ≤ 1 + tol; same set as `SVC.support_` on a clean dataset |
| 41 | Two linear SVMs | deep | trace | `⚠ HAND-TRACE` print which of `SVC(kernel="linear")` and `LinearSVC` penalises the intercept and uses squared hinge by default (documented facts, printed by given code reading `get_params()`) |
| 42 | Kernels: circles | applied | code | `circle_classifier()` returns a pipeline; on `make_circles` RBF reaches ≥ 0.95 accuracy while linear stays ≤ 0.7 |

## G. Clustering (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 43 | Lloyd's k-means | drill | code | `kmeans_lloyd(X, init_centres, max_iter)`; from the same initial centres, same labels and centres as `KMeans(init=centres, n_init=1)` |
| 44 | k-means++ initialisation | applied | code | `kmeans_pp(X, k, seed)`; first centre is a data point; later centres are far (statistical test: on well-separated blobs every blob gets a centre in ≥ 95% of 50 seeds) |
| 45 | DBSCAN from scratch | deep | code | `dbscan_scratch(X, eps, min_samples)`; same clustering as `sklearn.cluster.DBSCAN` up to label renaming (compare with `adjusted_rand_score == 1`); noise = −1 |
| 46 | Trace DBSCAN | drill | trace | `⚠ HAND-TRACE` 9 points on a line, eps = 1.1, min_samples = 3: print core / border / noise for each point |
| 47 | Average-linkage clustering | challenge | code | `agglomerative_average(X)` returns the merge sequence; matches `scipy.cluster.hierarchy.linkage(X, "average")` heights within 1e-9 for n ≤ 30 |
| 48 | Where k-means fails | deep | code | `best_algorithm(name)` for three datasets (blobs, moons, unequal-density) returns the algorithm that recovers the truth (ARI ≥ 0.9): k-means, DBSCAN, … ; tests compute the ARI |
| 49 | Single linkage chains | drill | explain | why single linkage joins two blobs connected by a thin bridge and average linkage does not; checklist |

## H. PCA, t-SNE, UMAP (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 50 | PCA two ways | applied | code | `PCAScratch(n_components)` via SVD of centred X; `explained_variance_ratio_` and transformed data match `PCA` (components up to sign) |
| 51 | Compress digits | applied | code | `components_for_variance(X, 0.9)` on `load_digits`; reconstruction error falls as k grows; result equals `PCA(0.9).n_components_` |
| 52 | PCA before a model | deep | code | `pca_pipeline(k)` inside a pipeline; CV accuracy on digits within 0.02 of no-PCA with far fewer features; PCA fit only on train folds (spy) |
| 53 | Neighbours, not distances | challenge | code | `neighbour_preservation(X, Y, k)` = mean share of each point's k nearest neighbours kept in the embedding; t-SNE keeps more neighbours than random but the ratio of between-cluster distances is not preserved (test checks both on 3 known clusters) |
| 54 | Why t-SNE distances are not meaningful | deep | explain | `assessment = "explain"`; the outcome: using §12.3's known geometry, explain why cluster sizes and gaps in a t-SNE plot carry no meaning, what *is* preserved, and that UMAP has the same limits; checklist in `answer.md` |
| 55 | Different seeds, different pictures | deep | trace | `⚠ HAND-TRACE` given the printed `geometry(Y)` summaries of two t-SNE runs (inline numbers), print what the given "rule for reading a t-SNE" says about each claim (true/false) |

## I. Project (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 56 | Logistic regression estimator class | applied | code | `LogisticRegressionNewton(C)` estimator (fit/predict/predict_proba/coef_); passes the §13.3 match test for C in {0.1, 1, 10} |
| 57 | Gaussian NB estimator class | applied | code | `GaussianNB` (§13.2) with `classes_`, `theta_`, `var_`; match test |
| 58 | k-means estimator class | challenge | code | `KMeans(n_clusters, init, n_init, seed)` with k-means++ and restarts; inertia within 1% of sklearn's best on blobs |
| 59 | PCA estimator class with inverse transform | challenge | code | `PCA(n_components)` with `fit`, `transform`, `inverse_transform`; round-trip error equals the dropped variance |
| 60 | The from-scratch library and its report | challenge | code | `assessment = "build"`; the §13 library: `LinearRegressionGD`, `LogisticRegressionNewton`, `GaussianNB`, `KMeans`, `PCA` in one `solution.py`, plus `comparison_report()` returning a DataFrame (model, metric ours, metric sklearn, max diff, ok); tests are the chapter's §13.3 match tests over 3 seeds |

## Counts check

Tiers: drill 20 (1, 2, 6, 7, 8, 9, 11, 13, 20, 22, 24, 27, 30, 34, 37, 38, 40, 43, 46, 49), applied 20 (3, 4, 5, 10, 14, 15, 16, 18, 19, 23, 28, 31, 33, 36, 42, 44, 50, 51, 56, 57),
deep 14 (12, 17, 21, 25, 26, 29, 32, 35, 41, 45, 48, 52, 54, 55), challenge 6 (39, 47, 53, 58, 59, 60).
Kinds: trace 10 (7, 11, 20, 24, 26, 30, 34, 41, 46, 55), explain 5 (21, 36, 37, 49, 54), code 45.
Assessment: explain p054, trace p020, fix p016, build p060 — exactly one each.

## Risks and open questions

- p033's exact match depends on sklearn's `init` and loss defaults; check against the installed 1.9.1 while writing and pin the settings in
  `problem.md`.
- t-SNE time under the cap: measure p053 (300 points) — expect a few seconds; drop to 200 points if > 10 s.
- `KMeans(init=array)` warns about `n_init`; pass `n_init=1` explicitly.
