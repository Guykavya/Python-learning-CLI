# Range sum with range update (two Fenwicks)

Range add **and** range sum, without lazy propagation: two Fenwick trees over the difference array (chapter section 11). Ranges are **half-open and 0-indexed**.

- `RangeAddSum(a)`;
- `add(l, r, v)`: add `v` to every element of `a[l:r]`;
- `range_sum(l, r)`: the sum of `a[l:r]`.

Both `O(log n)`.

## Example

```python
>>> rr = RangeAddSum([5, 3, 8, 6, 2, 7, 4, 1])
>>> rr.range_sum(0, 8), rr.range_sum(2, 7)
(36, 27)
>>> rr.add(2, 6, 10)
>>> rr.range_sum(0, 8), rr.range_sum(2, 7), rr.range_sum(0, 2)
(76, 67, 8)
>>> rr.add(0, 8, -1)
>>> rr.range_sum(0, 8), rr.range_sum(3, 5)
(68, 26)
```

## Constraints

- Up to 2 * 10**5 elements and 2 * 10**5 operations on long ranges.

## Think about

1. With the difference array `d` of all the additions, write the sum of the first `p` elements as a formula in `d`. How many times is `d[j]` counted?
2. Why does that formula need **two** prefix sums over `d`: one of `d[j]` and one of `j * d[j]`?
3. Where do the original values go?
