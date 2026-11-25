# Residuals versus fitted, as numbers

Chapter section 9.1. The residual-versus-fitted plot shows heteroscedasticity as a **funnel**: the residuals fan out as the fitted value grows. Turn that picture into a number.

Write `funnel_ratio(result)`. It takes a fitted OLS results object, splits the observations into thirds by **fitted value** (use the 1/3 and 2/3 quantiles of `result.fittedvalues`), and returns

```text
std of residuals where fitted >= the 2/3 quantile   /   std of residuals where fitted <= the 1/3 quantile
```

as a float (`np.std` with `ddof=1`). A ratio near 1 means constant spread; a ratio far above 1 means the spread grows with the fitted value.

## Example

```text
funnel_ratio(res_clean)   ->  about 1.0
funnel_ratio(res_hetero)  ->  about 7      (spread grows with x)
```
