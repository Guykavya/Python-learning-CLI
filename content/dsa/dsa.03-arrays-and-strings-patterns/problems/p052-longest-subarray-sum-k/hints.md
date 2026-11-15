## Hint 1

The sum of `a[j..i-1]` is `P[i] - P[j]`. You want it equal to `k`, so `P[j] = P[i] - k`. For a fixed `i`, which `j` gives
the **longest** subarray: the earliest or the latest index with that prefix value?

## Hint 2

Walk once from left to right with a running prefix `pre`. Before the loop, store `first[0] = 0` (the empty prefix). At
each `i`, first look up `pre - k`; then store `pre` **only if it is not already there**.

## Hint 3

```
first = {0: 0}; pre = 0; best = 0
for i in 1..n:
    pre += a[i-1]
    if pre - k in first: best = max(best, i - first[pre - k])
    if pre not in first: first[pre] = i
print best
```
