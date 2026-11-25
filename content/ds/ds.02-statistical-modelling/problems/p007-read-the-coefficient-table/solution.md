## Approach

Collect the four pieces into one tidy table, transform the three on the log scale if asked, and round at the end (rounding before `exp` would compound the error).

## Code

```python
import numpy as np
import pandas as pd


def coef_report(result, exponentiate=False, digits=3):
    ci = np.asarray(result.conf_int())
    out = pd.DataFrame({
        "estimate": np.asarray(result.params),
        "ci_low": ci[:, 0],
        "ci_high": ci[:, 1],
        "p": np.asarray(result.pvalues),
    }, index=list(result.model.exog_names))
    if exponentiate:
        out[["estimate", "ci_low", "ci_high"]] = np.exp(out[["estimate", "ci_low", "ci_high"]])
    return out.round(digits)
```

## Complexity

O(p).

## Another way

`pd.concat([result.params, result.conf_int(), result.pvalues], axis=1)` and then rename the columns.
