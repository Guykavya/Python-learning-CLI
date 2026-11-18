## Hint 1

Let `f(i)` = the best sum of a block that **ends exactly at index `i`**. Such a block is either `nums[i]` alone, or the best block ending at `i - 1` with `nums[i]` added. Which is better depends on whether `f(i - 1)` is positive. What is `f(0)`?

## Hint 2

The best block can end anywhere, so the answer is the max of `f(i)` over **all** `i`, not `f(n - 1)`. Keep it in a second variable as you go.

```
cur = best = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
return best
```
