## Approach

Two steps: **find the best sum**, then **find the parcels** that make it.

1. A subset with sum `s` leaves `total - s` for the other friend: difference `|total - 2s|`. The best is the largest reachable `s <= total // 2` (subset sum, chapter section 12).
2. To get the parcels back we need more than the 1-D array: keep the 2-D table `f[i][s]` = "the first `i` parcels can make `s`" and walk back from `(n, best)`, as in chapter sections 9 and 10. At row `i`, if `f[i-1][s]` is True the sum can be made **without** parcel `i - 1`, so skip it. If it is False, parcel `i - 1` was needed: take it and continue from `s - nums[i-1]` (which is True in row `i - 1` by the transition).

```python
def split_evenly(nums):
    n = len(nums)
    total = sum(nums)
    half = total // 2
    f = [[False] * (half + 1) for _ in range(n + 1)]   # f[i][s]: first i parcels can make s
    f[0][0] = True
    for i in range(1, n + 1):
        w = nums[i - 1]
        prev, row = f[i - 1], f[i]
        for s in range(half + 1):
            row[s] = prev[s] or (s >= w and prev[s - w])
    best = half
    while not f[n][best]:
        best -= 1
    group = []
    s = best
    for i in range(n, 0, -1):          # walk back: was parcel i-1 needed?
        if not f[i - 1][s]:
            group.append(i - 1)
            s -= nums[i - 1]
    group.reverse()
    return total - 2 * best, group
```

For `[1, 6, 11, 5]`: total 23, half 11, and 11 is reachable, so the difference is 1. Walking back from `(4, 11)`: `f[3][11]` is True (11 alone), so parcel 3 is skipped; `f[2][11]` is False, so parcel 2 (the 11) is taken and `s` becomes 0; the rest is skipped. Group `[2]`: 11 against 12.

Each index is visited once in the walk, so it can never appear twice.

## Complexity

`O(n * total)` time and space for the table (100 x 5,001 booleans at most). The walk back is `O(n)`.

## Another way

Keep only the 1-D array, plus `who[s]` = the index of the parcel that **first** made `s` reachable. With the downward loop, `s - nums[who[s]]` was reachable before that parcel, so its own `who` is a smaller index: following `s -> s - nums[who[s]]` back to 0 lists different parcels. It saves memory (`O(total)`), but the 2-D walk back is easier to prove correct.
