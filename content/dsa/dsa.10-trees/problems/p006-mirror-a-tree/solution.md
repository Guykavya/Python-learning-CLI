## Approach

The mirror of a tree is: swap the two children, and mirror each of them. Trust the recursion for the two subtrees: `invert(root.right)` is the mirror of the right subtree, and it becomes the new left child. The tuple assignment evaluates both calls before it assigns, so nothing is overwritten too early. The function returns the root so the caller (and the parent call) can use the result.

## Code

```python
def invert(root):
    if root is None:
        return None
    root.left, root.right = invert(root.right), invert(root.left)
    return root
```

## Complexity

`O(n)` time (each node is visited once), `O(h)` stack, and no new nodes.

## Another way

Iterative: walk the tree with a stack or a queue; at each popped node swap its two children with `node.left, node.right = node.right, node.left` and push both children. The order of the walk does not matter, because the swap at one node does not depend on the others. That version also works on a chain of 5,000 nodes.
