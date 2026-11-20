## Hint 1

Quick checks first: if `sum(nums) % k != 0`, it is impossible. Let `target = sum(nums) // k`. If any number is bigger than `target`, it is impossible too.

Fill the groups one at a time. Once you know the set `mask` of numbers already placed, you know their sum, and the fill level of the current group is that sum `% target`. So the state is only `mask`: the "which group, how full" information is **redundant** (chapter section 19, "Assigning tasks").

## Hint 2

Let `f[mask]` = `True` if the numbers in `mask` can be placed so that all full groups have sum `target` and the current group is not over `target`. Base: `f[0] = True`. From a reachable `mask` with current fill `r = sum(mask) % target`, a number `i` not in `mask` may be added if `r + nums[i] <= target`. The answer is `f[full]`.

## Hint 3

```
total sum check; target = total // k; any number > target -> False
fill = [-1] * (1 << n)        # -1 = unreachable, else the current group's fill
fill[0] = 0
for mask in 0 .. 2**n - 1:
    if fill[mask] == -1: continue
    for i in 0..n-1:
        if bit i not in mask and fill[mask] + nums[i] <= target:
            fill[mask | 1 << i] = (fill[mask] + nums[i]) % target
return fill[full] == 0
```

Storing the fill instead of `True` saves recomputing the sum of `mask` each time.
