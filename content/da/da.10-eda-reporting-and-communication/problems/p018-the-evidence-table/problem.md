# The evidence table

Chapter section 5.6. The analysis ends with one row per hypothesis: the estimate, its interval and a **verdict**. The verdict must follow a rule, not a mood.

Write `evidence_table(results)`. `results` is a list of dicts with the keys `hypothesis`, `estimate`, `ci_low`, `ci_high`, `null` (the value meaning "no effect",
for example 1 for a ratio, 0 for a difference), `direction` (`"up"` if the hypothesis predicts an estimate above `null`, `"down"` below) and `margin` (the smallest effect
that would matter, on either side of `null`).

Verdict, checked in this order:

1. `supported`: the whole interval lies on the predicted side (`ci_low > null` for up, `ci_high < null` for down);
2. `not supported`: the whole interval lies on the **opposite** side, **or** the whole interval lies within `null - margin` to `null + margin` (any effect is too small to matter);
3. otherwise `inconclusive`.

Return a DataFrame with the columns `hypothesis`, `estimate`, `CI` (text such as `"2.71 to 3.09"`, two decimals) and `verdict`, one row per result in the input order.

## Example

A ratio of 2.90 with CI 2.71 to 3.09, null 1, direction up: `supported`. A difference of 0.02 with CI -0.03 to 0.05, null 0, margin 0.1: `not supported` (any effect is too small).
