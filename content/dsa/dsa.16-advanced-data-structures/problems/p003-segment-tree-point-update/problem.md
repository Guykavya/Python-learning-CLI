# Segment tree: point update

Add point updates to the sum segment tree of p002 (chapter section 3). Ranges are **half-open and 0-indexed**.

- `SegTree(a)`, `query(l, r)`: as in p002 (`self.t` of size `4n`, root at index 1);
- `update(i, v)`: set `a[i] = v`, in `O(log n)`.

## Example

```python
>>> st = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
>>> st.update(3, 100)
>>> st.t[1:16]
[130, 116, 14, 8, 108, 9, 5, 5, 3, 8, 100, 2, 7, 4, 1]
>>> st.query(2, 7), st.query(0, 4)
(121, 116)
```

Only `t[1]`, `t[2]`, `t[5]` and `t[11]` changed: the path from the leaf of `a[3]` to the root.

## Constraints

- `1 <= len(a) <= 2 * 10**5`. The tests run 2,000 random operations on arrays of 50 elements against a plain list, then 10**5 mixed operations on 2 * 10**5 elements (queries over long ranges).

## Think about

1. Which nodes contain position `i`? How many are there?
2. In what order must they be fixed: leaf first or root first? Why?
3. `update` sets a value (`a[i] = v`), it does not add. What changes if you forget that?
