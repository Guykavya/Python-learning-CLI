## Approach

Tree DP with three modes per node. `go(node)` returns `(open, watched, camera)`, each the fewest cameras in the subtree of `node`, with every node strictly below `node` watched, and `node` itself:

| mode | meaning | formula |
|---|---|---|
| `open` | not watched yet; the parent must hold a camera | `l1 + r1` |
| `watched` | watched by a child's camera, no camera on `node` | `min(l2 + min(r1, r2), r2 + min(l1, l2))` |
| `camera` | holds a camera | `1 + min(l0, l1, l2) + min(r0, r1, r2)` |

A missing child is `(0, 0, INF)`: it is "already fine" in the first two modes and cannot hold a camera. The root has no parent, so the answer is `min(watched, camera)` at the root.

```python
INF = float("inf")


def min_cameras(root):
    if root is None:
        return 0

    def go(node):
        if node is None:
            return 0, 0, INF                       # nothing to watch, no camera possible
        l0, l1, l2 = go(node.left)
        r0, r1, r2 = go(node.right)
        open_ = l1 + r1                            # children watched, but none has a camera
        watched = min(l2 + min(r1, r2), r2 + min(l1, l2))
        camera = 1 + min(l0, l1, l2) + min(r0, r1, r2)
        return open_, watched, camera

    _, watched, camera = go(root)
    return min(watched, camera)
```

A leaf gives `(0, INF, 1)`: it can be left open (0 cameras), it cannot be watched by a child, or it holds a camera. Its parent, if both children are such leaves, gets `open = INF`, `watched = INF`... no: `watched = min(1 + min(INF, 1), ...) = 2` and `camera = 1 + 0 + 0 = 1`. So one camera on the parent of two leaves: the expected answer.

## Complexity

`O(n)` time, `O(h)` recursion depth.

## Another way

A greedy, bottom-up, is also correct here: in post-order, put a camera on a node exactly when one of its children is not watched; a node with a camera child is watched; otherwise the node is left for its parent (and the root gets a camera if it is still unwatched). It works because a camera on the **parent** of a leaf watches everything a camera on the leaf would, and more (the exchange argument of dsa.13). The DP needs no such proof, which is why it is the safer first answer, and it extends to weighted versions (a different price per node) where the greedy breaks.
