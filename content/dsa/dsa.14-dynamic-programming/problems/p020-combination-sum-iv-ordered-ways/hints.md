## Hint 1

Every sequence that sums to `a` ends with some number `x` from `nums`. Take that last `x` away: what is left is **any** sequence that sums to `a - x`. So the number of sequences for `a` is the sum, over every `x <= a`, of the number of sequences for `a - x`.

## Hint 2

That rule needs `f[a - x]` to be **complete** (all numbers allowed) before `f[a]` is computed. So the amounts must be the **outer** loop, going up, and the numbers the inner loop. p018 had the loops the other way round, and that is exactly why it counted combinations.

## Hint 3

```
f = [0] * (target + 1); f[0] = 1      # one way to make 0: the empty sequence
for a in 1..target:                   # outer: amounts
    for x in nums:                    # inner: the last number
        if x <= a:
            f[a] += f[a - x]
return f[target]
```
