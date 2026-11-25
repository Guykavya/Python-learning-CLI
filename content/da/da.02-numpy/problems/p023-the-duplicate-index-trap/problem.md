# The duplicate-index trap

Chapter section 9.5. A shop has `n` products, numbered `0` to `n - 1`. Every sale is recorded as a product number in
the array `idx`, and its amount in `amounts`. Write:

- `count_by_index(idx, n)`: an integer array of length `n`, where position `p` holds **how many times** `p` appears in `idx`.
- `add_amounts(totals, idx, amounts)`: a **new** array equal to `totals` plus, for every sale `i`, `amounts[i]` added
  at position `idx[i]`. The same product can appear many times, and every sale must count. `totals` is a float array
  and is not changed.

All values of `idx` are between `0` and `n - 1` (or `len(totals) - 1`). `idx` may be empty. No Python loops.

The obvious line `counts[idx] += 1` is **wrong** when `idx` has duplicates. Find out why before you write the fix.

## Example

```python
count_by_index(np.array([0, 0, 1]), 3).tolist()        # [2, 1, 0]
add_amounts(np.zeros(3), np.array([2, 0, 2]), np.array([5.0, 1.0, 4.0])).tolist()
# [1.0, 0.0, 9.0]
```
