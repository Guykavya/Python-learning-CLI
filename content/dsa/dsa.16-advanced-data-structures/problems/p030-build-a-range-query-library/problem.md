# Build a range-query library

Build one module, `solution.py`, with the three structures you will reach for most often, all with the same conventions: **0-indexed, half-open ranges** `[l, r)`.

| Class | Methods |
|---|---|
| `FenwickTree(n_or_list)` | `add(i, v)`, `prefix(r)`, `range_sum(l, r)`; the constructor takes either a size `n` (all zeros) or a list, built in `O(n)` |
| `SegmentTree(a, merge, identity)` | `update(i, v)` (`a[i] = v`), `query(l, r)` (merge of `a[l:r]` **in order**, `identity` if empty); iterative, size `2n`, any associative `merge` |
| `SparseTable(a, f)` | `query(l, r)` for `l < r` in `O(1)`; `f` is idempotent (`min`, `max`, `math.gcd`, ...); static |

The test file is one shared **harness**: a single function runs random operations on any structure and compares it with a plain list, and it is used for all three classes (sum, min, gcd, string concatenation, ...). A timed test then runs 10**5 operations on each.

## Example

```python
>>> fw = FenwickTree([5, 3, 8, 6, 2, 7, 4, 1])
>>> fw.range_sum(2, 7), FenwickTree(4).prefix(4)
(27, 0)
>>> st = SegmentTree(list("segment"), lambda x, y: x + y, "")
>>> st.update(0, "S"); st.query(0, 4)
'Segm'
>>> SparseTable([5, 3, 8, 6, 2, 7, 4, 1], min).query(1, 7)
2
```

## Constraints

- Up to 2 * 10**5 elements; every update and query `O(log n)` (Fenwick, segment tree) or `O(1)` (sparse table queries).

## Think about

1. How can `FenwickTree` tell a size from a list in its constructor?
2. Which of the three is the only one that may use a non-commutative `merge`, and what does that require in its query?
3. Which mistakes would a single shared harness catch that hand-written examples might miss?
