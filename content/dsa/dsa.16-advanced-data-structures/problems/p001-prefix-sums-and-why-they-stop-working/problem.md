# Prefix sums and why they stop working

Write a class `PrefixSums` (chapter section 1). Ranges are **half-open and 0-indexed**: `[l, r)` means `a[l], ..., a[r - 1]`, like `a[l:r]`; the empty range `l == r` has sum 0.

- `PrefixSums(a)`: build `self.pre`, a list of `len(a) + 1` numbers with `pre[k] = a[0] + ... + a[k - 1]`;
- `query(l, r)`: the sum of `a[l:r]` in `O(1)`;
- `set(i, v)`: make `a[i] = v` and **repair** `pre` so that later queries are right. Return the **number of entries of `pre` you had to change**.

The return value of `set` is the point of the problem: it shows the price of an update.

## Example

```python
>>> ps = PrefixSums([5, 3, 8, 6, 2, 7, 4, 1])
>>> ps.pre
[0, 5, 8, 16, 22, 24, 31, 35, 36]
>>> ps.query(2, 7), ps.query(0, 8), ps.query(4, 4)
(27, 36, 0)
>>> ps.set(3, 100)          # pre[4] .. pre[8] all contained the old a[3]
5
>>> ps.query(2, 7)
121
>>> ps.set(7, 1)            # a[7] is already 1: is anything repaired?
1
```

## Constraints

- `len(a)` up to 10**6. Queries must be `O(1)`; the tests ask 2 * 10**5 queries over long ranges, where adding up the range each time is far too slow.
- `set(i, v)` changes exactly the entries `pre[i + 1], ..., pre[n]`: return `n - i`, even if the value does not change (the code still has to visit them, or check them).

## Think about

1. Which entries of `pre` contain `a[i]`? How many are there for `i = 0`?
2. If half of 10**5 operations are `set` with random `i`, about how many entries do you repair in total? Compare with `log2(10**5) ≈ 17` per operation for the trees of this module.
