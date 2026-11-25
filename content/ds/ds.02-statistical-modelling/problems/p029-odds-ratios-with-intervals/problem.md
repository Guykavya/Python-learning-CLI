# Odds ratios with intervals

Chapter section 13.5. In a logistic model each coefficient is a change in **log-odds**. Taking `exp` turns it into an **odds ratio**: the factor by which the odds are multiplied for a one-unit rise in the predictor. An odds ratio of 1 means no effect.

Write `odds_ratios(result)` for a fitted statsmodels logistic result. Return a DataFrame with one row per parameter (index = the parameter names, in model order) and the columns, in this order:

`odds_ratio`, `ci_low`, `ci_high`, `p`

The first three are `exp` of the coefficient and of the two ends of its 95% confidence interval; `p` is the coefficient's p-value, unchanged. Round everything to 3 decimals **after** the `exp`.

## Example

```text
odds_ratios(res)
          odds_ratio  ci_low  ci_high      p
const          0.612   0.45    0.83     0.002
x1             3.320   2.4     4.6      0.0     # one unit of x1 multiplies the odds by 3.3
```
