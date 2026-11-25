import numpy as np
from sklearn import linear_model, pipeline, preprocessing


def make_curve(n, noise=0.3, seed=0):
    r = np.random.default_rng(seed)
    x = np.sort(r.uniform(0, 1, n))
    return x.reshape(-1, 1), np.sin(2 * np.pi * x) + r.normal(0, noise, n)


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


def bias_variance(degree, n_train=30, reps=150, noise=0.3, seed=0):
    points = np.linspace(0.05, 0.95, 19)
    P = np.empty((reps, len(points)))
    for r in range(reps):
        X, y = make_curve(n_train, noise, seed=seed + r)
        P[r] = poly_model(degree).fit(X, y).predict(points.reshape(-1, 1))
    bias2 = float(np.mean((P.mean(axis=0) - np.sin(2 * np.pi * points)) ** 2))
    variance = float(np.mean(P.var(axis=0)))
    return bias2, variance
