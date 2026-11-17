## Approach

At a node whose value is below `lo`, the whole left subtree is smaller still, so only the right subtree can contribute; at a value above `hi` only the left subtree can. A node inside the range counts its own value and needs both subtrees. This is the pruning of the backtracking module on a tree: the BST order tells you which branches cannot hold an answer.

## Code

```python
def range_sum(root, lo, hi):
    if root is None:
        return 0
    if root.val < lo:
        return range_sum(root.right, lo, hi)       # everything on the left is too small
    if root.val > hi:
        return range_sum(root.left, lo, hi)        # everything on the right is too big
    return root.val + range_sum(root.left, lo, hi) + range_sum(root.right, lo, hi)
```

## Complexity

`O(h + m)` time: one path from the root into the range, plus the `m` nodes inside the range (and a short path out on each side). `O(h)` memory for the recursion. A balanced tree and a short range read only a few dozen pointers; a visit-everything function always reads `O(n)`.

## Another way

An inorder walk that stops after `hi` and starts counting at `lo` is also `O(h + m)`: use the iterative inorder with a stack, skip the nodes below `lo`, and break when a value is above `hi`. The BST iterator of problem 45 gives the same walk one value at a time.
