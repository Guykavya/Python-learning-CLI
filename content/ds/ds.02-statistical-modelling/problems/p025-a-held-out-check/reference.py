import numpy as np
import statsmodels.formula.api as smf


def holdout_rmse(df, formula, test_frac=0.25, seed=0):
    n = len(df)
    idx = np.random.default_rng(seed).permutation(n)
    cut = int(n * (1 - test_frac))
    train, test = df.iloc[idx[:cut]], df.iloc[idx[cut:]]
    res = smf.ols(formula, data=train).fit()

    def rmse(d):
        return float(np.sqrt(np.mean((d["y"] - res.predict(d)) ** 2)))

    return {"train_rmse": rmse(train), "test_rmse": rmse(test)}
