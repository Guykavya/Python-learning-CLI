# Reliability table

Chapter section 11.2. A model is **calibrated** when its probabilities mean what they say: of all customers given about 30%, about 30% churn. A **reliability table** checks this bin by bin.

Write `reliability(y, p, bins=10)` returning a DataFrame with one row per **non-empty** bin and the columns `bin_low, n, predicted, observed`:

- bins are **equal-width** on `[0, 1]`: a probability `p` goes to bin `k = min(floor(p * bins), bins - 1)` (so `p = 1.0` falls in the last bin)
- `bin_low` = `k / bins`, `n` = number of rows in the bin, `predicted` = mean `p` in the bin, `observed` = mean `y` in the bin
- rows in increasing order of `bin_low`; empty bins are left out

## Example

```text
y = [0, 0, 1, 1, 1];  p = [0.05, 0.15, 0.12, 0.95, 0.91]
reliability(y, p, 10)
 bin_low  n  predicted  observed
     0.0  1      0.050       0.0
     0.1  2      0.135       0.5
     0.9  2      0.930       1.0
```
