# Fix the normaliser that edits your data

Chapter sections 6.3 and 10.6. A teammate wrote `normalise(x)` to rescale data into the range 0 to 1 (min → 0,
max → 1). It "works" in their notebook, and it has **three bugs**. The file `solution.py` already contains this code;
fix it.

```python
import numpy as np


def normalise(x):
    """Rescale x to the range [0, 1]: the minimum becomes 0 and the maximum 1."""
    x -= x.min()
    x /= x.max()
    return x
```

Required behaviour:

- the caller's array is **never changed**, and the result is a new array (it shares no memory with `x`);
- integer input works and gives a float result;
- the result has the same shape as `x` (any number of dimensions; min and max are taken over **all** values);
- a constant array (max == min) gives an array of zeros of the same shape, with **no RuntimeWarning**;
- an empty array raises `ValueError` (as now).

## Symptoms the teammate reported

1. "After `scaled = normalise(prices)` my `prices` array is all between 0 and 1. I needed the real prices!"
2. "`normalise(np.array([3, 5, 9]))` crashes with `UFuncTypeError: Cannot cast ufunc 'divide' output from dtype('float64') to dtype('int64') with casting rule 'same_kind'`."
3. "For a column where every value is 7 I get `nan`s and a 'invalid value encountered in divide' warning."

## Example

```python
prices = np.array([10.0, 15.0, 30.0])
normalise(prices).tolist()          # [0.0, 0.25, 1.0]
prices.tolist()                     # [10.0, 15.0, 30.0]   unchanged
normalise(np.array([3, 5, 9]))      # array([0.        , 0.33333333, 1.        ])
normalise(np.array([7.0, 7.0]))     # array([0., 0.])
```
