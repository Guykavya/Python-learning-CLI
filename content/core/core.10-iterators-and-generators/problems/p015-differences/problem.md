# differences with pairwise

`itertools.pairwise(xs)` gives the overlapping pairs `(x0, x1), (x1, x2), ...`. (It needs Python 3.10+.)

Write `differences(numbers)` in `solution.py`. It returns the list of differences between each number and
the one before it. Use `pairwise`.

**Examples**

```python
differences([1, 4, 9, 16])    # [3, 5, 7]
differences([5, 3, 3, 10])    # [-2, 0, 7]
differences([7])              # []
differences([])               # []
```
