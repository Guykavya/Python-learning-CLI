## Hint 1

Recipe step 1: the memo becomes `t = [[0] * k for _ in range(n + 1)]`, so `t[i][run]` is `go(i, run)`. Step 2: the base case `go(0, run) = 1` becomes `t[0][run] = 1` for every `run`. Step 3: every `go(i - 1, x)` becomes `t[i - 1][x]`. Remember the trap `[[0] * k] * (n + 1)` (chapter section 4).

## Hint 2

Row `i` reads only row `i - 1`. So loop `i` upward from 1 to `n`; inside, `run` can go in any order (all reads are in the previous row). The answer is the cell the original call asked for: `go(n, 0)`.

## Hint 3

```
t = (n + 1) rows of k zeros
for run in 0..k-1: t[0][run] = 1
for i in 1..n:
    for run in 0..k-1:
        total = t[i-1][0]
        if run + 1 < k: total += t[i-1][run+1]
        t[i][run] = total
return t[n][0]
```
