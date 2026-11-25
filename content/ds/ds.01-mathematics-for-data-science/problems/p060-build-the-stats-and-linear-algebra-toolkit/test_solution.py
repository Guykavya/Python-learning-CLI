import math

import numpy as np
import pytest

import ast
import inspect

from scipy import stats

import solution as m

rng0 = np.random.default_rng(60)
Ar = rng0.normal(size=(5, 5)) + 5 * np.eye(5)
br = rng0.normal(size=5)
Xd = rng0.normal(size=(300, 4)) @ rng0.normal(size=(4, 4))
Sym = Ar @ Ar.T
xx, yy = rng0.normal(size=40), rng0.normal(size=40) + 0.3
NAMES = ["norm", "cosine_similarity", "project", "solve", "least_squares", "power_iteration", "pca", "low_rank", "num_grad",
         "grad_check", "gradient_descent", "bayes_posterior", "normal_cdf", "normal_ppf", "binom_pmf", "t_cdf", "t_ppf",
         "mean_ci", "welch_t", "permutation_test", "bootstrap_ci"]


@pytest.fixture(autouse=True)
def _no_shortcuts(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("this toolkit is NumPy only: do not call np.linalg.solve / inv / lstsq / eigh / pinv / matrix_rank.")
    for name in ("solve", "inv", "lstsq", "eigh", "eig", "pinv", "matrix_rank"):
        monkeypatch.setattr(np.linalg, name, boom)


def test_module_is_numpy_only_and_documented():
    tree = ast.parse(inspect.getsource(m))
    imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"math", "numpy"}, f"only math and numpy may be imported, found {sorted(imported)}."
    missing = [n for n in NAMES if not hasattr(m, n)]
    assert not missing, f"missing functions: {missing}."
    undocumented = [n for n in NAMES if not inspect.getdoc(getattr(m, n))]
    assert not undocumented, f"every function needs a docstring, missing for {undocumented}."


def test_vectors():
    assert np.isclose(m.norm([3, 4, 12]), 13.0), "norm([3, 4, 12]) = 13."
    assert np.isclose(m.cosine_similarity([1, 0], [1, 1]), 1 / math.sqrt(2)), "45 degrees."
    assert np.allclose(m.project([3, 4], [1, 0]), [3, 0]), "shadow on the x axis."
    p = m.project([3, 4], [1, 1])
    assert np.isclose((np.array([3, 4]) - p) @ [1, 1], 0), "the residual is perpendicular to d."


def test_solve_and_singular():
    x = m.solve(Ar, br)
    assert np.allclose(Ar @ x, br), "A @ x must reproduce b."
    assert np.allclose(m.solve([[0, 1], [1, 0]], [4, 7]), [7, 4]), "a zero on the diagonal needs a row swap."
    with pytest.raises(ValueError):
        m.solve([[1, 2], [2, 4]], [1, 2])


def test_least_squares_full_and_deficient_rank():
    assert np.allclose(m.least_squares(Xd, Xd @ [1, 2, 3, 4]), [1, 2, 3, 4]), "full rank: recover the coefficients."
    A = np.c_[np.ones(10), np.arange(10.0), 2 * np.arange(10.0)]
    x = m.least_squares(A, 3 + 0.5 * np.arange(10.0))
    assert np.allclose(x, [3, 0.1, 0.2]), "rank deficient: the minimum-norm solution is [3, 0.1, 0.2]."


def test_eigen_pca_and_low_rank():
    lam = np.linalg.svd(Sym, compute_uv=False)[0]
    val, vec = m.power_iteration(Sym)
    assert np.isclose(val, lam, rtol=1e-6), "largest eigenvalue by power iteration."
    scores, comps, ev = m.pca(Xd, 4)
    assert scores.shape == (300, 4) and comps.shape == (4, 4), "scores are n x k, components k x d."
    assert np.allclose(ev, np.sort(np.linalg.svd(Xd - Xd.mean(0), compute_uv=False) ** 2 / 299)[::-1]), "explained variances use ddof = 1."
    s = np.linalg.svd(Xd, compute_uv=False)
    assert np.isclose(np.linalg.norm(Xd - m.low_rank(Xd, 2)), math.sqrt(float((s[2:] ** 2).sum()))), "Eckart-Young error."


def test_calculus():
    g = m.num_grad(lambda p: p[0] ** 2 * p[1] + 3 * p[1], [2.0, 3.0])
    assert np.allclose(g, [12, 7], atol=1e-6), "gradient of x^2 y + 3 y at (2, 3) is (12, 7)."
    assert m.grad_check(lambda p: float(p @ p), lambda p: 2 * p, np.array([1.0, 2.0])) < 1e-6, "a correct gradient passes."
    assert m.grad_check(lambda p: float(p @ p), lambda p: 3 * p, np.array([1.0, 2.0])) > 0.1, "a wrong gradient is flagged."
    w = m.gradient_descent(lambda w: 2 * (w - np.array([3.0, -1.0])), [0, 0], 0.1, 200)
    assert np.allclose(w, [3, -1]), "descent reaches the minimum; return w only."


def test_probability():
    assert np.isclose(m.bayes_posterior(0.01, 0.99, 0.05), 99 / 594), "classic medical test."
    assert np.isclose(m.normal_cdf(m.normal_ppf(0.975)), 0.975) and np.isclose(m.normal_ppf(0.975), 1.959964, atol=1e-5), "normal round trip."
    assert np.isclose(sum(m.binom_pmf(k, 12, 0.3) for k in range(13)), 1), "the binomial pmf adds up to 1."
    assert np.isclose(sum(k * m.binom_pmf(k, 12, 0.3) for k in range(13)), 3.6), "mean n p."


def test_t_distribution_and_mean_ci():
    assert np.isclose(m.t_ppf(0.975, 9), stats.t.ppf(0.975, 9), atol=1e-4), "t quantile with 9 degrees of freedom."
    assert np.isclose(m.t_ppf(0.975, 29), stats.t.ppf(0.975, 29), atol=1e-4), "t quantile with 29 degrees of freedom."
    assert np.isclose(m.t_cdf(1.5, 7), stats.t.cdf(1.5, 7), atol=1e-5) and np.isclose(m.t_cdf(-1.5, 7), stats.t.cdf(-1.5, 7), atol=1e-5), "t cdf is symmetric."
    ref = stats.t.interval(0.95, len(xx) - 1, loc=xx.mean(), scale=stats.sem(xx))
    assert np.allclose(m.mean_ci(xx), ref, atol=1e-3), "mean_ci must match the scipy interval."


def test_welch_permutation_bootstrap():
    r = stats.ttest_ind(xx, yy, equal_var=False)
    t, df, p = m.welch_t(xx, yy)
    assert np.isclose(t, r.statistic) and np.isclose(df, r.df) and np.isclose(p, r.pvalue, atol=1e-4), "welch_t must match scipy."
    obs, pp = m.permutation_test(xx, yy, reps=3000)
    assert np.isclose(obs, xx.mean() - yy.mean()) and abs(pp - r.pvalue) < 0.05, "permutation p near the Welch p."
    assert m.permutation_test(xx, xx + 5, reps=1000)[1] < 0.01, "a shift of 5 is certainly significant."
    lo, hi = m.bootstrap_ci(xx, np.median, reps=1500)
    assert lo < np.median(xx) < hi, "the bootstrap interval surrounds the median."
