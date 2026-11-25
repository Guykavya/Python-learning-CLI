## Approach

`theta` is the slope of the regression of `y` on `x`; subtracting `theta * (x - mean(x))` removes the part of `y` that `x` explains and leaves the mean unchanged. The variance falls by the factor `1 - r2`, so a pre-period measure with correlation 0.5 makes the interval about 13% narrower, and one with 0.9 about 56% narrower.

## Code

```python
import numpy as np


def cuped(df, y="converted", x="pre_orders_90d"):
    yv, xv = df[y].astype(float).to_numpy(), df[x].astype(float).to_numpy()
    theta = np.cov(yv, xv)[0, 1] / np.var(xv, ddof=1)
    adjusted = yv - theta * (xv - xv.mean())
    return adjusted, float(theta), float(np.corrcoef(yv, xv)[0, 1] ** 2)
```

## Complexity

O(n).

## Another way

Regress `y` on the group indicator **and** `x` (`y ~ B + x`): the coefficient of B is the same adjusted effect with a standard error from the model.
