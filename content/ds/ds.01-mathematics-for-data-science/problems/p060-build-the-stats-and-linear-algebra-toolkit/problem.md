# Build the stats and linear-algebra toolkit

Chapter section 16. Gather what the module built into **one** file, `solution.py` (your `mathkit`), using **only NumPy and `math`** (no SciPy, no `np.linalg.solve/inv/lstsq/eigh/matrix_rank/pinv`; `np.linalg.svd` and `np.linalg.norm` are allowed). Each function needs a **docstring** that states what it takes and returns; the test checks for it.

| Group | Functions and behaviour |
|---|---|
| Linear algebra | `norm(v)`; `cosine_similarity(x, y)`; `project(a, d)`; `solve(A, b)` (Gaussian elimination with partial pivoting, raises `ValueError` for a singular matrix); `least_squares(A, b)` (minimum-norm solution through the SVD, works for rank-deficient `A`); `power_iteration(A, steps=500, seed=0)` returns `(value, vector)`; `pca(X, k)` returns **`(scores, components, explained_variance)`** (scores `n x k`, components `k x d`, variances of the `k` largest components, `ddof=1`); `low_rank(M, k)` |
| Calculus | `num_grad(f, p, h=1e-5)`; `grad_check(f, grad, p, h=1e-5)` (relative error); `gradient_descent(grad, w0, lr, steps)` returns the final `w` only |
| Probability | `bayes_posterior(prior, sensitivity, false_positive_rate)`; `normal_cdf(x, mu=0, sigma=1)`; `normal_ppf(q, mu=0, sigma=1)`; `binom_pmf(k, n, p)` |
| Inference | `t_cdf(x, df)` (numerical integration of the t density with the trapezoid rule); `t_ppf(q, df)` (bisection on `t_cdf`); `mean_ci(x, level=0.95)` (uses your `t_ppf`); `welch_t(a, b)` returns `(t, df, p)` (uses your `t_cdf`); `permutation_test(a, b, stat, reps=10000, seed=0)` returns `(observed, p)` with `stat(a, b)` a function of two arrays (default: difference of means); `bootstrap_ci(x, stat=np.mean, level=0.95, reps=5000, seed=0)` |

**Note.** Some functions have the same names as those in earlier problems but different signatures, because this toolkit is self-contained (for example `pca` here returns scores too, and `mean_ci` finds the t quantile itself). Follow the table, not the earlier problems.

## Example

```text
solve([[2, 1], [1, 3]], [3, 5])       ->  [0.8, 1.4]
normal_ppf(0.975)                      ->  1.95996
bootstrap_ci(x, np.median)             ->  (low, high) around the sample median
```

## Hand in for your own version (not tested here)

At least three **mutation checks**: copy a function, inject a bug (drop the square root in `norm`, flip the sign in `gradient_descent`), and confirm that your own tests notice it.
