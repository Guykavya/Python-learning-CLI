## Approach

Prefix sums plus remainders. `k` divides `P[i] - P[j]` exactly when `P[i] % k == P[j] % k`. Walking left to right, the
number of good subarrays ending at `i` equals the number of earlier prefixes (including the empty one, `P[0] = 0`) with
the same remainder as `P[i]`. A dictionary counts them as you go.

Python's `%` with a positive `k` always returns a value in `0..k-1`, even for negative numbers: `-2 % 5 == 3`. That
is the mathematical remainder, so `-2` and `3` (which differ by 5) land in the same bucket, as they should.

## Code

```python
n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

seen = {0: 1}
total = 0
rem = 0
for x in a:
    rem = (rem + x) % k
    total += seen.get(rem, 0)
    seen[rem] = seen.get(rem, 0) + 1
print(total)
```

Example `4 5 0 -2 -3 1`, `k = 5`: remainders after each element are `4 4 4 2 4 0`. The counts added are `0, 1, 2, 0,
3, 1`, total 7.

## Complexity

O(n) time, and O(min(n, k)) memory: the dictionary has at most one key per distinct remainder.

## Another way

Collect all `n + 1` prefix remainders, sort them, and for every run of `c` equal values add `c * (c - 1) / 2` pairs.
That is O(n log n), with no dictionary. When `k` is small you can use a list of size `k` instead of a dictionary.
