## Approach

Run the test on the residuals, and report both kinds of standard errors side by side so the reader sees how much they differ.

## Code

```python
import numpy as np
from statsmodels.stats.diagnostic import het_breuschpagan


def hetero_check(result):
    lm, lm_p, f, f_p = het_breuschpagan(result.resid, result.model.exog)
    robust = result.get_robustcov_results(cov_type="HC3")
    return {
        "bp_p": float(lm_p),
        "se_ordinary": np.asarray(result.bse),
        "se_robust": np.asarray(robust.bse),
    }
```

## Complexity

O(n p^2).

## Another way

`result = smf.ols(...).fit(cov_type="HC3")` gives robust standard errors in the summary directly. With robust errors the coefficients do not change; only the standard errors, intervals and p-values do.
