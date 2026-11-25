## Approach

Draw all flips at once, `rng.integers(0, 2, size=n)`. The running number of heads is `np.cumsum(flips)`, and the number of flips so far is `1, 2, …, n` = `np.arange(1, n + 1)`. Dividing element by element gives every running proportion. Integer divided by integer with `/` is `float64` in NumPy, as in Python.

## Code

```python
import numpy as np


def running_mean_of_flips(n, rng):
    flips = rng.integers(0, 2, size=n)
    return np.cumsum(flips) / np.arange(1, n + 1)
```

## Complexity

O(n) time and memory, all in C.

## Another way

`rng.random(n) < 0.5` gives booleans; `np.cumsum` of booleans counts the `True`s, so the rest is the same. With `rng.binomial(1, p, size=n)` you can simulate an unfair coin with heads probability `p`. Plotting the result (da.09) shows the wide early swings settling towards 0.5, with a spread that shrinks like `0.5 / sqrt(i)` (Ch. 13.7).
