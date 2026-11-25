## Approach

Standardise so the penalty is fair, fit, and read the non-zero coefficients. At a suitable `alpha` the junk features are dropped exactly.

## Code

```python
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler


def lasso_selected(X, y, alpha):
    if alpha < 0:
        raise ValueError("alpha must be non-negative")
    Z = StandardScaler().fit_transform(X)
    coef = Lasso(alpha=alpha).fit(Z, y).coef_
    return [name for name, c in zip(X.columns, coef) if c != 0]
```

## Complexity

One lasso fit (coordinate descent).

## Another way

`LassoCV` chooses `alpha` by cross-validation; it usually keeps a few extra weak features, so a larger alpha (the "one standard error rule") gives a sparser model.
