## Approach

Three bugs, three causes:

1. **In place.** `x -= ...` and `x /= ...` write into the caller's array (Ch. 6.3). If the caller passed a slice, they write into the big array behind it too (Ch. 6.1).
2. **Wrong dtype.** An in-place operation must store its result in `x`'s own dtype. `int64 / int64` gives floats, and `same_kind` casting refuses to put them into an int array: `UFuncTypeError` (Ch. 10.6). The non-in-place `(x - lo) / span` simply makes a new float array.
3. **0 / 0.** For a constant array the span is 0, and `0 / 0` is `nan` with a warning. There is nothing to rescale: decide the answer (zeros) before dividing.

## Code

```python
import numpy as np


def normalise(x):
    """Rescale x to the range [0, 1]: the minimum becomes 0 and the maximum 1."""
    x = np.asarray(x)
    lo = x.min()
    span = x.max() - lo
    if span == 0:
        return np.zeros(x.shape)
    return (x - lo) / span
```

## Complexity

O(n) time, one new array (plus one temporary for `x - lo`).

## Another way

`x = x.astype(float)` at the start makes a private float copy, after which the in-place lines are safe and save one temporary; that is fine if you comment *why* the copy is there. For the constant case `np.divide(x - lo, span, out=np.zeros(x.shape), where=span != 0)` avoids the `if` (Ch. 10.6). Keep the three symptoms as tests, so the bugs cannot come back.
