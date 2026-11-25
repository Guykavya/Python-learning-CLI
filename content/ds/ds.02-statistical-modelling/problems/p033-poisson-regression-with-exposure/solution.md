## Approach

The model for the expected count is `mu = exposure * exp(b0 + b1 * treated)`. Taking logs: `log(mu) = log(exposure) + b0 + b1 * treated`. The log of the exposure enters with a fixed coefficient of 1, which is exactly what an offset does.

## Code

```python
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


def rate_model(df):
    model = smf.glm("count ~ treated", data=df, family=sm.families.Poisson(),
                    offset=np.log(df["exposure"]))
    res = model.fit()
    lo, hi = res.conf_int().loc["treated"]
    return {"rate_ratio": float(np.exp(res.params["treated"])),
            "ci_low": float(np.exp(lo)), "ci_high": float(np.exp(hi))}
```

## Complexity

O(n p^2) per IRLS step.

## Another way

Model the rate directly with a weighted fit, or add `np.log(exposure)` as an ordinary predictor to see whether its coefficient is close to 1 (a check of the offset assumption).
