## Approach

Same shape as `size`, but a node contributes its value instead of `1`. The empty tree contributes `0`, which is the neutral element of addition. Negative values need no special case.

## Code

```python
def tree_sum(root):
    if root is None:
        return 0
    return root.val + tree_sum(root.left) + tree_sum(root.right)
```

## Complexity

`O(n)` time, `O(h)` stack.

## Another way

Walk the tree with a stack and add `node.val` to a running total. Or collect all values with any traversal (chapter section 4) and call `sum(...)` on the list: shorter, but it needs `O(n)` extra memory.
