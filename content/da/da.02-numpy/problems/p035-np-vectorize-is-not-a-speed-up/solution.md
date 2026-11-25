## Approach

The model answer is in `answer.md`. The key fact: `np.vectorize` still calls a Python function once per element, so it inherits Python's per-element cost. Real vectorisation means expressing the rule with whole-array operations (ufuncs, masks, `np.where`/`np.select`), so the loop runs in C.

## Code

```python
fees = np.select(
    [weights <= 1.0, weights <= 5.0],
    [40.0, 40.0 + (weights - 1.0) * 15.0],
    default=100.0 + (weights - 5.0) * 25.0,
)
```

On `[0.5, 1.0, 3.0, 5.0, 8.0]` both versions give `[40, 40, 70, 100, 175]`.

## Complexity

Both are O(n). The difference is the constant: one Python call per element against a handful of C loops over the array. Measure it on your machine; in Ch. 12.3 the gap was a factor of about 33.

## Another way

Nested `np.where(w <= 1.0, 40.0, np.where(w <= 5.0, ..., ...))`, or a "sum of bands" with `np.clip`: `40 + 15 * np.clip(w - 1, 0, 4) + 25 * np.clip(w - 5, 0, None)`, which avoids computing three full branches.
