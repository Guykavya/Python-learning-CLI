## Approach

Walk down and carry the part of the target that is still missing. At each node take the node's value off the target. A path may end only at a leaf, so the comparison happens there: `leaf.val == remaining target`. For an inner node, the answer is true if the left or the right subtree can finish the path. An empty tree has no path, so `None` returns `False` (not `target == 0`).

## Code

```python
def has_path_sum(root, target):
    if root is None:
        return False
    if root.left is None and root.right is None:      # a leaf: the path must end here
        return root.val == target
    rest = target - root.val
    return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)
```

## Complexity

`O(n)` time in the worst case (the `or` stops at the first success), `O(h)` stack.

## Another way

Pass the running sum **up to** the node (`running + node.val`) and compare it with the fixed `target` at the leaf; it is the same idea with addition instead of subtraction. An explicit stack of `(node, sum_so_far)` pairs does it without recursion. To collect the paths instead of a yes/no, see the next problem.
