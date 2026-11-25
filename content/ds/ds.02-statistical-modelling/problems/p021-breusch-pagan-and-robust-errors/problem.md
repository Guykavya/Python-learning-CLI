# Breusch-Pagan and robust errors

Chapter section 9.5. When the spread of the errors depends on the predictors, ordinary standard errors are wrong but the coefficients are still unbiased. Two tools: a **test** that detects the problem, and **robust standard errors** that survive it.

Write `hetero_check(result)` for a fitted OLS results object. It returns a dict with three keys:

- `"bp_p"`: the p-value of the Breusch-Pagan test (`statsmodels.stats.diagnostic.het_breuschpagan`, residuals against the model's design matrix)
- `"se_ordinary"`: the ordinary standard errors (`result.bse`) as a NumPy array
- `"se_robust"`: the HC3 robust standard errors as a NumPy array (`result.get_robustcov_results("HC3").bse`, or refit with `cov_type="HC3"`)

## Example

```text
hetero_check(res_hetero)  ->  {"bp_p": 0.0000..., "se_ordinary": array([0.20, 0.08]), "se_robust": array([0.17, 0.16])}
hetero_check(res_clean)   ->  {"bp_p": 0.8..., ...}     # no evidence, and the two kinds of SE agree
```
