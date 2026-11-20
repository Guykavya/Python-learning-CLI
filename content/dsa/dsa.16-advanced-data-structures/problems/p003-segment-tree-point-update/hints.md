## Hint 1

Walk from the root towards the leaf of position `i`: at a node `[lo, hi)`, go left if `i < mid`, otherwise right. At the leaf, store `v`.

## Hint 2

On the way **back up**, recompute every node on the path from its two children: `t[node] = t[2 * node] + t[2 * node + 1]`. A parent computed before its child changed would keep the old sum.

## Hint 3

```
_update(node, lo, hi, i, v):
    if hi - lo == 1: t[node] = v; return
    mid = (lo + hi) // 2
    if i < mid: _update(2*node, lo, mid, i, v)
    else:       _update(2*node+1, mid, hi, i, v)
    t[node] = t[2*node] + t[2*node+1]
```
