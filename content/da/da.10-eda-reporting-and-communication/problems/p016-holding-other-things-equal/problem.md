# Holding other things equal

Chapter section 5.3. New customers churn more, and (in this company) they also get late boxes more often. A plain comparison of "late" against "not late" then mixes the effect
of lateness with the effect of being new: it is **confounded**. A logistic regression with both columns estimates the effect of `late` **holding `new` equal**.

Write `late_effect(df)`. `df` has one row per customer-week with three 0/1 columns: `churn`, `late` and `new`. Return a dict with:

- `odds_ratio`, `ci_low`, `ci_high`: from a logistic model `churn ~ const + late + new` (`statsmodels`: `sm.GLM(y, sm.add_constant(X), family=sm.families.Binomial()).fit()`),
  the exponentiated coefficient of `late` and its exponentiated 95% interval (`fit.conf_int()`);
- `naive_odds_ratio`: the odds ratio from the 2 x 2 table of `late` against `churn` **without** adjusting:
  `(churners / stayers among late) / (churners / stayers among not late)`.

All four as plain floats.

## Example

In the test's world the true odds ratio of `late` is 2.0. The adjusted estimate lands near 2 (its interval contains 2), while the naive one is about 3.4: it also counts
part of the "new customer" effect.
