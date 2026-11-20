# Segment tree for gcd

A factory cuts metal bars and wants the longest piece length that divides every bar between two positions on a rack, while single bars are replaced. That is the **greatest common divisor** of a range. Write `GcdTree` (chapter section 5). Ranges are **half-open and 0-indexed**.

- `GcdTree(a)`, `update(i, v)` (`a[i] = v`), `query(l, r)`: `math.gcd` of `a[l:r]`;
- the empty range returns `0`; `gcd(0, 0) = 0`, and `gcd(0, x) = x`.

## Example

```python
>>> gt = GcdTree([12, 18, 30, 8, 20, 45])
>>> gt.query(0, 3), gt.query(2, 5), gt.query(3, 4), gt.query(5, 5)
(6, 2, 8, 0)
>>> gt.update(3, 6)
>>> gt.query(0, 4)
6
```

## Constraints

- `0 <= a[i] <= 10**12`, so zeros may appear. Up to 2 * 10**5 elements and 10**5 operations.

## Think about

1. Why is `0` the identity for gcd, while it was the wrong identity for min?
2. Is gcd associative? Why does that matter for a segment tree?
3. Why is a gcd query over a long range still fast, although `math.gcd` is not `O(1)`?
