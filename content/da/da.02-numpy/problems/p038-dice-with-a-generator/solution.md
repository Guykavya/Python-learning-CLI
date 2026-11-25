## Approach

Draw all rolls at once with the Generator that was passed in: `rng.integers(1, 7, size=n)` (the upper bound is excluded, like `range`). Count with `np.bincount`, which returns the count of every value from 0 up to the maximum; `minlength=7` guarantees 7 slots even when no 6 appears (or `n = 0`), and `[1:]` drops the 0 slot.

Taking `rng` as an argument (Ch. 13.2) is what makes the function testable and reproducible: the caller decides the seed, and repeated calls continue the same stream instead of repeating it.

## Code

```python
import numpy as np


def simulate_rolls(n, rng):
    rolls = rng.integers(1, 7, size=n)
    return np.bincount(rolls, minlength=7)[1:]
```

## Complexity

O(n) time and memory for the rolls; the counting is one pass in C.

## Another way

`np.unique(rolls, return_counts=True)` gives the counts of the faces that appeared, but drops faces that never came up, so you would need to place them into a length-6 array yourself. `bincount` with `minlength` is simpler for small integer codes.
