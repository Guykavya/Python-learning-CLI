## Hint 1

Which two results attributes give you the interval and the p-value? What does `conf_int()` return as column names?

## Hint 2

```text
ci = result.conf_int()           # DataFrame or array with 2 columns
out = DataFrame(estimate = result.params, ci_low = ci[0], ci_high = ci[1], p = result.pvalues)
if exponentiate: out[first 3 columns] = exp(...)
return out.round(digits)
```
Careful: `conf_int()` returns a DataFrame with columns `0` and `1` when the model was fitted on a DataFrame, and an array when it was fitted on arrays.
