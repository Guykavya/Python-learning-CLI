# Step rates by segment with Wilson intervals

Chapter section 3.4. Compare the funnel of **mobile** and **desktop** step by step, and say how sure each rate is. A step rate is `sessions at the step / sessions at the previous step` (for the first step, the previous
step is "all sessions of the segment"). The interval of a proportion should be a **Wilson** interval: it behaves well for small counts and rates near 0 or 1.

Write `step_rates(df, by, steps)` returning a DataFrame with one row per segment and step and the columns `[by, "step", "n_prev", "n", "rate %", "CI low", "CI high"]`:

- rows sorted by segment (ascending), and inside a segment in the order of `steps`;
- `n_prev`: the sessions at the previous step (all sessions of the segment for the first step); `n`: the sessions at this step (`True` values of the column, **counted independently**, as in the chapter);
- `rate %` and the 95% Wilson limits (`scipy.stats.binomtest(n, n_prev).proportion_ci(method="wilson")`), all in **percent**;
- when `n_prev` is 0 the rate and both limits are `NaN` (no crash).

## Example

Mobile: 100 sessions, 60 viewed, 30 in the cart. Rows: `view` with `n_prev = 100, n = 60, rate = 60.0`; `cart` with `n_prev = 60, n = 30, rate = 50.0`.
