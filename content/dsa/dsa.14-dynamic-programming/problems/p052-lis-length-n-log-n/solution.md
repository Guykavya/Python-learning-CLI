## Approach

Change the state (chapter section 13). Instead of "the best length ending at `i`", keep for **each length** the best ending:

> `tails[k]` = the smallest last value of any increasing subsequence of length `k + 1` seen so far.

Smaller is better, because whatever can follow a larger ending can also follow a smaller one. `tails` is strictly increasing: if a subsequence of length `k + 2` ends in `v`, dropping its last item gives one of length `k + 1` that ends below `v`, so `tails[k] < tails[k + 1]`.

For a new number `x`:

- if `x` is larger than every entry, a subsequence of length `len(tails)` can be extended: **append**;
- otherwise let `k` be the first position with `tails[k] >= x`. The subsequence of length `k` (ending at `tails[k-1] < x`) extended by `x` has length `k + 1` and ends at `x <= tails[k]`: **replace**.

```python
from bisect import bisect_left


def lis_len(nums):
    tails = []                           # tails[k]: smallest end of an increasing run of length k+1
    for x in nums:
        k = bisect_left(tails, x)        # first tails[k] >= x
        if k == len(tails):
            tails.append(x)              # x extends the longest one
        else:
            tails[k] = x                 # a length-(k+1) subsequence can now end lower
    return len(tails)
```

**`bisect_left`, not `bisect_right`.** If `x` equals some `tails[k]`, `bisect_left` returns that `k` and `x` replaces an equal value: nothing changes, which is right because `x` cannot extend a subsequence ending in an equal value. `bisect_right` would skip past the equal value and append: that counts non-decreasing subsequences, and `[3, 3]` would give 2.

The final `tails` is **not** necessarily a real subsequence (for `[2, 5, 3, 1]` it ends as `[1, 3]`); only its length is meaningful.

## Complexity

`O(n log n)` time: one binary search per number. `O(n)` space.

## Another way

Coordinate-compress the values to `0..m-1`, then compute `f[i] = 1 + max(f[j] : nums[j] < nums[i])` with a structure that answers "maximum over all values below `v`" in `O(log n)` (a Fenwick or segment tree, as in dsa.10). Also `O(n log n)`, more code, but it generalises (to counting LIS, or weighted LIS).
