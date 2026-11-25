# How stable is the threshold?

Chapter section 10. The best threshold on a validation set is an **estimate**: a different validation sample would give a different threshold. Measure how much it moves.

Write `threshold_stability(y, p, cost, grid, reps=100, seed=0)` returning `(lo, hi)`, the **5th and 95th percentiles** (`np.percentile`) of the best threshold over bootstrap resamples:

- one `rng = np.random.default_rng(seed)`; each repetition draws `idx = rng.integers(0, n, n)`
- on the resample, the best threshold is the one in `grid` with the lowest total cost (predict positive when `p >= t`; `cost` has any of the keys `tn, fp, fn, tp`, missing ones cost 0; first in `grid` on a tie)

## Example

```text
2,000 calibrated predictions, cost {"fp": 20, "fn": 100}:  (0.12, 0.23)    # around the theoretical 0.167
20,000 predictions:                                         (0.15, 0.19)    # more data, a tighter range
```
