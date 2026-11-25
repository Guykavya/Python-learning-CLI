# Interval for a difference in proportions

Chapter section 4.6. Group 1 had `k1` successes in `n1` trials, group 2 had `k2` in `n2`. The difference `p1 - p2` has the standard error

`SE = sqrt(p1 (1 - p1) / n1 + p2 (1 - p2) / n2)`

and the interval `(p1 - p2) +- z * SE`.

Write `diff_prop_ci(k1, n1, k2, n2, z=1.96)` returning `(difference, (low, high))`.

```python
d, (lo, hi) = diff_prop_ci(130, 1000, 100, 1000)
# d = 0.03, interval (0.0021, 0.0579)
```

## Example

13.0% against 10.0%, 1,000 each: difference 3.0 points, 95% interval 0.2 to 5.8 points. Swapping the groups flips the sign of
all three numbers.
