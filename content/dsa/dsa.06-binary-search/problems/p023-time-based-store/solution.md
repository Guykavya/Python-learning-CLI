## Approach

Keep two parallel lists per key. Because the times arrive in increasing order, the lists stay sorted. A `get` is an upper bound search: the answer is the entry just before the first time that is larger than `t`.

## Code

```python
import sys

q = int(sys.stdin.readline())
times = {}
vals = {}
out = []
for _ in range(q):
    parts = sys.stdin.readline().split()
    if parts[0] == "set":
        key, value, t = parts[1], parts[2], int(parts[3])
        times.setdefault(key, []).append(t)
        vals.setdefault(key, []).append(value)
    else:
        key, t = parts[1], int(parts[2])
        ts = times.get(key, [])
        lo, hi = 0, len(ts)
        while lo < hi:
            mid = (lo + hi) // 2
            if ts[mid] <= t:
                lo = mid + 1
            else:
                hi = mid
        out.append(vals[key][lo - 1] if lo > 0 else "NONE")
print("\n".join(out))
```

## Complexity

O(log k) per `get` (k = sets of that key), O(1) per `set`; O(q) memory.

## Another way

Store `(time, value)` tuples in one list per key and search with a key function (`bisect_right(lst, t, key=lambda p: p[0])`), or use `bisect_right(lst, (t, chr(0x10FFFF)))`. The two parallel lists avoid both tricks.
