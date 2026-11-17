# Trace: draw a tree from a description

The chapter (section 2) describes a tree as a **level-order list** in which `None` means "no node here". The function `build_tree` reads the list two values at a time as the left and right child of the nodes in a queue. Predict **exactly** what this program prints. Do not run it.

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

def name(node):
    return "None" if node is None else str(node.val)

def describe(node):
    if node is None:
        return
    print(f"{node.val}: left={name(node.left)} right={name(node.right)}")
    describe(node.left)
    describe(node.right)

def size(node):
    if node is None:
        return 0
    return 1 + size(node.left) + size(node.right)

def height(node):
    if node is None:
        return 0
    return 1 + max(height(node.left), height(node.right))

def leaf_values(node):
    if node is None:
        return []
    if node.left is None and node.right is None:
        return [node.val]
    return leaf_values(node.left) + leaf_values(node.right)

root = build_tree([1, 2, 3, None, 4, 5, None, None, None, 6])
describe(root)
print("size", size(root))
print("height", height(root))
print("leaves", len(leaf_values(root)))
print("leaf values", leaf_values(root))
```

Write your answer in `answer.txt`, one printed line per line. The first six lines come from `describe` (one line per node, in the order of its recursive calls); then `size`, `height`, `leaves` and `leaf values` follow, as printed.

## How to work

Draw the tree first. Go through the list with a queue on paper: the root is the first value; then take the nodes in the order they were created, and give each node the next **two** values of the list as its left and right child (a `None` means no child, but it still uses up one place in the list). Only then walk the picture in the order of `describe` (a node, then its whole left subtree, then its whole right subtree).

## After you answer

1. Which node has the single value `6` as a child, and why does it sit under `5` and not under `4`?
2. The list has 10 entries but the tree has 6 nodes. Where do the other 4 entries go?
3. The height is counted in nodes. What would it be if you counted edges?
