# Trace: the queue in a level-order walk

This is the level-order walk of the chapter (section 6), with prints. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

root = build_tree([8, 3, 10, 1, 6, None, 14])
levels = []
queue = deque([root])
level_no = 0
while queue:
    level_no += 1
    print(f"level {level_no}: size {len(queue)}")
    level = []
    for _ in range(len(queue)):
        node = queue.popleft()
        level.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
        print(f"pop {node.val}: queue={[n.val for n in queue]}")
    levels.append(level)
print(levels)
```

Write your answer in `answer.txt`, one printed line per line. A `level` line shows how many nodes the queue holds when the level starts. A `pop` line shows the queue **after** the popped node's children were appended (front of the queue first). The last line is the list of levels.

## How to work

Draw the tree from `[8, 3, 10, 1, 6, None, 14]` first (a queue again: `8` gets `3` and `10`; `3` gets `1` and `6`; `10` gets no left child and the right child `14`). Then keep the queue on paper as a row of values. For every pop write the popped node, cross it out at the front, and add its children at the back, left child first. The number printed after `size` is `len(queue)` **before** the inner loop starts, so it does not change while the level is processed.

## After you answer

1. Why is `size` read before the inner loop, and what would go wrong if the loop used `while queue` instead of `range(len(queue))`?
2. At the moment a level starts, what exactly is in the queue?
3. How large does the queue get, and which level causes it?
