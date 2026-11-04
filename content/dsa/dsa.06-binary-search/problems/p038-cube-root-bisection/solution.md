## Approach

`f` is increasing, so the predicate `f(mid) >= c` is False...False True...True on the real line. Halve the interval 100 times; the width becomes `10^5 / 2^100`, far smaller than the float precision.

## Code

```python
t = int(input())
for _ in range(t):
    c = int(input())
    lo, hi = 0.0, 100000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if mid * mid * mid + mid >= c:
            hi = mid
        else:
            lo = mid
    print(f"{(lo + hi) / 2:.6f}")
```

## Complexity

O(t * 100) time, O(1) space.

## Another way

Newton iteration `x = x - (x^3 + x - c) / (3x^2 + 1)` converges much faster, but needs a good start value and is harder to prove. Bisection always works for a monotone function.
