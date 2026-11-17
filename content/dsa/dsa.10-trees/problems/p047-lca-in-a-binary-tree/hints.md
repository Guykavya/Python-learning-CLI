## Hint 1

Define the call: `lca(node, p, q)` returns `p` or `q` if exactly one of them is in the subtree of `node` (the one that is there), `None` if none of them is, and the LCA if both are. What is the answer for `None`? For a node that **is** `p` or `q`? (You do not need to look below it: why?)

## Hint 2

Ask both children. If **both** answers are not `None`, then `p` is on one side and `q` on the other, so this node is the split point: return `node`. If only one child answers, pass that answer up unchanged. If neither does, return `None`.

## Hint 3

```
def lca(node, p, q):
    if node is None or node is p or node is q:
        return node
    left = lca(node.left, p, q)
    right = lca(node.right, p, q)
    if left is not None and right is not None:
        return node
    return left if left is not None else right
```
