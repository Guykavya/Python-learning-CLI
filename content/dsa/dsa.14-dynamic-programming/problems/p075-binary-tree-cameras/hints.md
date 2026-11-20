## Hint 1

Let `go(node)` return a triple `(open, watched, camera)`: the fewest cameras in the subtree in each of the three modes, with every node **below** `node` watched. Use `INF = float("inf")` for impossible modes. A missing child returns `(0, 0, INF)`: it needs nothing, and it cannot hold a camera. The answer is `min(watched, camera)` of the root: the root has no parent to watch it, so "open" is not allowed there.

## Hint 2

With the children's triples `(l0, l1, l2)` and `(r0, r1, r2)`:

- `camera = 1 + min(l0, l1, l2) + min(r0, r1, r2)`: the camera watches the children, so they may be in any mode, even open.
- `open = l1 + r1`: nobody watches the node, so the children have no camera, and they must already be watched (an open child would stay unwatched forever).
- `watched`: at least one child has a camera, and the other child is watched (with or without a camera).

## Hint 3

```
def go(node):
    if node is None: return (0, 0, INF)
    l0, l1, l2 = go(node.left); r0, r1, r2 = go(node.right)
    open    = l1 + r1
    watched = min(l2 + min(r1, r2), r2 + min(l1, l2))
    camera  = 1 + min(l0, l1, l2) + min(r0, r1, r2)
    return (open, watched, camera)
a, b, c = go(root); return min(b, c)       (0 for an empty tree)
```
