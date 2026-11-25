## Approach

Simulate the confounded world, fit the long and the short model, and check the algebraic identity `short = long_hours + long_ability * delta`. In a **sample** this identity is exact, not approximate: the short regression's slope is the long slope plus the omitted variable's coefficient times the slope of the omitted variable on the kept one.

## Code

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


def omitted_bias(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    ability = rng.normal(0, 1, n)
    hours = 0.8 * ability + rng.normal(0, 1, n)
    score = 50 + 2 * hours + 5 * ability + rng.normal(0, 3, n)
    df = pd.DataFrame({"ability": ability, "hours": hours, "score": score})
    long = smf.ols("score ~ hours + ability", data=df).fit()
    short = smf.ols("score ~ hours", data=df).fit()
    delta = np.cov(df["ability"], df["hours"])[0, 1] / df["hours"].var()
    return {
        "long_slope": float(long.params["hours"]),
        "short_slope": float(short.params["hours"]),
        "predicted_short": float(long.params["hours"] + long.params["ability"] * delta),
    }
```

## Complexity

O(n).

## Another way

With the true numbers the expected short slope is `2 + 5 * 0.8 / 1.64 = 4.44`. The bias does not shrink as `n` grows; only the interval shrinks around the wrong value.
