# Fix the diagnostics report

Chapter section 18. A helper `diagnose(result)` should return a dict of numbers for a fitted OLS model. A colleague wrote it, and **three numbers are wrong**. Open `solution.py` (it contains their code), find the bugs and fix them. Do not rewrite everything: each bug is one small change.

The dict must contain these keys, with these meanings:

| key | meaning |
|---|---|
| `r2` | the model's R-squared |
| `bp_p` | the Breusch-Pagan p-value (LM test) of the residuals against the model's design matrix |
| `dw` | Durbin-Watson statistic of the **residuals** |
| `n_high_leverage` | how many rows have leverage `h > 2p/n` (`p` = number of parameters including the constant) |
| `n_cooks_flagged` | how many rows have Cook's distance `D > 4/n` |
| `max_vif` | the largest variance inflation factor **among the predictors** (the constant is not a predictor) |

## Example

```text
res = sm.OLS(y, sm.add_constant(X)).fit()      # three predictors
diagnose(res)
-> {"r2": 0.83, "bp_p": 0.41, "dw": 1.96, "n_high_leverage": 11, "n_cooks_flagged": 4, "max_vif": 1.3}
```

The test compares every key with statsmodels separately, so the failing messages tell you which key is wrong.
