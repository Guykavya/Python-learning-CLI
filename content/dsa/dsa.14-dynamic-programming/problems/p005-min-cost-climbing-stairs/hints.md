## Hint 1

`f(i)` = the cheapest price to arrive at stair `i`. You arrived from `i - 1` (and paid `cost[i - 1]` to leave it) or from `i - 2` (and paid `cost[i - 2]`). Write `f(i)` as a `min` of two sums. Where is the top in this numbering?

## Hint 2

```
n = len(cost)
f = [0] * (n + 1)          # f[0] = f[1] = 0: start there for free
for i in 2..n:
    f[i] = min(f[i-1] + cost[i-1], f[i-2] + cost[i-2])
return f[n]
```
