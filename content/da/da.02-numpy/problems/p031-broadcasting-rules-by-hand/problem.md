# Broadcasting rules by hand

Chapter section 11.2. Write `broadcast_shape(*shapes)`: the shape that NumPy would give to an operation on arrays of these shapes, computed with plain Python from the rules, **without** NumPy's helpers (`np.broadcast_shapes`, `np.broadcast_to`, `np.broadcast_arrays`; the test disables them, so calling one fails).

- Each shape is a tuple (or list) of non-negative integers. `()` is the shape of a scalar.
- Return a **tuple** of `int`s. With no shapes at all, return `()`; with one shape, return it as a tuple.
- Pad every shape with `1`s on the left to the longest length. On each axis, the lengths that are not `1` must all be equal: the result is that length; if every length is `1`, the result is `1`. A length `1` stretches to any length, **including 0**: `(0,)` with `(1,)` gives `(0,)`.
- If an axis has two different lengths, neither of them `1`, raise `ValueError`. Check the axes **from the last to the first** and report the first bad one you meet: the message must contain the words `axis k`, where `k` is that axis's position in the padded result (0-based, counted from the left), and it should show the clashing lengths.

## Example

```python
broadcast_shape((3, 1), (4,))            # (3, 4)
broadcast_shape((5, 1, 4), (3, 1))       # (5, 3, 4)
broadcast_shape((2, 1), (1, 3), (4, 1, 1))   # (4, 2, 3)
broadcast_shape()                        # ()
broadcast_shape((3, 4), (3, 4, 1))
# ValueError: cannot broadcast: axis 1 has lengths 3 and 4
```

In the last example the padded shapes are `(1, 3, 4)` and `(3, 4, 1)`: axis 2 is fine (4 and 1), axis 1 clashes (3 and 4).
