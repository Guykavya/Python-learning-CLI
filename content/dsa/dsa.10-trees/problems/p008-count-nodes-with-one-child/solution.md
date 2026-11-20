## Approach

Look at each node once. It counts when exactly one of its two children is `None`. In Python `(root.left is None) != (root.right is None)` is exactly that "exclusive or". The answer for the tree is the node's own contribution (0 or 1) plus the answers of both subtrees; the empty tree contributes 0.

## Code

```python
def count_one_child(root):
    if root is None:
        return 0
    mine = 1 if (root.left is None) != (root.right is None) else 0
    return mine + count_one_child(root.left) + count_one_child(root.right)
```

## Complexity

`O(n)` time, `O(h)` stack.

## Another way

Count with any traversal: loop over all nodes with a stack and add 1 for each node that has exactly one child. A full binary tree (every node has 0 or 2 children) has answer 0; a chain of `n` nodes has `n - 1`.
