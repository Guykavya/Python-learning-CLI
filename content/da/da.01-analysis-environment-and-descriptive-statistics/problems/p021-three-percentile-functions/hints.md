## Hint 1

All three start the same way. What is the common first step, and what differs: the *position* formula, the base (0 or 1), and whether you interpolate? Use `p * n / 100`, not `p / 100 * n`: why can the second give a different `ceil`?

## Hint 2

```text
ordered = sorted(values)
nearest: rank = max(1, ceil(p * n / 100)); return ordered[rank - 1]
inclusive: pos = (n-1)*p/100; lo = floor(pos); hi = min(lo+1, n-1); lerp(ordered[lo], ordered[hi], pos-lo)
exclusive: pos = (n+1)*p/100; check 1 <= pos <= n; lo = floor(pos); hi = min(lo+1, n); lerp(ordered[lo-1], ordered[hi-1], pos-lo)
```
