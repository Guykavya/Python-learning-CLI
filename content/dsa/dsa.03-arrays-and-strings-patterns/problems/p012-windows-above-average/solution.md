## Approach

A fixed-size sliding window with a running sum. Every window is checked once, including the first one, and the
average test is turned into an integer test by multiplying both sides by `k`.

## Code

```python
n, k, t = map(int, input().split())
a = [int(x) for x in input().split()]

need = t * k
s = sum(a[:k])
count = 1 if s >= need else 0
for r in range(k, n):
    s += a[r] - a[r - k]
    if s >= need:
        count += 1

print(count)
```

## Complexity

O(n) time, O(1) extra memory. There are `n - k + 1` windows.

## Another way

With prefix sums, window `i` (starting at index `i`) sums to `p[i + k] - p[i]`; count how many of those reach
`need`. A trick worth knowing: subtract `t` from every reading first. Then a window qualifies when its new sum is
`>= 0`. That form is handy when the threshold is an average and the windows have different lengths.

`s // k >= t` also happens to be correct, because `t` is an integer: the floor of the average reaches `t` exactly
when the average does. It stops being correct as soon as `t` is a fraction such as 3.5, while `s >= t * k` (with
`2 * s >= 7 * k` for 3.5) keeps working, so prefer the multiplication.
