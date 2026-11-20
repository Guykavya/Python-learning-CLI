# Iterative (bottom-up) segment tree

Write the bottom-up segment tree of chapter section 6: no recursion, a list of exactly `2n` entries, and **any associative** combine, even one where the order matters. Ranges are **half-open and 0-indexed**.

- `IterSeg(a, combine, identity)`: `self.t` has length `2 * len(a)`; the leaves are `t[n + i] = a[i]`, and `t[i] = combine(t[2i], t[2i + 1])` for `i = n - 1` down to `1`;
- `update(i, v)`: `a[i] = v`;
- `query(l, r)`: `combine` of `a[l], a[l + 1], ..., a[r - 1]` **in this order**; `identity` for the empty range.

## Example

```python
>>> it = IterSeg([5, 3, 8, 6, 2, 7, 4, 1], lambda x, y: x + y, 0)
>>> it.t[1:]
[36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1]
>>> it.query(2, 7)
27
>>> words = IterSeg(list("segmenttree"), lambda x, y: x + y, "")   # string concatenation: order matters
>>> words.query(2, 7), words.query(0, 11)
('gment', 'segmenttree')
```

## Constraints

- Any `n >= 1`, not only powers of two. The tests use string concatenation and a matrix product to catch any left/right mix-up, and time 10**5 operations on 2 * 10**5 elements.

## Think about

1. In the query loop, when does the **left** pointer take a node, and when does the **right** pointer?
2. Why must the pieces taken on the left and on the right go into **two different** accumulators?
3. For `n = 5`, some internal nodes join elements that are not neighbours in the array. Why does the query never use such a node?
