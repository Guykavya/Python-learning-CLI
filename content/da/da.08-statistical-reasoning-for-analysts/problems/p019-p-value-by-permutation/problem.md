# p-value by permutation

Chapter section 5. If the null hypothesis ("the group label does not matter") is true, shuffling the labels should produce
differences like the one we saw. A **permutation test** does exactly that: pool the values, shuffle, split into groups of the original
sizes, compute the difference in means, and count how often a shuffled difference is at least as extreme as the observed one.

Write `permutation_p(a, b, reps, rng)` returning the **two-sided** p-value for the difference in means `mean(a) - mean(b)`:

- `d_obs = mean(a) - mean(b)`;
- repeat `reps` times: `rng.permutation` of the pooled values, the first `len(a)` as group A, the rest as group B, `d = mean_A - mean_B`;
- `p = (1 + count(|d| >= |d_obs|)) / (reps + 1)`: the **+1 correction** counts the observed arrangement itself, so p is never exactly 0;
- use only `rng`; with the same seed you must get the same p.

```python
a = np.array([12.0, 15, 14, 16, 13]); b = np.array([10.0, 11, 9, 12, 10])
permutation_p(a, b, 5000, np.random.default_rng(0))     # small, around 0.01
```

## Example

If `a` and `b` have exactly the same values, every shuffle is as extreme as the observed difference (0), so `p = (1 + reps) / (reps + 1) = 1`.
