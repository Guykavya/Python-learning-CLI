## Approach

`down(node)` is the length in edges of the longest same-value path that starts at `node` and goes straight down. A branch continues into a child only when the child's value equals this node's value; then its length is `down(child) + 1`, otherwise it is `0`. The longest path that bends at this node is `left_len + right_len`: record it. Return `max(left_len, right_len)` to the parent, because a parent can extend only one of them.

## Code

```python
def longest_univalue_path(root):
    best = 0

    def down(node):
        """Edges of the longest same-value path that starts at `node` and goes down."""
        nonlocal best
        if node is None:
            return 0
        left, right = down(node.left), down(node.right)
        left_len = left + 1 if node.left is not None and node.left.val == node.val else 0
        right_len = right + 1 if node.right is not None and node.right.val == node.val else 0
        best = max(best, left_len + right_len)       # a path that bends at this node
        return max(left_len, right_len)              # the parent can continue only one way

    down(root)
    return best
```

## Complexity

`O(n)` time, `O(h)` memory for the recursion.

## Another way

Look at the tree as a **forest**: keep only the edges that join two nodes with equal values. The answer is the largest diameter of one component of that forest. That is also how the tests check the function (a breadth-first search from every node over the equal-value edges). The recursive version above is the "return one branch, record the bend" pattern of the diameter.
