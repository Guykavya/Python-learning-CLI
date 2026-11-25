## Approach

Hold part of the data back. Predictions for the held-out rows use the coefficients learned from the training rows only. A large gap between the two errors is the sign of overfitting.

## Code

```python
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
```

## Complexity

O(n p^2) for the fit, O(n p) for the predictions.

## Another way

Repeat with several random splits (or k-fold cross-validation, the subject of ds.04) and average, because one split of a small data set can be lucky or unlucky.
