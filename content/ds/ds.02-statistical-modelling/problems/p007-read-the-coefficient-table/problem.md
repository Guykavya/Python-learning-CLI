# Read the coefficient table

Chapter section 17.3. Every report should show, for each coefficient: the estimate, its 95% confidence interval and the p-value. For logistic or Poisson models the coefficients are on a log scale, so people often want `exp(...)` of them.

Write `coef_report(result, exponentiate=False, digits=3)` that takes any fitted statsmodels results object and returns a DataFrame:

- index: the parameter names, in the model's order
- columns, in this order: `estimate`, `ci_low`, `ci_high`, `p`
- with `exponentiate=True`, apply `exp` to the first three columns (not to `p`)
- every number rounded to `digits` decimals

## Example

```text
coef_report(res)                       # linear model
          estimate  ci_low  ci_high      p
const       37.105  32.034   42.175    0.0
x1           5.290   4.486    6.094    0.0
coef_report(logit_res, exponentiate=True)   # odds ratios
```
