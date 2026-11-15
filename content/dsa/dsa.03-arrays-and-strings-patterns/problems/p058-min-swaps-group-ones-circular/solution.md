## Approach

Choose where the final block of `m` ones will be. A block that already holds `w` ones holds `m - w` zeros; each swap can
fix at most one zero (it brings in one 1 from outside), and `m - w` swaps are always enough. So the answer is
`m - (most ones in a circular window of size m)`, a **fixed** sliding window on a circle.

Circular windows: there are exactly `n` windows of size `m`, starting at `0, 1, ..., n - 1`. Let the end index run from
`m - 1` to `n + m - 2` and take every index modulo `n`. No copy of the array is needed.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

m = sum(a)
if m == 0:
    print(0)
else:
    window = sum(a[:m])
    best = window
    for i in range(m, n + m - 1):
        window += a[i % n] - a[(i - m) % n]
        if window > best:
            best = window
    print(m - best)
```

Example `0 1 0 1 1 0 0`, `m = 3`: the window sums for starts 0 to 6 are `1 2 2 2 1 0 1` (the last one wraps: positions
6, 0, 1). The best is 2, so the answer is `3 - 2 = 1`.

## Complexity

O(n) time, O(1) extra memory.

## Another way

Write the array twice, `b = a + a`, and use prefix sums: the window starting at `s` has `P[s + m] - P[s]` ones. That is
easier to get right at first, at the cost of O(n) extra memory. Doubling the array is the standard trick for every
"circular" window or subarray question; the modulo index is the same trick without the copy.
