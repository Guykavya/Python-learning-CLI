# Segment tree: build and query sum

Write the recursive sum segment tree of chapter section 3, without updates for now. Ranges are **half-open and 0-indexed**: `query(l, r)` is the sum of `a[l:r]`, and `query(l, l)` is 0.

- `SegTree(a)`: build the tree in a flat list `self.t` of size `4 * len(a)`: node `1` is the root and covers `[0, n)`; node `i` covering `[lo, hi)` has the children `2i` for `[lo, mid)` and `2i + 1` for `[mid, hi)`, with `mid = (lo + hi) // 2`;
- `query(l, r)`: the sum of `a[l:r]`, visiting `O(log n)` nodes.

## Example

```python
>>> st = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
>>> st.t[1:16]
[36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1]
>>> st.query(2, 7), st.query(0, 8), st.query(3, 4), st.query(5, 5)
(27, 36, 6, 0)
>>> SegTree([42]).query(0, 1)
42
```

## Constraints

- `1 <= len(a) <= 2 * 10**5`, any length (not only powers of two); values are integers.
- The tests check `t` for a few small arrays, compare `query` with `sum(a[l:r])` on random ranges, then ask 10**5 queries over long ranges of a 2 * 10**5 array: adding up each range is too slow.

## Think about

1. What are the three cases of the query, and what does each return?
2. Why `r <= lo or hi <= l` for "no overlap", and not `<`?
3. For `n = 5`, which node indices does the build use? Why is `4n` enough?
