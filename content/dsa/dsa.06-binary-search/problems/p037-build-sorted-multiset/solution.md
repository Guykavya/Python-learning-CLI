## Approach

Keep the list sorted at all times. Every command needs only `lower` (first index `>= x`) or `upper` (first index `> x`): `add` inserts at `lower`, `remove` checks `s[lower]`, `count_le` is `upper`, `ceil` is `s[lower]`, `kth` is plain indexing.

## Code

```python
import sys

q = int(sys.stdin.readline())
s = []


def lower(x):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi) // 2
        if s[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper(x):
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi) // 2
        if s[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


out = []
for _ in range(q):
    op, v = sys.stdin.readline().split()
    v = int(v)
    if op == "add":
        s.insert(lower(v), v)
    elif op == "remove":
        i = lower(v)
        if i < len(s) and s[i] == v:
            del s[i]
            out.append("1")
        else:
            out.append("0")
    elif op == "count_le":
        out.append(str(upper(v)))
    elif op == "kth":
        out.append(str(s[v - 1]) if 1 <= v <= len(s) else "none")
    else:
        i = lower(v)
        out.append(str(s[i]) if i < len(s) else "none")
print("\n".join(out))
```

## Complexity

O(log n) per search; `insert` and `del` move up to n elements in one fast memory copy, so the total is fine for 10^5 commands (a balanced tree would make every command O(log n), see the further reading).

## Another way

A Fenwick tree or a balanced tree gives O(log n) for insert and delete too; for up to 10^5 operations the sorted list is simpler and fast enough because list shifting is done in C.
