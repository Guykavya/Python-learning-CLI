## Approach

Each mean is "the number that, repeated n times, gives the same result": same total (arithmetic, weighted), same product (geometric), same total time (harmonic). Logs turn the product into a sum and avoid overflow on long lists.

## Code

```python
import math

def weighted_mean(values, weights):
    if not values or len(values) != len(weights):
        raise ValueError("need equal, non-empty lists")
    if any(w < 0 for w in weights) or sum(weights) == 0:
        raise ValueError("weights must be non-negative and not all zero")
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)

def geometric_mean(values):
    if not values or any(v <= 0 for v in values):
        raise ValueError("need a non-empty list of positive numbers")
    return math.exp(sum(math.log(v) for v in values) / len(values))

def harmonic_mean(values):
    if not values or any(v <= 0 for v in values):
        raise ValueError("need a non-empty list of positive numbers")
    return len(values) / sum(1 / v for v in values)
```

## Complexity

O(n) each.

## Another way

`statistics.fmean(values, weights)`, `statistics.geometric_mean` and `statistics.harmonic_mean` exist (note: the library's `harmonic_mean` returns 0 when a value is 0, here a zero is an error).

For growth in percent, convert to factors first: `+10%` is 1.10, `-10%` is 0.90.
