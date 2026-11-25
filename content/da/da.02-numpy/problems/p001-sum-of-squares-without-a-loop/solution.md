## Approach

The loop of Ch. 1.3 does one Python step per number. NumPy keeps all `n` numbers in one block of `int64`, multiplies them element by element in compiled code, and adds them up in compiled code too. The loop still happens, but inside NumPy. `int(...)` turns the NumPy scalar into a plain Python integer.

## Code

```python
import numpy as np


def sum_squares(n):
    values = np.arange(n, dtype=np.int64)
    return int((values * values).sum())
```

## Complexity

O(n) time and O(n) extra memory (one array of `n` integers, 8 MB for a million). The Python loop is also O(n) but each step costs tens of nanoseconds of interpreter work instead of about one.

## Another way

Mathematics beats both: `(n − 1) · n · (2n − 1) / 6` gives the answer in O(1) (use `//` so it stays an integer). The vectorised version is the point here, because most real data has no closed formula. Note the limit of `int64`: for `n` around `3 * 10**6` the sum passes `9.2 * 10**18` and wraps round silently (Ch. 4.2); Python's own integers never overflow.
