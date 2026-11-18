## Hint 1

Change subset sum from "is `s` reachable?" to "**in how many ways** is `s` reachable?". `f[s]` = the number of subsets of the numbers processed so far with sum `s`. Before any number, only the empty subset exists: `f[0] = 1`, everything else 0.

## Hint 2

When the number `x` arrives, every old subset with sum `s - x` gives a new subset with sum `s` (add `x`). The old subsets with sum `s` stay. So `f[s] = f[s] + f[s - x]`, with the **old** `f[s - x]`: loop `s` downwards. Check `x = 0`: the loop includes `s = 0`, and `f[s] += f[s]` doubles every count. Is that right?

## Hint 3

```
f = [0] * (target + 1); f[0] = 1
for x in nums:
    for s from target down to x:
        f[s] += f[s - x]
return f[target]
```

If you write a recursion instead, be careful with the base case: reaching sum 0 is **not** the end when zeros may still follow.
