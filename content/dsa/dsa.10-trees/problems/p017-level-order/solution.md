## Approach

A queue holds the nodes found but not yet handled. At the start of each round it holds exactly the nodes of one level, so `len(queue)` (read once, before the loop) says how many to take. Take them from the front, record their values, and append their children at the back: those become the next level. The round ends when the level is finished, and the loop ends when no children were added.

## Code

```python
from collections import deque


def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):             # exactly the nodes of this level
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        levels.append(level)
    return levels
```

## Complexity

`O(n)` time, each node is appended and popped once. `O(w)` memory for the queue, where `w` is the widest level (up to about `n / 2` for a perfect tree), plus the output.

## Another way

A depth-first version (chapter section 6) passes the depth down and appends to `levels[depth]`, creating a new inner list when `depth == len(levels)`. Because the left child is visited first, each level fills from left to right. It uses `O(h)` memory instead of `O(w)`, but recursion fails on a very deep tree.
