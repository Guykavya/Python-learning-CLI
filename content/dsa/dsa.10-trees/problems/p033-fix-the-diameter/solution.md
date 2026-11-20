## Approach

The starter measures one candidate: the path that passes through the root. The longest path has a highest node, and that node can be anywhere. So compute for every node `left_height + right_height` and keep the maximum. To avoid walking subtrees again and again, one recursive function returns the height to its parent and records the best path in a shared variable: "return for the parent, record for the answer".

## Code

```python
def diameter(root):
    best = 0

    def go(node):                                  # returns the height of the subtree (in nodes)
        nonlocal best
        if node is None:
            return 0
        left = go(node.left)
        right = go(node.right)
        best = max(best, left + right)             # a path with `node` as its highest point
        return 1 + max(left, right)                # what the parent needs

    go(root)
    return best
```

## Complexity

`O(n)` time, one visit per node. `O(h)` memory for the recursion.

## Another way

Keep the classmate's `height` and call `height(node.left) + height(node.right)` at every node, taking the maximum: it fixes the bug, but `height` walks the whole subtree each time, so a chain costs `O(n^2)`. Another correct method: run a breadth-first search from any node to find the farthest node `a`, then another from `a` to find the farthest node `b`: the distance `a`-`b` is the diameter (it needs the tree as an undirected graph).
