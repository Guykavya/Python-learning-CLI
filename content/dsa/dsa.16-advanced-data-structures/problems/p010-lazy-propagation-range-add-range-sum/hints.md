## Hint 1

Cover `[l, r)` with whole nodes, exactly like a query. For a covered node `[lo, hi)`: its sum grows by `v * (hi - lo)`, and the children still owe `+v`: store it in a tag `lz[node] += v` and stop.

## Hint 2

Before you look into the children of a node (in `add` **and** in `query`, on partial overlap), **push** its tag: apply `lz[node]` to both children (sum += tag * length, tag += tag), then set `lz[node] = 0`. After the recursive `add` returns, recompute the node's sum from its children.

## Hint 3

```
_apply(node, lo, hi, v): s[node] += v * (hi - lo); lz[node] += v
_push(node, lo, hi): if lz[node]: apply to both children; lz[node] = 0
_add(node, lo, hi, l, r, v):
    if no overlap: return
    if inside: _apply(node, lo, hi, v); return
    _push(node, lo, hi); recurse left and right; s[node] = s[2node] + s[2node+1]
_query: same three cases, with _push before descending
```
