## Hint 1

Take the tree `[1, 2, 7, 3, 4]` and put two long arms below `2`, so that `2` is the middle of the longest path. The classmate measures `height(2's subtree) + height(7's subtree)`. Which node must be the middle (highest point) of the longest path? Is it the root?

## Hint 2

The longest path has a highest node, and that node can be **any** node. For a node, the best path through it has the length `height(left) + height(right)` (heights in nodes, the result in edges). So the answer is the **maximum** of that number over all nodes. A function that returns the height to its parent and, on the side, records `left + right` in a variable `best` does it in one pass.

## Hint 3

```
best = 0
def go(node):                          # returns the height of this subtree
    if node is None: return 0
    left = go(node.left)
    right = go(node.right)
    best = max(best, left + right)     # a path with `node` as its highest point
    return 1 + max(left, right)        # what the parent needs
go(root); return best
```
