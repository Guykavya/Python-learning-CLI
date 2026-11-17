## Approach

Do an ordinary level order, which always finds each level from left to right, and write each finished level in the right direction: reverse the levels with an odd index. Changing the order in which children enter the queue would break the left-to-right order of the **next** level, so it is easier and safer to reverse only the finished list.

## Code

```python
from collections import deque


def zigzag(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        if len(levels) % 2 == 1:                # levels 1, 3, 5, ... go right to left
            level.reverse()
        levels.append(level)
    return levels
```

## Complexity

`O(n)` time (reversing a level costs its size, so the total is still `O(n)`), `O(w)` queue memory plus the output.

## Another way

The one-liner of the chapter (section 6): `[lv if i % 2 == 0 else lv[::-1] for i, lv in enumerate(level_order(root))]`. Or use two stacks: one holds the current level, the other the next; pushing the children left-then-right into one stack and right-then-left into the other makes each stack pop in the alternating order.
