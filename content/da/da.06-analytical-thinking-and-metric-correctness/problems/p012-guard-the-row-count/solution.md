## Approach

Compare two lengths. Growth means a key repeated on the right side (fan-out); shrinkage means a key that found no
partner in an inner join. Two different diseases get two different messages. Returning `after` lets the guard sit in a chain.

## Code

```python
def assert_rows_unchanged(before, after, label):
    n_before, n_after = len(before), len(after)
    if n_after > n_before:
        raise AssertionError(f"fan-out in {label}: {n_before} → {n_after} rows")
    if n_after < n_before:
        raise AssertionError(f"rows lost in {label}: {n_before} → {n_after} rows")
    return after
```

## Complexity

O(1): `len` of a frame is constant time.

## Another way

`left.merge(right, validate="m:1")` checks the *relationship* before the join; this guard checks the *outcome* after it.
Use both: the first says what you expect, the second proves it. With `assert` statements the guard disappears under
`python -O`, which is why it raises explicitly.
