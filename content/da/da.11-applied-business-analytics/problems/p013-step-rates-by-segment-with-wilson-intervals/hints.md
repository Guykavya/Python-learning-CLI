## Hint 1

Loop over the segments (`groupby(by)`), and inside over the steps while keeping the previous count. What must you do when the previous count is 0, before calling the Wilson function?

## Hint 2

```text
for key, g in df.groupby(by):
    prev = len(g)
    for s in steps:
        k = int(g[s].sum())
        if prev == 0: nan row
        else: ci = binomtest(k, prev).proportion_ci(0.95, method="wilson"); row = (k/prev*100, ci.low*100, ci.high*100)
        prev = k
```
