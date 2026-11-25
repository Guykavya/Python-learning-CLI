# Comparing floats

Chapter sections 4.3 and 4.6. `0.1 + 0.2 == 0.3` is `False`. Write `close_mask(a, b, rtol=1e-05, atol=1e-08)` that
returns a boolean array, `True` where `a` and `b` are **close**:

```text
|a - b| <= atol + rtol * |b|
```

- `a` and `b` are float arrays of the same shape (no `inf`, but they may contain `nan`).
- Where either value is `nan`, the answer is `False`.
- Do not use `==` to compare the values.

## Example

```python
a = np.array([0.1 + 0.2, 1.0, 1.0, np.nan])
b = np.array([0.3,       1.1, 1.0, np.nan])
close_mask(a, b).tolist()   # [True, False, True, False]
```
