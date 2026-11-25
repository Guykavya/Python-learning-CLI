## Approach

Count the favourable sequences with `comb(n, k)` and divide by all `2**n` equally likely sequences.

## Code

```python
import math


def p_exactly_k_heads(n, k):
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) / 2 ** n
```

## Complexity

O(1) arithmetic on big integers.

## Another way

`scipy.stats.binom.pmf(k, n, 0.5)` gives the same number.
