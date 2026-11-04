## Approach

Keep the sum of the current window. Each slide changes it by two numbers: the one that enters (`a[r]`) and the one
that leaves (`a[r - k]`). Track the largest value the sum takes.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]

s = sum(a[:k])
best = s
for r in range(k, n):
    s += a[r] - a[r - k]
    if s > best:
        best = s

print(best)
```

## Complexity

O(n) time: `k` additions for the first window, then two per slide. O(1) extra memory.

## Another way

With prefix sums `p`, the window ending at index `r` sums to `p[r + 1] - p[r + 1 - k]`. Take the maximum over all
`r`: also O(n), but with O(n) memory. Re-summing each window with `sum(a[i:i + k])` is O(n * k), which is
10^10 steps when `k = n / 2 = 100000`.
