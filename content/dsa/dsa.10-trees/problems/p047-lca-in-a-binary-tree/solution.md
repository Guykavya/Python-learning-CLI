## Approach

The call `lca(node, p, q)` returns `p` or `q` if exactly one of them is in the subtree (the one that is there), `None` if neither is, and the LCA if both are. For `None` the answer is `None`. When `node` is `p` or `q`, return it at once: if the other one is below, this node is the LCA; if not, the answer is passed up anyway. Otherwise ask both children: two answers mean the nodes are on different sides, so this node is the LCA; one answer is passed up unchanged.

## Code

```python
def lca(root, p, q):
    if root is None or root is p or root is q:
        return root
    left = lca(root.left, p, q)
    right = lca(root.right, p, q)
    if left is not None and right is not None:
        return root                          # p and q are on different sides: the split point
    return left if left is not None else right
```

## Complexity

`O(n)` time (every node may be visited once) and `O(h)` memory for the recursion.

## Another way

Build a parent map (a dictionary `node -> parent`), collect all ancestors of `p` (including `p`) in a set, and walk up from `q` until you meet one: `O(n)` time and memory, and no recursion. The tests use this as the brute force. If the nodes have `parent` links, it is the intersection of two linked lists (dsa.09).
