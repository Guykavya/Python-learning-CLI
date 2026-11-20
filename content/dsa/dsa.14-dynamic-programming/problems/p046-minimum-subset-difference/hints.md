## Hint 1

If friend A carries sum `s`, friend B carries `total - s` and the difference is `|total - 2s|`. It is smallest for the reachable `s` closest to `total / 2`; you may look only at `s <= total // 2` (a bigger `s` is just the other friend's side). So first find the largest reachable `best <= total // 2`; the difference is `total - 2 * best`.

## Hint 2

To know **which** parcels make `best`, keep the whole 2-D table, as in the 2-D knapsack: `f[i][s]` = "some subset of the first `i` parcels sums to `s`". `f[i][s] = f[i-1][s] or (s >= nums[i-1] and f[i-1][s - nums[i-1]])`. Then walk back from `(n, best)`: if `f[i-1][s]` is already True, parcel `i - 1` is not needed; otherwise it **must** be taken: record `i - 1` and subtract its weight.

## Hint 3

```
half = total // 2
f = (n + 1) x (half + 1) table of False; f[0][0] = True
for i in 1..n:
    for s in 0..half:
        f[i][s] = f[i-1][s] or (s >= w and f[i-1][s - w])     # w = nums[i-1]
best = largest s with f[n][s]
group = []; s = best
for i from n down to 1:
    if not f[i-1][s]:          # parcel i-1 was needed
        group.append(i-1); s -= nums[i-1]
return total - 2 * best, group
```
