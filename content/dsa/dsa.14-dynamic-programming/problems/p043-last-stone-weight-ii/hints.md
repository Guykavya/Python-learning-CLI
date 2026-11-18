## Hint 1

Follow one stone through the game. Every smash subtracts one weight from another, so the final stone is `(+ some stones) - (the other stones)`. Call the two groups `A` and `B`. The final weight is `sum(A) - sum(B)`, which is `>= 0`. The reverse is also true: for **any** split into two groups, there is a smashing order that ends with `|sum(A) - sum(B)|` (keep smashing one stone of the heavier side against one of the lighter side). So the question is: split the stones into two groups whose sums are **as close as possible**.

## Hint 2

If one group sums to `s`, the other sums to `total - s`, and the difference is `total - 2s`. To make it small, make `s` as large as possible **but not above `total // 2`**. Which sums `s` are reachable by a subset? That is the boolean subset-sum array of chapter section 12.

## Hint 3

```
total = sum(stones); half = total // 2
f = [False] * (half + 1); f[0] = True
for x in stones:
    for s from half down to x:
        if f[s - x]: f[s] = True
best = the largest s <= half with f[s]
return total - 2 * best
```
