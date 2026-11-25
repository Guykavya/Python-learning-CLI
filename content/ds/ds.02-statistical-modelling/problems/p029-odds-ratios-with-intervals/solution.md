## Approach

Exponentiate the coefficient and both interval ends (the interval is built on the log-odds scale, so transform its ends, never recompute from the odds ratio). Leave the p-value alone.

## Code

```python
import numpy as np
import pandas as pd


def odds_ratios(result):
    ci = np.asarray(result.conf_int())
    out = pd.DataFrame({
        "odds_ratio": np.exp(np.asarray(result.params)),
        "ci_low": np.exp(ci[:, 0]),
        "ci_high": np.exp(ci[:, 1]),
        "p": np.asarray(result.pvalues),
    }, index=list(result.model.exog_names))
    return out.round(3)
```

## Complexity

O(p).

## Another way

`np.exp(result.conf_int())` on the whole DataFrame works when the model was fitted on DataFrame input.
