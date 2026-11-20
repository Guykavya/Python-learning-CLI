# Segment tree for min

A weather station stores hourly temperatures, corrects single readings now and then, and is asked for the **lowest** temperature between two hours. Write `MinTree` (chapter section 5): the segment tree of p003 with `min` instead of `+`. Ranges are **half-open and 0-indexed**.

- `MinTree(a)`, `update(i, v)` (`a[i] = v`), `query(l, r)`: the minimum of `a[l:r]`;
- the empty range `query(l, l)` returns `math.inf`.

## Example

```python
>>> mt = MinTree([5, 3, 8, 6, 2, 7, 4, 1])
>>> mt.query(0, 4), mt.query(4, 8), mt.query(2, 7)
(3, 1, 2)
>>> mt.update(5, -9)
>>> mt.query(2, 7), mt.query(0, 2)
(-9, 3)
>>> mt.query(3, 3)
inf
```

## Constraints

- Values may be negative or positive, up to 10**9 in size. Up to 2 * 10**5 elements and 10**5 operations.

## Think about

1. What must the "no overlap" case return so that it never changes a minimum? Why is `0` wrong?
2. Which lines of the sum tree change, and which stay exactly the same?
