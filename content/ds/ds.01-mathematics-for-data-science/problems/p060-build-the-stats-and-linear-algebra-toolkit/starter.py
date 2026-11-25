"""mathkit: linear algebra, calculus and inference from scratch with NumPy (fill in every function)."""
import math

import numpy as np


def norm(v):
    """Length of v."""
    raise NotImplementedError


def cosine_similarity(x, y):
    """Cosine of the angle between x and y."""
    raise NotImplementedError


def project(a, d):
    """Projection of a onto d."""
    raise NotImplementedError


def solve(A, b):
    """Solve A x = b (Gaussian elimination, partial pivoting); ValueError if singular."""
    raise NotImplementedError


def least_squares(A, b):
    """Minimum-norm least-squares solution through the SVD."""
    raise NotImplementedError


def power_iteration(A, steps=500, seed=0):
    """(largest eigenvalue, unit eigenvector) of a symmetric matrix."""
    raise NotImplementedError


def pca(X, k):
    """(scores, components, explained_variance) of the top k principal components."""
    raise NotImplementedError


def low_rank(M, k):
    """Best rank-k approximation of M."""
    raise NotImplementedError


def num_grad(f, p, h=1e-5):
    """Central-difference gradient of f at p."""
    raise NotImplementedError


def grad_check(f, grad, p, h=1e-5):
    """Relative error between grad(p) and the numerical gradient."""
    raise NotImplementedError


def gradient_descent(grad, w0, lr, steps):
    """Final w after `steps` gradient steps."""
    raise NotImplementedError


def bayes_posterior(prior, sensitivity, false_positive_rate):
    """P(sick | positive)."""
    raise NotImplementedError


def normal_cdf(x, mu=0.0, sigma=1.0):
    """Normal cdf."""
    raise NotImplementedError


def normal_ppf(q, mu=0.0, sigma=1.0):
    """Normal quantile function."""
    raise NotImplementedError


def binom_pmf(k, n, p):
    """Binomial pmf."""
    raise NotImplementedError


def t_cdf(x, df, steps=2001):
    """t cdf by numerical integration."""
    raise NotImplementedError


def t_ppf(q, df):
    """t quantile function by bisection."""
    raise NotImplementedError


def mean_ci(x, level=0.95):
    """t confidence interval for the mean."""
    raise NotImplementedError


def welch_t(a, b):
    """(t, df, p) of Welch's t-test."""
    raise NotImplementedError


def permutation_test(a, b, stat=lambda x, y: x.mean() - y.mean(), reps=10000, seed=0):
    """(observed, two-sided p) of a permutation test."""
    raise NotImplementedError


def bootstrap_ci(x, stat=np.mean, level=0.95, reps=5000, seed=0):
    """Percentile bootstrap interval."""
    raise NotImplementedError
