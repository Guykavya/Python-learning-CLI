# Sparse table: range minimum

A climate archive stores 10**5 years of yearly minimum temperatures that never change, and researchers ask a million questions "coldest year value in `[l, r)`". Write `SparseMin` (chapter section 15). Ranges are **half-open and 0-indexed**, and never empty.

- `SparseMin(a)`: build `self.table`, where `table[k][i]` is the minimum of `a[i : i + 2**k]` (row `k` has `n - 2**k + 1` entries);
- `query(l, r)`: the minimum of `a[l:r]` (`l < r`) in **`O(1)`**: two table lookups, no loop.

## Example

```python
>>> sp = SparseMin([5, 3, 8, 6, 2, 7, 4, 1])
>>> for row in sp.table:
...     print(row)
[5, 3, 8, 6, 2, 7, 4, 1]
[3, 3, 6, 2, 2, 4, 1]
[3, 2, 2, 2, 1]
[1]
>>> sp.query(1, 7), sp.query(0, 8), sp.query(4, 5), sp.query(2, 4)
(2, 1, 2, 6)
```

## Constraints

- Up to 2 * 10**5 values; up to 10**6 queries. Precompute the floor of `log2` for every length, so a query does no loop and no `math.log2` call.

## Think about

1. How is row `k` built from row `k - 1`?
2. For `[l, r)` of length `L`, which `k` do you use, and where do the two blocks start?
3. The two blocks may overlap. Why is that fine for minimum?
