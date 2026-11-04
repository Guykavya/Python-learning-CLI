## Approach

Binary search on the answer. The predicate "`r * r > n`" is False...False True...True over `r`. Find the first True with the half-open template; the answer is one less.

## Code

```python
q = int(input())
for _ in range(q):
    n = int(input())
    lo, hi = 0, n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid > n:
            hi = mid
        else:
            lo = mid + 1
    print(lo - 1)
```

## Complexity

O(q log n) time (about 60 steps per query for 10^18), O(1) space. Python integers are exact, so there is no overflow.

## Another way

Newton iteration: `r = n; while r * r > n: r = (r + n // r) // 2` converges in about log log n steps, but it is harder to prove correct. Binary search is easy to get right.
