## Approach

At each depth you see the rightmost node of that depth, which is the **last** node when the level is read from left to right. So run a level-order walk and keep the last node of every level. A depth with no right child still shows the node that is rightmost among the others, and this comes out of the level order without any special case.

## Code

```python
from collections import deque


def right_side_view(root):
    if root is None:
        return []
    view, queue = [], deque([root])
    while queue:
        size = len(queue)
        for i in range(size):
            node = queue.popleft()
            if i == size - 1:                   # the last node of the level is the one you see
                view.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
    return view
```

## Complexity

`O(n)` time, `O(w)` memory for the queue.

## Another way

A depth-first version visits the **right** child first and records the first node it meets at each new depth (`if depth == len(view): view.append(node.val)`). It uses `O(h)` memory, and it is a nice example of top-down information (the depth). A third way: take `level_order(root)` and return `[level[-1] for level in levels]` (the chapter's one-liner).
