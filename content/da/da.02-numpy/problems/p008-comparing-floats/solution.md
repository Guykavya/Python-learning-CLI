## Approach

Write the tolerance rule as array expressions. `np.abs(a - b)` is the distance, `atol + rtol * np.abs(b)` the allowed distance, and `<=` gives a boolean mask. `nan` needs no special case: any comparison with `nan` is `False`, which is exactly what we want.

## Code

```python
import numpy as np


def close_mask(a, b, rtol=1e-05, atol=1e-08):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.abs(a - b) <= atol + rtol * np.abs(b)
```

## Complexity

O(n), with two temporary arrays.

## Another way

`np.isclose(a, b, rtol=rtol, atol=atol)` is this exact rule (it also handles `inf` and has `equal_nan=True` if you want two `nan`s to count as close). `np.allclose` answers "are all of them close?" with one boolean. Note the rule is not symmetric: the tolerance uses `|b|`, so `b` should be the reference value.
