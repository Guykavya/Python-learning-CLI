import numpy as np


def _naive(train, horizon, season):
    last = np.asarray(train, dtype=float)[-season:]
    return np.array([last[i % season] for i in range(horizon)])


def beats_seasonal_naive(model_fn, df, origins, horizon=28, season=7):
    model_err, naive_err = [], []
    for o in origins:
        train, future = df.iloc[:o], df.iloc[o:o + horizon]
        actual = future["sales"].to_numpy(dtype=float)
        pred = np.asarray(model_fn(train, future.drop(columns="sales")), dtype=float)
        model_err.append(np.mean(np.abs(actual - pred)))
        naive_err.append(np.mean(np.abs(actual - _naive(train["sales"], horizon, season))))
    m, n = float(np.mean(model_err)), float(np.mean(naive_err))
    return m, n, bool(m < n)
