## Approach

Simulate the repeated study: draw, build the interval, check whether it contains the truth, and report the share of successes.

## Code

```python
def coverage(ci_fn, sampler, truth, reps, rng):
    hits = 0
    for _ in range(reps):
        lo, hi = ci_fn(sampler(rng))
        hits += lo <= truth <= hi
    return hits / reps
```

## Complexity

O(reps x cost of one sample and interval).

## Another way

The same function shows why wrong formulas matter: replace `ci_mean` by "mean +- 1.96 x s" (the standard deviation, not the standard error) and the coverage becomes almost 100%: the interval is valid but uselessly wide. Also try n = 5 with 1.96 instead of the t quantile: coverage falls below 95%.
