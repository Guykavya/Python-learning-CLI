## Approach

Define `gain(node)` as the best sum of a path that starts at `node` and goes straight down. A branch with a negative gain is dropped (`max(0, ...)`). The best path whose highest node is `node` is `node.val + left_gain + right_gain`: record it in `best`. The value returned to the parent is only `node.val + max(left_gain, right_gain)`, because the parent can extend one branch, not a bend. Start `best` at minus infinity so that all-negative trees work.

## Code

```python
def max_path_sum(root):
    best = float("-inf")

    def gain(node):
        """Best sum of a path that starts at `node` and goes down (at least `node` itself)."""
        nonlocal best
        if node is None:
            return 0
        left = max(0, gain(node.left))              # a negative branch is dropped
        right = max(0, gain(node.right))
        best = max(best, node.val + left + right)   # a path that bends at this node
        return node.val + max(left, right)          # the parent can continue only ONE way down

    gain(root)
    return best
```

## Complexity

`O(n)` time: one visit per node. `O(h)` memory for the recursion.

## Another way

A brute force starts at every node and walks the undirected tree in all directions (`O(n^2)`), as in the chapter: it is the right way to test this function on random trees. The same "return one branch, record the bend" pattern gives the diameter (section 7) and the longest univalue path (next problem).
