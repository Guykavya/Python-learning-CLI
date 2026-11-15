## Approach

Store the distinct values in a set. A value `x` with `x - 1` in the set is in the **middle** of some run, so skip it.
A value with no `x - 1` is the **start** of a run; walk up `x + 1, x + 2, ...` while they are in the set. Every value is
visited by at most one inner walk, so the total is linear.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

values = set(a)
best = 0
for x in values:
    if x - 1 not in values:
        length = 1
        while x + length in values:
            length += 1
        best = max(best, length)
print(best)
```

## Complexity

O(n) on average. The inner `while` runs only for run starts, and each run is walked once, so the total number of steps over
all starts is at most the number of distinct values.

## Another way

Sort the distinct values and scan: a run continues while `b[i] == b[i-1] + 1`. That is O(n log n) and needs no set,
and is perfectly fine for these limits.
