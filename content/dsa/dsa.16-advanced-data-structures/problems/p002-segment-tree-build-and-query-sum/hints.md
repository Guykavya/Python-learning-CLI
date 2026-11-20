## Hint 1

`_build(node, lo, hi)`: if the range has one element (`hi - lo == 1`), store it in `t[node]`. Otherwise build both halves, then `t[node] = t[2 * node] + t[2 * node + 1]`.

## Hint 2

`_query(node, lo, hi, l, r)` has three cases: **no overlap** (`r <= lo or hi <= l`): return 0; **inside** (`l <= lo and hi <= r`): return `t[node]` without going deeper; **partial**: ask both children and add.

## Hint 3

```
query(l, r) = _query(1, 0, n, l, r)
_query(node, lo, hi, l, r):
    if r <= lo or hi <= l: return 0
    if l <= lo and hi <= r: return t[node]
    mid = (lo + hi) // 2
    return _query(2*node, lo, mid, l, r) + _query(2*node+1, mid, hi, l, r)
```
