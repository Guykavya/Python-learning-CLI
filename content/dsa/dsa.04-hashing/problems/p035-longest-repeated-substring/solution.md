## Approach

`repeats(k)` is monotone (true up to some length, then false), so binary search finds the largest true `k`. The check for one
`k` rolls a hash over every window and stops when it meets a hash already in the set.

## Code

```python
B = 911382323
M = (1 << 61) - 1

s = input().strip()
n = len(s)
vals = [ord(c) - 96 for c in s]


def repeats(k):
    h = 0
    for i in range(k):
        h = (h * B + vals[i]) % M
    top = pow(B, k - 1, M)
    seen = {h}
    for i in range(k, n):
        h = ((h - vals[i - k] * top) * B + vals[i]) % M
        if h in seen:
            return True
        seen.add(h)
    return False


lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi + 1) // 2
    if repeats(mid):
        lo = mid
    else:
        hi = mid - 1
print(lo)
```

## Complexity

O(n log n) time: about 17 checks of O(n) each for `n = 10^5`. O(n) memory.

## Another way

A **suffix array** plus the LCP array finds the longest repeated substring exactly (the maximum LCP value) in O(n log n) without
any collision risk. Brute force over all pairs of starting positions is O(n^2) or worse.
