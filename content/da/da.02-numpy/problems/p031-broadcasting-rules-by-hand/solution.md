## Approach

The chapter's `predict_shape` (Ch. 11.2) is the core: pad every shape on the left with `1`s, then look at one axis at a time. The lengths that are not `1` must agree; `1` stretches to anything, including `0`. Two extra requirements: walk the axes from the right (the direction the rule is stated in) so the error names the first clash met, and raise a `ValueError` instead of returning `None`.

## Code

```python
def broadcast_shape(*shapes):
    if not shapes:
        return ()
    ndim = max(len(s) for s in shapes)
    padded = [(1,) * (ndim - len(s)) + tuple(int(n) for n in s) for s in shapes]
    result = [1] * ndim
    for axis in range(ndim - 1, -1, -1):
        lengths = [s[axis] for s in padded]
        not_one = sorted({n for n in lengths if n != 1})
        if len(not_one) > 1:
            raise ValueError(f"cannot broadcast: axis {axis} has lengths {not_one[0]} and {not_one[1]}")
        result[axis] = not_one[0] if not_one else 1
    return tuple(result)
```

## Complexity

O(k × d) for k shapes of at most d axes. No arrays are created, so even shapes describing terabytes are checked instantly.

## Another way

Reduce pairwise: `functools.reduce(two_shapes, shapes, ())` with a helper for two shapes. It is the same rule; the set version handles any number of shapes in one pass. NumPy's own `np.broadcast_shapes` does exactly this check, and it is what you use in real code.
