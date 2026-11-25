# Ranks from `argsort`

Chapter sections 9.3, 15.1 and 15.6. Write `ranks(x, descending=False)` for a 1-D array of numbers (ints or floats,
no `nan`). It returns an integer array of the same length where position `i` holds the **rank** of `x[i]`:

- rank 0 is the smallest value (or, with `descending=True`, the largest);
- **ties are broken by position**: of two equal values, the one that comes first in `x` gets the lower rank, in both
  directions;
- every rank `0 .. len(x) - 1` appears exactly once.

No Python loops.

## Example

```python
x = np.array([40, 10, 30, 10])
ranks(x).tolist()                    # [3, 0, 2, 1]
ranks(x, descending=True).tolist()   # [0, 2, 1, 3]
```

In the second line, 40 is the largest (rank 0); the two 10s share the last places, and the first of them (position 1)
gets rank 2.
