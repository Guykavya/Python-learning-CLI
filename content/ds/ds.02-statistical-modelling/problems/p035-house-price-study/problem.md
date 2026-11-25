# House-price study

Chapter section 19 (the module project). You receive a table of 1,200 flats (synthetic, with known truth) and must run a small, honest regression study. The columns are `price_lakh`, `area_sqft`, `bedrooms`, `bathrooms`, `age_years`, `distance_km`, `parking` (0/1) and `locality` (`Central`, `Suburb`, `Outskirts`). The true price depends on area with an **elasticity of 0.85**. The table contains **one impossible row**: an area typed with an extra zero (more than 4,000 sq ft in a data set where every genuine flat is at most 4,000).

Write `house_study(df)`. It must:

1. Remove every row with `area_sqft > 4000` (data-entry errors). Keep a count.
2. Fit, on the cleaned data, `np.log(price_lakh) ~ np.log(area_sqft / 1000) + bedrooms + bathrooms + age_years + C(locality) + parking`.
3. Return a dict with these keys:

| key | value |
|---|---|
| `n_dropped` | number of rows removed in step 1 |
| `n_used` | rows used in the fit |
| `elasticity` | coefficient of `np.log(area_sqft / 1000)` |
| `elasticity_ci` | `(low, high)`, its 95% interval |
| `max_vif` | the largest VIF among the predictors (leave out the intercept) |
| `bp_p` | Breusch-Pagan p-value (LM test) |
| `holdout_rmse` | RMSE **on the log-price scale** of a 75/25 split (`np.random.default_rng(0).permutation(n)` of the cleaned rows, first 75% to fit, last 25% to evaluate) of the same formula |
| `outliers` | list of the **index labels** of rows with `abs(externally studentised residual) > 3` in the full cleaned fit, sorted ascending |

Use `result.get_influence().resid_studentized_external` for the residuals of the last key.

## Example

```text
house_study(make_houses(1200, 2025))
-> {"n_dropped": 1, "n_used": 1199, "elasticity": 0.886, "elasticity_ci": (0.834, 0.939),
    "max_vif": 3.97, "bp_p": 0.047, "holdout_rmse": 0.19, "outliers": [940, ...]}
```
(`940` is a genuine luxury flat priced three times too high for its features; it stays in the data but is reported.)
