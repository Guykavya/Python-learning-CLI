## Approach

A node with no children is a leaf and contributes 1. For any other node, the leaves lie in the left or in the right subtree, so the answer is the sum of the two recursive answers. The empty tree contributes 0. There are two base cases because the recursion would otherwise only ever reach `None`, which returns 0.

## Code

```python
def count_leaves(root):
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return count_leaves(root.left) + count_leaves(root.right)
```

## Complexity

`O(n)` time, `O(h)` stack.

## Another way

Count with a loop and a stack: pop a node; if both children are `None`, add 1; otherwise push the children that exist. Or use the formula for a **full** binary tree (every node has 0 or 2 children): leaves = internal nodes + 1, but that does not hold for a general tree such as `[1, 2]`.
