## Approach

Every subset of `n` positions is a number from 0 to `2^n - 1` (a bitmask). We build `sums[mask]` in increasing order of
`mask`. `mask & -mask` isolates the lowest set bit `low`; `mask ^ low` is the same subset without that element, a
smaller number, so its sum is already known. Then `sums[mask] = sums[mask ^ low] + a[position of low]`. We count the
masks whose sum equals `t`.

## Code

```python
n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

sums = [0] * (1 << n)
count = 1 if t == 0 else 0           # the empty subset
for mask in range(1, 1 << n):
    low = mask & -mask
    sums[mask] = sums[mask ^ low] + a[low.bit_length() - 1]
    if sums[mask] == t:
        count += 1
print(count)
```

## Complexity

O(2^n) time and O(2^n) space, with O(1) work per subset. For `n = 18` that is 262144 steps, well under a second.
Recomputing each sum from scratch is O(n * 2^n), about 18 times more.

## Another way

Build the sums by doubling: start with `[0]`; for each element `x`, extend the list with every old sum plus `x`.
After all elements the list holds the sum of every subset, and `list.count(t)` gives the answer. For larger `n` (up to
about 40), split the array in two halves and combine the halves with a dict (meet in the middle).
