# Standardised coefficients

Chapter section 7.5. Coefficients depend on the units of their variables, so two raw coefficients cannot be compared. If you convert **every** variable (the response too) to a z-score (subtract the mean, divide by the standard deviation) and refit, each coefficient means "the change in `y`, in standard deviations, for a one-standard-deviation change in `x`".

Write `standardised_coefs(df, y, xs)` that returns a `pandas.Series` indexed by the predictor names (no intercept), with the coefficients of that standardised fit. Use the sample standard deviation (`ddof=1`, the pandas default). You may use statsmodels or NumPy.

A useful identity: the standardised coefficient equals `b * sd(x) / sd(y)`, where `b` is the raw coefficient.

## Example

```text
df: hours (sd 2.0), age (sd 10.0), score (sd 8.0); raw slopes 3 per hour and 0.4 per year
standardised_coefs(df, "score", ["hours", "age"])
-> hours 0.75 (3 * 2 / 8),  age 0.5 (0.4 * 10 / 8)      # approximately
```
