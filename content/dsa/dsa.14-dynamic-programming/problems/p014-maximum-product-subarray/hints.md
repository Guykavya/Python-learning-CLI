## Hint 1

Multiplying by a negative number swaps big and small: the **smallest** (most negative) product ending at `i - 1`, times a negative `nums[i]`, can be the **largest** product ending at `i`. So keep two values per position: `hi(i)` = the largest product of a block ending at `i`, and `lo(i)` = the smallest.

## Hint 2

A block ending at `i` is `nums[i]` alone, or it extends a block ending at `i - 1`. So both `hi(i)` and `lo(i)` are among the three candidates `nums[i]`, `hi(i-1) * nums[i]`, `lo(i-1) * nums[i]`. The candidate `nums[i]` alone also handles zeros: after a 0, both `hi` and `lo` restart.

## Hint 3

```
hi = lo = best = nums[0]
for x in nums[1:]:
    candidates = (x, hi * x, lo * x)
    hi, lo = max(candidates), min(candidates)     # both from the OLD hi and lo
    best = max(best, hi)
return best
```
