# Poisson regression with exposure

Chapter section 15.2. Counts of events depend on **how long (or how much) you watched**: a clinic observed for 6 months sees more cases than one observed for 1 month. The right model is for the **rate** per unit of exposure, with `log(exposure)` as an **offset** (a predictor whose coefficient is fixed at 1).

Write `rate_model(df)`. `df` has columns `count` (events), `exposure` (time or population at risk, positive) and `treated` (0 or 1). Fit a Poisson GLM of `count` on `treated` with `offset = log(exposure)`, and return a dict:

- `"rate_ratio"`: `exp(coefficient of treated)`: how many times higher the event **rate** is in the treated group
- `"ci_low"`, `"ci_high"`: the 95% confidence interval for the rate ratio (exp of the interval ends)

## Example

```text
rate_model(df)  ->  {"rate_ratio": 1.5, "ci_low": 1.41, "ci_high": 1.58}     # treated groups have a 50% higher rate
```
In this data the treated units were also watched for longer, so ignoring exposure would show a rate ratio near 3.
