## Approach

`keepdims=True` (Ch. 10.3) keeps the reduced axis with length 1, so the mean of a `(n, m)` table along `axis=1` has shape `(n, 1)` and broadcasts against `(n, m)` row by row; along `axis=0` it is `(1, m)`. The same code therefore works for both axes and for 1-D input.

For a constant column `x - mean` is already all zeros. Dividing it by 1 instead of 0 keeps the zeros and avoids `0 / 0 = nan` and its warning: `np.where(std == 0, 1.0, std)`. This is exactly the chapter's `nptools.zscore`.

## Code

```python
import numpy as np


def zscore(x, axis=0, ddof=0):
    x = np.asarray(x, dtype=float)
    mean = x.mean(axis=axis, keepdims=True)
    std = x.std(axis=axis, ddof=ddof, keepdims=True)
    return (x - mean) / np.where(std == 0, 1.0, std)
```

## Complexity

O(size of x) time, a few temporaries of the same size. `np.asarray(..., dtype=float)` makes a copy for integer input, and the arithmetic builds new arrays, so the input is never changed.

## Another way

`np.divide(x - mean, std, out=np.zeros_like(x), where=std != 0)` writes zeros wherever the std is 0 (Ch. 10.6). It is equivalent; the `np.where` divisor is shorter.
