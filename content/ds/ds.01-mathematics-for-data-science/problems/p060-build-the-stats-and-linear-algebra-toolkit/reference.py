"""mathkit: linear algebra, calculus and inference from scratch with NumPy."""
import math

import numpy as np


def norm(v):
    """Length of the vector v (float)."""
    v = np.asarray(v, dtype=float)
    return math.sqrt(float(np.sum(v * v)))


def cosine_similarity(x, y):
    """Cosine of the angle between x and y; ValueError for a zero vector."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    nx, ny = norm(x), norm(y)
    if nx == 0 or ny == 0:
        raise ValueError("cosine is undefined for a zero vector")
    return float(x @ y) / (nx * ny)


def project(a, d):
    """Projection of the vector a onto the direction d."""
    a, d = np.asarray(a, float), np.asarray(d, float)
    return (a @ d) / (d @ d) * d


def solve(A, b):
    """Solve A x = b by Gaussian elimination with partial pivoting; ValueError if A is singular."""
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    scale = max(float(np.abs(A).max()), 1e-300)
    for col in range(n):
        piv = col + int(np.argmax(np.abs(A[col:, col])))
        if abs(A[piv, col]) < 1e-12 * scale:
            raise ValueError("singular matrix")
        if piv != col:
            A[[col, piv]] = A[[piv, col]]
            b[[col, piv]] = b[[piv, col]]
        for row in range(col + 1, n):
            f = A[row, col] / A[col, col]
            A[row, col:] -= f * A[col, col:]
            b[row] -= f * b[col]
    x = np.zeros(n)
    for row in range(n - 1, -1, -1):
        x[row] = (b[row] - A[row, row + 1:] @ x[row + 1:]) / A[row, row]
    return x


def least_squares(A, b):
    """Minimum-norm least-squares solution through the SVD (works for rank-deficient A)."""
    U, s, Vt = np.linalg.svd(np.asarray(A, float), full_matrices=False)
    s_inv = np.where(s > 1e-10 * s.max(), 1.0 / np.where(s == 0, 1.0, s), 0.0)
    return (Vt.T * s_inv) @ (U.T @ np.asarray(b, float))


def power_iteration(A, steps=500, seed=0):
    """(largest eigenvalue, unit eigenvector) of a symmetric matrix by power iteration."""
    A = np.asarray(A, float)
    v = np.random.default_rng(seed).normal(size=A.shape[0])
    v /= np.linalg.norm(v)
    for _ in range(steps):
        w = A @ v
        v = w / np.linalg.norm(w)
    return float(v @ A @ v), v


def pca(X, k):
    """(scores n x k, components k x d, explained variances of the k largest components) of X."""
    X = np.asarray(X, float)
    Xc = X - X.mean(axis=0)
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:k].T, Vt[:k], (s ** 2 / (len(Xc) - 1))[:k]


def low_rank(M, k):
    """Best rank-k approximation of the matrix M."""
    U, s, Vt = np.linalg.svd(np.asarray(M, float), full_matrices=False)
    return (U[:, :k] * s[:k]) @ Vt[:k]


def num_grad(f, p, h=1e-5):
    """Central-difference gradient of f at the point p (a vector)."""
    p = np.asarray(p, dtype=float)
    g = np.zeros_like(p)
    for i in range(len(p)):
        step = np.zeros_like(p)
        step[i] = h
        g[i] = (f(p + step) - f(p - step)) / (2 * h)
    return g


def grad_check(f, grad, p, h=1e-5):
    """Relative error between the analytic gradient grad(p) and the numerical gradient of f."""
    a = np.asarray(grad(p), float)
    n_ = num_grad(f, p, h)
    denom = np.linalg.norm(a) + np.linalg.norm(n_)
    return 0.0 if denom == 0 else float(np.linalg.norm(a - n_) / denom)


def gradient_descent(grad, w0, lr, steps):
    """Final w after `steps` steps of w <- w - lr * grad(w), starting at w0."""
    w = np.array(w0, dtype=float)
    for _ in range(steps):
        w = w - lr * grad(w)
    return w


def bayes_posterior(prior, sensitivity, false_positive_rate):
    """P(sick | positive test) from the prior, the sensitivity and the false positive rate."""
    return sensitivity * prior / (sensitivity * prior + false_positive_rate * (1 - prior))


def normal_cdf(x, mu=0.0, sigma=1.0):
    """P(X <= x) for X ~ Normal(mu, sigma^2)."""
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))


def normal_ppf(q, mu=0.0, sigma=1.0):
    """The x with P(X <= x) = q for X ~ Normal(mu, sigma^2), by bisection."""
    if not 0.0 < q < 1.0:
        raise ValueError("q must be strictly between 0 and 1")
    lo, hi = -40.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if normal_cdf(mid) < q else (lo, mid)
    return mu + sigma * (lo + hi) / 2


def binom_pmf(k, n, p):
    """P(K = k) for K ~ Binomial(n, p), computed in log-space."""
    if k < 0 or k > n:
        return 0.0
    if p == 0:
        return 1.0 if k == 0 else 0.0
    if p == 1:
        return 1.0 if k == n else 0.0
    logp = (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log1p(-p))
    return math.exp(logp)


def t_cdf(x, df, steps=2001):
    """P(T <= x) for the t-distribution with df degrees of freedom (trapezoid rule)."""
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    grid = np.linspace(0.0, abs(x), steps)
    dens = c * (1 + grid ** 2 / df) ** (-(df + 1) / 2)
    area = float(np.sum((dens[1:] + dens[:-1]) / 2 * np.diff(grid)))
    return 0.5 + math.copysign(area, x)


def t_ppf(q, df):
    """The x with P(T <= x) = q for the t-distribution, by bisection on t_cdf."""
    lo, hi = -200.0, 200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return (lo + hi) / 2


def mean_ci(x, level=0.95):
    """(low, high) t confidence interval for the mean of x."""
    x = np.asarray(x, float)
    se = x.std(ddof=1) / math.sqrt(len(x))
    q = t_ppf(0.5 + level / 2, len(x) - 1)
    return float(x.mean() - q * se), float(x.mean() + q * se)


def welch_t(a, b):
    """(t, df, two-sided p) of Welch's t-test for the means of a and b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    return float(t), float(df), 2 * (1 - t_cdf(abs(t), df))


def permutation_test(a, b, stat=lambda x, y: x.mean() - y.mean(), reps=10000, seed=0):
    """(observed statistic, two-sided permutation p-value) for the groups a and b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed)
    obs = stat(a, b)
    pooled = np.concatenate([a, b])
    count = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        count += abs(stat(pooled[:len(a)], pooled[len(a):])) >= abs(obs) - 1e-12
    return float(obs), (count + 1) / (reps + 1)


def bootstrap_ci(x, stat=np.mean, level=0.95, reps=5000, seed=0):
    """Percentile bootstrap interval (low, high) for stat(x)."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    boots = np.array([stat(x[i]) for i in idx])
    a = (1 - level) / 2
    return float(np.quantile(boots, a)), float(np.quantile(boots, 1 - a))
