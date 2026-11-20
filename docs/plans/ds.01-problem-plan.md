# Problem plan: ds.01 Mathematics for data science (60 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.01.p001` … `p060`, folder `pNNN-slug`. Requires da.02 (NumPy): NumPy is the tool,
SciPy appears **only in the tests** as the checker (the chapter's rule).

**Mix:** 20 drill, 20 applied, 14 deep, 6 challenge. **Kinds:** 45 code, 10 trace, 5 explain.
**assessment:** explain = p049, trace = p028, fix = p036, build = p060.
**★ core set (write first, 24):** 1, 2, 5, 9, 12, 15, 18, 22, 25, 26, 28, 29, 33, 36, 38, 41, 43, 46, 49, 50, 53, 55, 57, 60.
These cover both learning outcomes (gradient by hand + numeric check: p26–p29, p36; bootstrap + interpretation: p55–p58).

**Testing notes**
- Function names follow the chapter (`norm`, `cosine_similarity`, `project`, `solve`, `least_squares`, `power_iteration`, `pca`,
  `low_rank`, `num_grad`, `grad_check`, `gradient_descent`, `bayes_posterior`, `binom_pmf`, `normal_cdf`, `normal_ppf`,
  `t_ppf`, `mean_ci`, `welch_t`, `permutation_test`, `bootstrap_ci`), so p060 can gather them into the §16 toolkit.
- Checkers: `np.linalg` (`norm`, `solve`, `lstsq`, `eigh`, `svd`, `pinv`), `scipy.stats` (`binom`, `poisson`, `norm`, `t`,
  `ttest_ind(equal_var=False)`), `math.comb`. Tolerances stated in each assert (`rtol=1e-6` for exact linear algebra,
  `1e-4` for numeric derivatives, `0.02–0.05` absolute for simulation results).
- "Do it yourself" problems forbid the shortcut: the test monkeypatches `np.linalg.solve` / `np.linalg.inv` / `scipy` to raise
  when the problem says "without the library", with the message "this exercise is about doing it by hand".
- Eigenvectors and singular vectors are compared **up to sign** (`abs(dot) ≈ 1`); the message says so.
- Simulation problems take `seed` (or a `rng`) as an argument; the test never hard-codes a simulated number (R3), only checks
  it against the exact formula within a tolerance that the reference meets on 5 seeds.
- Bootstrap/permutation tests keep `reps ≤ 5,000` and `n ≤ 500` so each test file stays under ~10 s.
- Trace problems print rounded values (`f"{x:.3f}"`) or `tolist()`, never NumPy reprs (NumPy 2 prints `np.float64(...)`).

## A. Vectors and matrices (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Length of a vector | drill | code | `norm(v)` with a loop and `sqrt`, no `np.linalg`; zero vector; compare with `np.linalg.norm` on random vectors |
| 2 | Cosine similarity | drill | code | `cosine_similarity(x, y)`; parallel → 1, opposite → −1, perpendicular → 0; zero vector raises `ValueError` (message: "cosine is undefined for a zero vector") |
| 3 | Distance needs scale | applied | code | `standardise(X)` then `distances_from_first(X)`; test shows the nearest row changes after scaling (income vs age data inline) |
| 4 | Project a onto d | drill | code | `project(a, d)`; residual `a - p` is orthogonal to `d` (dot ≈ 0); d not unit length |
| 5 | Matrix product three ways | drill | code | `matmul(A, B)` with loops; shapes (2×3)(3×4); mismatched shapes raise `ValueError`; compare with `@` |
| 6 | Trace the matrix product | drill | trace | `⚠ HAND-TRACE` print each `C[i][j]` as a row-by-column dot product for a 2×2 by 2×3 product |
| 7 | Covariance matrix by hand | applied | code | `cov_matrix(X)` (centre, `Xcᵀ Xc / (n−1)`); symmetric; diagonal = variances; equals `np.cov(X, rowvar=False)` |
| 8 | Which matrices are symmetric, diagonal, identity? | drill | trace | `⚠ HAND-TRACE` four small matrices, print the label each check returns |

## B. Linear systems, rank, least squares (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Gaussian elimination | applied | code | `solve(A, b)` with partial pivoting, without `np.linalg` (monkeypatched); random well-conditioned 5×5 systems; a system that needs pivoting (zero on the diagonal) |
| 10 | Detect a singular system | deep | code | `solve` raises `ValueError("singular")` when a pivot is ~0; rank-deficient 3×3; message names the pivot tolerance |
| 11 | Rank by elimination | challenge | code | `rank(A)` with a tolerance; compare with `np.linalg.matrix_rank` on random low-rank products `U @ V` |
| 12 | Least squares with the normal equations | drill | code | `least_squares(A, b)`; recovers known coefficients from noisy data; equals `np.linalg.lstsq` within 1e-6 |
| 13 | Condition number and lost digits | deep | explain | why `make_near_singular(1e-10)` loses about 10 digits, and why `lstsq`/QR beats forming `AᵀA`; checklist: "condition number", "digits lost ≈ log10(κ)", "AᵀA squares κ" |
| 14 | Why not `inv(A) @ b`? | deep | explain | why `solve(A, b)` (one LU factorisation, reused for many right-hand sides) beats `inv(A) @ b` in speed and accuracy; checklist: "factorise once", "inverse costs more and loses digits", "`best_of` timing from §3.4"

## C. Eigenvalues, PCA, SVD (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Power iteration | drill | code | `power_iteration(A, steps, seed)` returns `(value, vector)`; compare with `np.linalg.eigh` largest; vector up to sign; unit length |
| 16 | Is it an eigenvector? | drill | code | `is_eigenvector(A, v, tol)` returning `(bool, lam)`; zero vector is never one |
| 17 | Trace power iteration | applied | trace | `⚠ HAND-TRACE` three steps on `[[2,1],[1,2]]` from `[1,0]`, printing the normalised vector to 3 decimals |
| 18 | PCA from the covariance matrix | applied | code | `pca(X, k)` returns components and explained-variance ratio; compare with `np.linalg.svd` of centred X (up to sign); ratios sum ≤ 1 |
| 19 | How many components keep 95%? | applied | code | `components_for(X, share)`; data built with 3 strong directions + noise → 3 |
| 20 | Low-rank approximation | applied | code | `low_rank(M, k)`; Frobenius error equals `sqrt(sum of dropped s²)` (Eckart–Young check) |
| 21 | Pseudo-inverse | deep | code | `pinv(A)` from the SVD with a cutoff; matches `np.linalg.pinv`; gives the minimum-norm solution for an underdetermined system |
| 22 | Compression ratio of an image matrix | challenge | code | `compress(M, k)` returns the approximation and the number of stored numbers `k(m+n+1)`; picks the smallest k with relative error < 5% on a synthetic 64×64 "image" |

## D. Derivatives and gradients (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | Numerical derivative | drill | code | `num_deriv(f, x, h)` central difference; within 1e-6 of the exact derivative for `x³`, `sin`, `exp` |
| 24 | The step-size trap | deep | trace | `⚠ HAND-TRACE` errors of the forward difference for h = 1e-1, 1e-5, 1e-12 on `x²` at 1 (printed as `"small"`/`"medium"`/`"large"` labels by a given classifier, so the output is machine-independent) |
| 25 | Derivatives by the rules | drill | code | `derivative_of(name)` returns the derivative function for 6 named functions (polynomial, `exp(2x)`, `log x`, `sigmoid`, product, chain); test compares with `num_deriv` at 20 points |
| 26 | Gradient of a two-input function | drill | code | `grad_f(p)` by hand for `f(x,y) = x²y + 3y`; checked against a numeric gradient |
| 27 | The gradient check | applied | code | `grad_check(f, grad, p, h)` returns the relative error; a correct gradient < 1e-6, a gradient with one sign flipped > 1e-2 |
| 28 | Trace a gradient step | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` two gradient-descent steps on `f(w) = (w−3)²` from 0 with lr 0.1, print `w` and `f(w)` to 4 decimals |
| 29 | Gradient of the MSE | applied | code | `mse_grad(w, X, y)` = `2/n · Xᵀ(Xw − y)`; checked by `grad_check` on random data |
| 30 | Gradient of the log-loss | deep | code | `logloss_grad(w, X, y)` via the chain rule; `grad_check` passes; stable for large `|z|` (no overflow warning: `np.errstate(over="raise")`) |
| 31 | Second derivative: minimum or maximum? | deep | trace | `⚠ HAND-TRACE` `classify_stationary` (given) on `x²` at 0, `−x²` at 0, `x³` at 0, `x⁴` at 0; print each label; the `x⁴` case shows why a zero second derivative says "flat", not "no minimum"
| 32 | Which gradient is wrong? | applied | explain | three hand gradients, one with a missing chain-rule factor; explain how the gradient check reveals it and which term is missing; checklist: "relative error", "chain rule", "inner derivative" |

## E. Gradient descent (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 33 | Gradient descent loop | drill | code | `gradient_descent(grad, w0, lr, steps)` returns the final `w` and the history; reaches the minimum of a quadratic bowl |
| 34 | The learning rate decides | applied | trace | `⚠ HAND-TRACE` 4 steps on `f(w)=w²` from 1 with lr 0.1, 0.5, 1.0, 1.1; print each `w` (decays, jumps to 0, oscillates, diverges) |
| 35 | Fit a regression by descent | applied | code | `fit_linear_gd(X, y, lr, steps)` with an intercept column; matches `lstsq` within 1e-3 on standardised features |
| 36 | Fix the descent that never converges | applied | code | `assessment = "fix"`; given code with the gradient sign flipped and features unscaled, so it diverges; the test checks convergence and that `grad_check` passes on the fixed gradient |
| 37 | Scaling speeds descent | deep | code | `steps_to_converge(X, y, lr, tol)` returns the step count; test shows standardised features need far fewer steps than raw (ratio > 10) |
| 38 | Mini-batch SGD | challenge | code | `sgd(X, y, lr, epochs, batch, seed)`; shuffles each epoch with the given seed (same seed → same result); ends within 5% of the `lstsq` loss |

## F. Probability and Bayes (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | Counting with combinations | drill | code | `p_exactly_k_heads(n, k)` with `math.comb`; sums to 1 over k |
| 40 | Birthday problem: formula and simulation | applied | code | `p_shared_birthday(k)` exact (23 → 0.507); `simulate_birthday(k, trials, seed)` within 0.02 of the exact value |
| 41 | Bayes for a medical test | drill | code | `bayes_posterior(prior, sensitivity, false_positive_rate)`; 1% prior, 99%/5% → about 0.167; prior 0 → 0 |
| 42 | Count people, not probabilities | drill | trace | `⚠ HAND-TRACE` the natural-frequency table for 10,000 people (sick & positive, healthy & positive …) printed as integers |
| 43 | Updating step by step | applied | code | `sequential_posterior(prior, tests)` with a list of results; two positives raise it more than one; a positive then a negative |
| 44 | Monty Hall by simulation | applied | code | `monty_hall(switch, trials, seed)`; switch ≈ 2/3, stay ≈ 1/3 within 0.02 |
| 45 | Bayes or base rate? | deep | explain | why a "99% accurate" test is mostly wrong for a rare disease; checklist: "base rate", "false positives outnumber", "prior" |

## G. Distributions, sampling, CLT (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 46 | Binomial and Poisson pmfs | drill | code | `binom_pmf`, `poisson_pmf` by formula (log-space for big n); compare with `scipy.stats` at many points; n = 1,000 does not overflow |
| 47 | Normal cdf and inverse | applied | code | `normal_cdf` via `math.erf`, `normal_ppf` by bisection; `normal_ppf(0.975) ≈ 1.96`; round-trip within 1e-8 |
| 48 | Mean and variance from a pmf | drill | code | `mean_var(values, probs)`; checks that probs sum to 1 (raises otherwise); die → 3.5 and 35/12 |
| 49 | Explain the central limit theorem | deep | explain | `assessment = "explain"`; in plain words: what the CLT promises about the sample mean of an exponential, what it does not promise (the data do not become normal), and why `σ/√n`; checklist given in `answer.md` |
| 50 | Sampling distribution of the mean | applied | code | `sample_means(draw, n, reps, seed)`; std of the means within 10% of `σ/√n` for n = 4, 16, 64 |
| 51 | Skewness and kurtosis | deep | code | `skewness(x)`, `excess_kurtosis(x)`; compare with `scipy.stats.skew/kurtosis(fisher=True, bias=True)` |

## H. Confidence intervals and tests (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 52 | Mean CI with the t-distribution | drill | code | `mean_ci(x, level)` using `scipy.stats.t.ppf`-equivalent from the chapter (`t_ppf`); compare with scipy's interval within 1e-4 |
| 53 | A coverage experiment | challenge | code | `coverage(ci_fn, n, reps, seed)`; t-interval covers ≈ 0.95 for n = 5; z-interval visibly lower (< 0.93) — the reason for t |
| 54 | Wald against Wilson | deep | trace | `⚠ HAND-TRACE` both intervals for k = 0, n = 20 printed to 3 decimals; Wald gives a zero-width interval, Wilson does not |
| 55 | Welch t-test by hand | applied | code | `welch_t(a, b)` returns `(t, df, p)`; equals `scipy.stats.ttest_ind(equal_var=False)` within 1e-6 |
| 56 | Permutation test | deep | code | `permutation_test(a, b, reps, seed)`; p near the Welch p on normal data; identical groups → p ≈ 1; two-sided |
| 57 | Reading a p-value correctly | deep | trace | `⚠ HAND-TRACE` given 6 statements about `p = 0.03`, print `True`/`False` for each (the code holds the statements and the learner's labels are the answer) |

## I. Bootstrap and the toolkit (Ch. 15–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 58 | Percentile bootstrap interval | applied | code | `bootstrap_ci(x, stat, level, reps, seed)`; for the mean it is close to the t-interval (within 15% width); works for the median; same seed → same interval |
| 59 | When the bootstrap fails | challenge | code | `boot_coverage(n, stat, truth, reps, boot_reps, seed)`; median of n = 50 normal covers ≈ 0.95, the **max** of a uniform covers far less (< 0.7); the test checks both and the message explains why the max fails |
| 60 | Build the stats and linear-algebra toolkit | challenge | code | `assessment = "build"`; the §16 module: `solve`, `least_squares`, `power_iteration`, `pca`, `num_grad`, `grad_check`, `normal_cdf`, `mean_ci`, `welch_t`, `bootstrap_ci` in one `solution.py`; the test is the chapter's §16.3 test set (each checked against NumPy/SciPy) plus the "with_bug" mutations (§16.3) that must be caught |

## Counts check

Tiers: drill 20 (1, 2, 4, 5, 6, 8, 12, 15, 16, 23, 25, 26, 28, 33, 39, 41, 42, 46, 48, 52), applied 20 (3, 7, 9, 17, 18, 19, 20, 27, 29, 32, 34, 35, 36, 40, 43, 44, 47, 50, 55, 58),
deep 14 (10, 13, 14, 21, 24, 30, 31, 37, 45, 49, 51, 54, 56, 57), challenge 6 (11, 22, 38, 53, 59, 60).
Kinds: trace 10 (6, 8, 17, 24, 28, 31, 34, 42, 54, 57), explain 5 (13, 14, 32, 45, 49), code 45.
Assessment: explain p049, trace p028, fix p036, build p060 — exactly one each.

## Risks and open questions

- `t_ppf` from the chapter uses numeric integration; p052 may be slow if the learner copies it with `steps=2001` inside a loop: keep
  test calls ≤ 20.
- Simulation tolerances must be checked on 5 seeds with the reference before shipping.
- The chapter says "scipy not installed: checks skipped": SciPy **is** installed now; tests may use it freely.
