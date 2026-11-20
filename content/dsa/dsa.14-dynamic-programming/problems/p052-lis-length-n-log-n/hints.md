## Hint 1

Keep a list `tails`. `tails[k]` = the smallest last value among all increasing subsequences of length `k + 1` found so far. A smaller last value is always better: anything that extends a subsequence ending in 9 also extends one ending in 5. So we only ever need one candidate per length. The length of `tails` is the LIS length so far.

## Hint 2

For each `x`: if it is bigger than every value in `tails`, it extends the longest subsequence: append. Otherwise find the **first** `k` with `tails[k] >= x` and set `tails[k] = x` (a subsequence of length `k + 1` can now end lower). `tails` stays sorted, so this `k` is found by binary search: `bisect_left(tails, x)`. Why `>=` and not `>`? Test it on `[3, 3]`.

## Hint 3

```
from bisect import bisect_left
tails = []
for x in nums:
    k = bisect_left(tails, x)
    if k == len(tails): tails.append(x)
    else: tails[k] = x
return len(tails)
```
